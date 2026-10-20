"""
Model inference service for RoadCast.
Loads the serialized HistGradientBoosting model, generates labeled historical estimates,
compares against historical baseline, and includes honest limitations.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

from app.domain.models import PredictionRequest, PredictionResponse

MODEL_ARTIFACT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "models", "traffic_model.joblib")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "model", "evaluation_report.json")
PROCESSED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "metro_traffic_processed.csv")


class ModelService:
    _instance = None

    def __init__(self):
        self.model = None
        self.eval_report = {}
        self.baseline_lookup = {}
        self.overall_mean = 3250.0

        if os.path.exists(REPORT_PATH):
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                self.eval_report = json.load(f)

        if os.path.exists(MODEL_ARTIFACT_PATH):
            print(f"Loading trained model artifact from {MODEL_ARTIFACT_PATH}...")
            self.model = joblib.load(MODEL_ARTIFACT_PATH)

        if os.path.exists(PROCESSED_PATH):
            df = pd.read_csv(PROCESSED_PATH)
            self.overall_mean = float(df["traffic_volume"].mean())
            self.baseline_lookup = df.groupby(["day_of_week", "hour"])["traffic_volume"].mean().to_dict()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(self, req: PredictionRequest) -> PredictionResponse:
        """
        Executes prediction and returns labeled estimate with baseline comparison.
        """
        day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }

        dow = day_map.get(req.day_name, 1)
        month = month_map.get(req.month_name, 10)
        is_weekend = 1 if dow >= 5 else 0
        is_holiday = 1 if req.is_holiday else 0

        # Baseline prediction
        baseline_val = float(self.baseline_lookup.get((dow, req.hour), self.overall_mean))

        # Model prediction
        if self.model is not None:
            features_df = pd.DataFrame([{
                "weather_main": req.weather_main,
                "day_name": req.day_name,
                "month_name": req.month_name,
                "hour": req.hour,
                "day_of_week": dow,
                "month": month,
                "temp_celsius": req.temp_celsius,
                "rain_1h": req.rain_1h,
                "snow_1h": req.snow_1h,
                "clouds_all": req.clouds_all,
                "is_weekend": is_weekend,
                "is_holiday": is_holiday
            }])
            raw_pred = float(self.model.predict(features_df)[0])
            pred_val = float(np.clip(raw_pred, 0, 8000))
        else:
            pred_val = baseline_val

        diff = round(pred_val - baseline_val, 1)
        pct_diff = round((diff / baseline_val) * 100, 2) if baseline_val > 0 else 0.0

        # Approximate 90% confidence interval based on test RMSE (461 veh/h)
        rmse = float(self.eval_report.get("candidate_ml_evaluation", {}).get("rmse", 460.0))
        ci_lower = max(0.0, round(pred_val - 1.645 * rmse, 1))
        ci_upper = min(8000.0, round(pred_val + 1.645 * rmse, 1))

        if pred_val < 1500:
            cat = "Low"
        elif pred_val < 3500:
            cat = "Moderate"
        elif pred_val < 5000:
            cat = "Heavy"
        else:
            cat = "Severe"

        return PredictionResponse(
            predicted_volume=round(pred_val, 1),
            baseline_volume=round(baseline_val, 1),
            difference_from_baseline=diff,
            pct_difference=pct_diff,
            congestion_category=cat,
            confidence_interval={"lower_90_pct": ci_lower, "upper_90_pct": ci_upper},
            model_name="RoadCast HistGradientBoosting Regressor",
            model_version="1.0.0",
            unit="vehicles per hour",
            historical_estimate_notice="ESTIMATE ONLY: This prediction is a statistical estimate trained on historical I-94 observations. It must not be interpreted as live traffic conditions or guaranteed travel time.",
            limitations=[
                "Applies exclusively to westbound I-94 at ATR Station 301 near Minneapolis-St. Paul.",
                "Does not reflect unpredictable incidents, crashes, active road construction, or extreme blizzards.",
                "Based on 2012-2018 historical baseline observations."
            ]
        )
