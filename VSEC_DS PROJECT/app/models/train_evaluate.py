"""
Model training, baseline comparison, and evaluation module for RoadCast.
Implements:
1. Chronological train/test split (no future data leakage).
2. Historical Hour x Day-of-Week mean baseline.
3. Supervised ML regression model (GradientBoostingRegressor / Ridge).
4. Rigorous evaluation metrics (MAE, RMSE, R²).
5. Serialization of trained model artifact and evaluation report.
"""

import os
import json
import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

PROCESSED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "metro_traffic_processed.csv")
MODEL_ARTIFACT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "models", "traffic_model.joblib")
MODEL_REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "model", "evaluation_report.json")


def train_and_evaluate(data_path: str = PROCESSED_DATA_PATH) -> dict:
    """
    Trains baseline and ML candidate model on historical data using chronological split.
    Saves serialized artifact and evaluation report.
    """
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values("date_time").reset_index(drop=True)

    # Chronological Split: 80% Train, 20% Test
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    split_date = train_df["date_time"].max()
    print(f"Chronological split date: {split_date}")
    print(f"Train size: {len(train_df)} ({train_df['date_time'].min()} to {split_date})")
    print(f"Test size: {len(test_df)} ({test_df['date_time'].min()} to {test_df['date_time'].max()})")

    # Target
    y_train = train_df["traffic_volume"].values
    y_test = test_df["traffic_volume"].values

    # 1. BASELINE MODEL: Historical Hour x Day-of-Week mean computed strictly on train set
    baseline_lookup = train_df.groupby(["day_of_week", "hour"])["traffic_volume"].mean().to_dict()
    train_mean = float(y_train.mean())

    def predict_baseline(row):
        return baseline_lookup.get((row["day_of_week"], row["hour"]), train_mean)

    y_test_baseline = test_df.apply(predict_baseline, axis=1).values

    baseline_mae = float(mean_absolute_error(y_test, y_test_baseline))
    baseline_rmse = float(root_mean_squared_error(y_test, y_test_baseline))
    baseline_r2 = float(r2_score(y_test, y_test_baseline))

    print(f"Baseline (Hour x Day Mean) -> MAE: {baseline_mae:.2f}, RMSE: {baseline_rmse:.2f}, R2: {baseline_r2:.4f}")

    # 2. CANDIDATE ML MODEL: HistGradientBoosting with OneHot features
    categorical_cols = ["weather_main", "day_name", "month_name"]
    numeric_cols = ["hour", "day_of_week", "month", "temp_celsius", "rain_1h", "snow_1h", "clouds_all", "is_weekend", "is_holiday"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
            ("num", "passthrough", numeric_cols)
        ]
    )

    ml_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_depth=8,
            random_state=42
        ))
    ])

    X_train = train_df[categorical_cols + numeric_cols]
    X_test = test_df[categorical_cols + numeric_cols]

    print("Fitting Gradient Boosting regressor...")
    ml_pipeline.fit(X_train, y_train)

    y_test_pred = ml_pipeline.predict(X_test)
    # Clip negative predictions as traffic volume cannot be negative
    y_test_pred = np.clip(y_test_pred, 0, 8000)

    ml_mae = float(mean_absolute_error(y_test, y_test_pred))
    ml_rmse = float(root_mean_squared_error(y_test, y_test_pred))
    ml_r2 = float(r2_score(y_test, y_test_pred))

    print(f"Candidate ML Model -> MAE: {ml_mae:.2f}, RMSE: {ml_rmse:.2f}, R2: {ml_r2:.4f}")

    mae_improvement_pct = round(((baseline_mae - ml_mae) / baseline_mae) * 100, 2)
    rmse_improvement_pct = round(((baseline_rmse - ml_rmse) / baseline_rmse) * 100, 2)
    print(f"Improvement over baseline: MAE reduced by {mae_improvement_pct}%, RMSE reduced by {rmse_improvement_pct}%")

    # 3. CLASSIFICATION EVALUATION (Capacity Tiers: Low, Moderate, Heavy, Severe)
    def to_congestion_tier(vol):
        if vol < 1500:
            return "Low"
        elif vol < 3500:
            return "Moderate"
        elif vol < 5000:
            return "Heavy"
        else:
            return "Severe"

    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    tier_labels = ["Low", "Moderate", "Heavy", "Severe"]
    y_test_tiers = [to_congestion_tier(v) for v in y_test]
    y_pred_tiers = [to_congestion_tier(v) for v in y_test_pred]

    cls_accuracy = float(accuracy_score(y_test_tiers, y_pred_tiers))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test_tiers, y_pred_tiers, labels=tier_labels, average="macro", zero_division=0)
    cm = confusion_matrix(y_test_tiers, y_pred_tiers, labels=tier_labels)
    print(f"Classification Metrics -> Accuracy: {cls_accuracy:.4f}, Macro F1: {f1:.4f}, Macro Precision: {prec:.4f}, Macro Recall: {rec:.4f}")

    # Generate Confusion Matrix Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(7, 5.5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=tier_labels, yticklabels=tier_labels, ax=ax, cbar=False)
        ax.set_title(f"Confusion Matrix: Congestion Tier Classification (Accuracy: {cls_accuracy*100:.1f}%)", fontsize=11, fontweight="bold", pad=12)
        ax.set_xlabel("Predicted Capacity Tier", fontsize=10)
        ax.set_ylabel("True Capacity Tier", fontsize=10)

        fig_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "..", "reports", "figures"),
            os.path.join(os.path.dirname(__file__), "..", "static", "figures")
        ]
        for fd in fig_dirs:
            os.makedirs(fd, exist_ok=True)
            fig.savefig(os.path.join(fd, "7_confusion_matrix_model.png"), dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("[ML] Generated confusion matrix figure: 7_confusion_matrix_model.png")
    except Exception as e:
        print(f"[ML] Note on plot: {e}")

    # Serialize model artifact
    os.makedirs(os.path.dirname(MODEL_ARTIFACT_PATH), exist_ok=True)
    joblib.dump(ml_pipeline, MODEL_ARTIFACT_PATH)

    # Save evaluation report
    report = {
        "model_name": "RoadCast Interstate Volume Estimator",
        "model_version": "1.0.0",
        "model_type": "HistGradientBoostingRegressor with OneHot Encoding",
        "training_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_variable": {
            "name": "traffic_volume",
            "unit": "vehicles per hour (veh/h)",
            "definition": "Westbound hourly vehicle counts on I-94 at ATR Station 301"
        },
        "split_strategy": {
            "type": "Chronological (Time-ordered)",
            "leakage_prevention": "Test set observations are chronologically subsequent to all training records; no future timestamps or target leakages were present during fitting.",
            "train_period": f"{train_df['date_time'].min()} to {split_date}",
            "test_period": f"{test_df['date_time'].min()} to {test_df['date_time'].max()}",
            "train_observations": len(train_df),
            "test_observations": len(test_df)
        },
        "input_features": {
            "categorical": categorical_cols,
            "numeric": numeric_cols
        },
        "baseline_evaluation": {
            "model": "Historical Hour-of-Day x Day-of-Week Mean",
            "mae": round(baseline_mae, 2),
            "rmse": round(baseline_rmse, 2),
            "r2_score": round(baseline_r2, 4)
        },
        "candidate_ml_evaluation": {
            "model": "HistGradientBoostingRegressor",
            "mae": round(ml_mae, 2),
            "rmse": round(ml_rmse, 2),
            "r2_score": round(ml_r2, 4)
        },
        "classification_evaluation": {
            "task": "4-Tier Congestion Classification (Low, Moderate, Heavy, Severe)",
            "accuracy": round(cls_accuracy, 4),
            "macro_precision": round(float(prec), 4),
            "macro_recall": round(float(rec), 4),
            "macro_f1_score": round(float(f1), 4),
            "confusion_matrix": cm.tolist(),
            "tier_labels": tier_labels
        },
        "performance_gain": {
            "mae_reduction_pct": mae_improvement_pct,
            "rmse_reduction_pct": rmse_improvement_pct,
            "r2_difference": round(ml_r2 - baseline_r2, 4)
        },
        "limitations_and_caveats": [
            "Estimates apply specifically to westbound I-94 near Minneapolis-St. Paul (Station 301).",
            "Not applicable to arbitrary city streets or other geographic regions without local training data.",
            "Predictions are statistical approximations based on historical data (2012-2018) and must not be used as live turn-by-turn guidance or guaranteed travel times.",
            "Extreme unobserved events (e.g., blizzards exceeding 30 inches or total road closures) may diverge from historical estimates."
        ]
    }

    os.makedirs(os.path.dirname(MODEL_REPORT_PATH), exist_ok=True)
    with open(MODEL_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Evaluation report saved to: {MODEL_REPORT_PATH}")
    return report



if __name__ == "__main__":
    train_and_evaluate()
