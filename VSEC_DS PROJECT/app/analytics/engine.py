"""
Analytics query and aggregation engine for RoadCast.
Provides thread-safe, high-performance in-memory filtering and aggregations
over the prepared historical traffic dataset.
Guarantees consistent filtering across metrics, charts, and findings.
"""

import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from app.domain.models import (
    FilterSpec, SummaryMetrics, HourlyTrendPoint,
    TimelinePoint, HeatmapCell, WeatherImpactPoint,
    CongestionDistributionPoint
)

PROCESSED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "metro_traffic_processed.csv")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "metadata", "dataset_manifest.json")


class AnalyticsEngine:
    _instance = None

    def __init__(self, data_path: str = PROCESSED_DATA_PATH):
        print(f"Initializing AnalyticsEngine with data: {data_path}...")
        self.df = pd.read_csv(data_path)
        self.df["date_time"] = pd.to_datetime(self.df["date_time"])
        self.df["date_str"] = self.df["date_time"].dt.strftime("%Y-%m-%d")
        self.total_clean_records = len(self.df)

        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.manifest["observation_count_clean"] = self.total_clean_records

        # Precompute overall averages for comparison
        self.overall_avg_volume = float(self.df["traffic_volume"].mean())

        # Baseline lookup dictionary for predictions
        self.baseline_lookup = self.df.groupby(["day_of_week", "hour"])["traffic_volume"].mean().to_dict()

        print(f"AnalyticsEngine loaded {self.total_clean_records} historical records (Date span: {self.df['date_time'].min()} to {self.df['date_time'].max()}).")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def apply_filters(self, spec: Optional[FilterSpec]) -> pd.DataFrame:
        """Applies FilterSpec criteria and returns filtered DataFrame."""
        if spec is None:
            return self.df

        sub = self.df

        if spec.start_date:
            sub = sub[sub["date_time"] >= pd.to_datetime(spec.start_date)]
        if spec.end_date:
            # End of day boundary
            sub = sub[sub["date_time"] <= pd.to_datetime(spec.end_date) + pd.Timedelta(days=1, microseconds=-1)]
        if spec.hours:
            sub = sub[sub["hour"].isin(spec.hours)]
        if spec.days_of_week:
            sub = sub[sub["day_of_week"].isin(spec.days_of_week)]
        if spec.weather_main:
            sub = sub[sub["weather_main"].isin(spec.weather_main)]
        if spec.is_holiday is not None:
            sub = sub[sub["is_holiday"] == (1 if spec.is_holiday else 0)]
        if spec.is_weekend is not None:
            sub = sub[sub["is_weekend"] == (1 if spec.is_weekend else 0)]
        if spec.congestion_category:
            sub = sub[sub["congestion_category"].isin(spec.congestion_category)]

        return sub

    def get_summary(self, spec: Optional[FilterSpec] = None) -> SummaryMetrics:
        """Computes summary statistics for dashboard metric cards."""
        filtered_df = self.apply_filters(spec)

        if len(filtered_df) == 0:
            return SummaryMetrics(
                average_volume=0.0,
                median_volume=0.0,
                peak_hour=0,
                peak_volume=0,
                total_observations=0,
                total_days=0,
                congestion_distribution={"Low": 0, "Moderate": 0, "Heavy": 0, "Severe": 0}
            )

        avg_vol = round(float(filtered_df["traffic_volume"].mean()), 2)
        med_vol = float(filtered_df["traffic_volume"].median())
        peak_rec = int(filtered_df["traffic_volume"].max())

        # Peak average hour
        hourly_means = filtered_df.groupby("hour")["traffic_volume"].mean()
        peak_hr = int(hourly_means.idxmax()) if len(hourly_means) > 0 else 0

        total_obs = int(len(filtered_df))
        total_days = int(filtered_df["date_str"].nunique())

        cong_counts = filtered_df["congestion_category"].value_counts().to_dict()
        cong_dist = {cat: int(cong_counts.get(cat, 0)) for cat in ["Low", "Moderate", "Heavy", "Severe"]}

        return SummaryMetrics(
            average_volume=avg_vol,
            median_volume=med_vol,
            peak_hour=peak_hr,
            peak_volume=peak_rec,
            total_observations=total_obs,
            total_days=total_days,
            congestion_distribution=cong_dist
        )

    def get_hourly_trend(self, spec: Optional[FilterSpec] = None) -> List[HourlyTrendPoint]:
        """Computes 24-hour traffic volume curve."""
        filtered_df = self.apply_filters(spec)
        points = []

        if len(filtered_df) == 0:
            return points

        grp = filtered_df.groupby("hour")["traffic_volume"]
        means = grp.mean().to_dict()
        medians = grp.median().to_dict()
        mins = grp.min().to_dict()
        maxs = grp.max().to_dict()
        counts = grp.count().to_dict()

        for h in range(24):
            mean_v = round(float(means.get(h, 0.0)), 1)
            med_v = float(medians.get(h, 0.0))
            min_v = int(mins.get(h, 0))
            max_v = int(maxs.get(h, 0))
            cnt = int(counts.get(h, 0))

            if mean_v < 1500:
                cat = "Low"
            elif mean_v < 3500:
                cat = "Moderate"
            elif mean_v < 5000:
                cat = "Heavy"
            else:
                cat = "Severe"

            points.append(HourlyTrendPoint(
                hour=h,
                mean_volume=mean_v,
                median_volume=med_v,
                min_volume=min_v,
                max_volume=max_v,
                count=cnt,
                congestion_category=cat
            ))

        return points

    def get_timeline(self, spec: Optional[FilterSpec] = None, max_points: int = 120) -> List[TimelinePoint]:
        """Computes daily aggregated trendline across the selected time period."""
        filtered_df = self.apply_filters(spec)
        if len(filtered_df) == 0:
            return []

        daily = filtered_df.groupby("date_str").agg(
            mean_volume=("traffic_volume", "mean"),
            peak_volume=("traffic_volume", "max"),
            count=("traffic_volume", "count")
        ).reset_index()

        daily = daily.sort_values("date_str")

        # Downsample if number of days exceeds max_points for smooth client rendering
        if len(daily) > max_points:
            step = int(np.ceil(len(daily) / max_points))
            daily = daily.iloc[::step].reset_index(drop=True)

        return [
            TimelinePoint(
                date=row["date_str"],
                mean_volume=round(float(row["mean_volume"]), 1),
                peak_volume=int(row["peak_volume"]),
                count=int(row["count"])
            )
            for _, row in daily.iterrows()
        ]

    def get_heatmap(self, spec: Optional[FilterSpec] = None) -> List[HeatmapCell]:
        """Computes 7 days x 24 hours matrix of average traffic volume."""
        filtered_df = self.apply_filters(spec)
        if len(filtered_df) == 0:
            return []

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        grp = filtered_df.groupby(["day_of_week", "hour"]).agg(
            mean_volume=("traffic_volume", "mean"),
            count=("traffic_volume", "count")
        ).reset_index()

        matrix_lookup = {
            (int(row["day_of_week"]), int(row["hour"])): (round(float(row["mean_volume"]), 1), int(row["count"]))
            for _, row in grp.iterrows()
        }

        cells = []
        for d in range(7):
            for h in range(24):
                val, cnt = matrix_lookup.get((d, h), (0.0, 0))
                if val < 1500:
                    cat = "Low"
                elif val < 3500:
                    cat = "Moderate"
                elif val < 5000:
                    cat = "Heavy"
                else:
                    cat = "Severe"

                cells.append(HeatmapCell(
                    day_of_week=d,
                    day_name=day_names[d],
                    hour=h,
                    mean_volume=val,
                    congestion_category=cat,
                    observation_count=cnt
                ))

        return cells

    def get_weather_impact(self, spec: Optional[FilterSpec] = None) -> List[WeatherImpactPoint]:
        """Analyzes volume impact across distinct weather categories."""
        filtered_df = self.apply_filters(spec)
        if len(filtered_df) == 0:
            return []

        total_obs = len(filtered_df)
        sub_avg = float(filtered_df["traffic_volume"].mean())

        grp = filtered_df.groupby("weather_main").agg(
            mean_volume=("traffic_volume", "mean"),
            median_volume=("traffic_volume", "median"),
            count=("traffic_volume", "count")
        ).reset_index()

        grp = grp.sort_values("count", ascending=False)

        results = []
        for _, row in grp.iterrows():
            cnt = int(row["count"])
            mean_v = round(float(row["mean_volume"]), 1)
            med_v = float(row["median_volume"])
            pct_tot = round((cnt / total_obs) * 100, 2)
            diff_pct = round(((mean_v - sub_avg) / sub_avg) * 100, 2) if sub_avg > 0 else 0.0

            results.append(WeatherImpactPoint(
                weather_main=str(row["weather_main"]),
                mean_volume=mean_v,
                median_volume=med_v,
                count=cnt,
                pct_of_total=pct_tot,
                volume_diff_pct_from_avg=diff_pct
            ))

        return results

    def get_distribution(self, spec: Optional[FilterSpec] = None) -> List[CongestionDistributionPoint]:
        """Returns distribution of volume across standard congestion classes."""
        filtered_df = self.apply_filters(spec)
        total = len(filtered_df)
        if total == 0:
            return []

        counts = filtered_df["congestion_category"].value_counts().to_dict()
        defs = {
            "Low": ("Nighttime and free-flow traffic", "< 1,500 veh/h"),
            "Moderate": ("Normal midday daytime flow", "1,500 – 3,499 veh/h"),
            "Heavy": ("Commute peak build-up", "3,500 – 4,999 veh/h"),
            "Severe": ("Rush-hour highway capacity", "≥ 5,000 veh/h")
        }

        results = []
        for cat in ["Low", "Moderate", "Heavy", "Severe"]:
            cnt = int(counts.get(cat, 0))
            pct = round((cnt / total) * 100, 2)
            desc, thresh = defs[cat]
            results.append(CongestionDistributionPoint(
                category=cat,
                count=cnt,
                percentage=pct,
                definition=desc,
                threshold=thresh
            ))

        return results

    def get_filter_options(self) -> Dict[str, Any]:
        """Provides available filter ranges and choices supported by this dataset."""
        return {
            "date_range": {
                "min": self.df["date_str"].min(),
                "max": self.df["date_str"].max()
            },
            "years": sorted(self.df["year"].unique().tolist()),
            "weather_categories": sorted(self.df["weather_main"].unique().tolist()),
            "days_of_week": [
                {"index": 0, "name": "Monday"},
                {"index": 1, "name": "Tuesday"},
                {"index": 2, "name": "Wednesday"},
                {"index": 3, "name": "Thursday"},
                {"index": 4, "name": "Friday"},
                {"index": 5, "name": "Saturday"},
                {"index": 6, "name": "Sunday"}
            ],
            "congestion_categories": ["Low", "Moderate", "Heavy", "Severe"],
            "total_clean_records": self.total_clean_records,
            "overall_avg_volume": round(self.overall_avg_volume, 1)
        }
