"""
Transformation and Data Cleaning module for RoadCast.
Standardizes schema, parses timestamps, handles missingness, removes timestamp duplicates,
filters physically impossible sensor errors (e.g., 0 Kelvin, 9800mm rain spikes),
derives temporal features and congestion categories,
and exports an auditable cleaning report.
"""

import os
import json
import datetime
import pandas as pd
import numpy as np

RAW_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "Metro_Interstate_Traffic_Volume.csv")
PROCESSED_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "metro_traffic_processed.csv")
REPORT_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "data_quality", "cleaning_report.json")


def clean_and_transform(raw_path: str = RAW_FILE, output_path: str = PROCESSED_FILE, report_path: str = REPORT_FILE) -> dict:
    """
    Executes reproducible cleaning pipeline on the raw dataset.
    """
    print(f"Reading raw data from: {raw_path}")
    raw_df = pd.read_csv(raw_path)
    initial_rows = int(len(raw_df))
    initial_cols = int(len(raw_df.columns))

    audit_log = []

    # 1. Missing values audit
    missing_counts = {col: int(cnt) for col, cnt in raw_df.isnull().sum().items()}
    audit_log.append({
        "step": "missingness_audit",
        "description": "Quantified missing values per column prior to imputation or drop.",
        "details": missing_counts
    })

    # Holiday normalization: replace NaN with 'None'
    df = raw_df.copy()
    holiday_nulls = int(df["holiday"].isnull().sum())
    df["holiday"] = df["holiday"].fillna("None")
    audit_log.append({
        "step": "holiday_normalization",
        "description": "Normalized non-holiday records from null to 'None'.",
        "records_affected": holiday_nulls
    })

    # 2. Timestamp parsing
    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    invalid_dates = int(df["date_time"].isnull().sum())
    if invalid_dates > 0:
        df = df.dropna(subset=["date_time"])
        audit_log.append({
            "step": "timestamp_validation",
            "description": "Dropped unparseable timestamps.",
            "records_dropped": invalid_dates
        })

    # Sort chronologically
    df = df.sort_values("date_time").reset_index(drop=True)

    # 3. Deduplication by timestamp key
    # Multiple weather rows occasionally exist for the same timestamp with the exact same traffic count.
    # We aggregate or retain the primary entry to guarantee 1 record per hour key.
    dups_count = int(df.duplicated(subset=["date_time"]).sum())
    df = df.drop_duplicates(subset=["date_time"], keep="first").reset_index(drop=True)
    audit_log.append({
        "step": "deduplication",
        "key": ["date_time"],
        "description": "Removed duplicate hourly readings for identical timestamps to produce continuous hourly time-series.",
        "duplicates_removed": dups_count
    })

    # 4. Validity checks & anomaly filtration
    # A. Temperature: 0 Kelvin (-273.15 C) indicates equipment sensor communication error
    temp_zero_mask = df["temp"] <= 10.0  # 10 K = -263 C, impossible in Minnesota
    temp_anomalies = int(temp_zero_mask.sum())
    if temp_anomalies > 0:
        # Impute with local forward/backward fill
        df.loc[temp_zero_mask, "temp"] = np.nan
        df["temp"] = df["temp"].ffill().bfill()
        audit_log.append({
            "step": "temperature_anomaly_handling",
            "description": "Identified sensor freeze (0 K) records and imputed from adjacent hourly observations.",
            "records_corrected": temp_anomalies
        })

    # B. Rain: outlier sensor glitch (e.g. 9831 mm in 1 hour)
    rain_glitch_mask = df["rain_1h"] > 250.0  # 250mm/hour exceeds all-time state records
    rain_anomalies = int(rain_glitch_mask.sum())
    if rain_anomalies > 0:
        df.loc[rain_glitch_mask, "rain_1h"] = np.nan
        df["rain_1h"] = df["rain_1h"].ffill().bfill()
        audit_log.append({
            "step": "rainfall_anomaly_handling",
            "description": "Capped physically impossible rainfall gauge spikes (>250mm/hr) using local forward fill.",
            "records_corrected": rain_anomalies
        })

    # C. Traffic volume validity check: non-negative and realistic
    invalid_volume_count = int(((df["traffic_volume"] < 0) | (df["traffic_volume"] > 10000)).sum())
    if invalid_volume_count > 0:
        df = df[(df["traffic_volume"] >= 0) & (df["traffic_volume"] <= 10000)]
        audit_log.append({
            "step": "traffic_volume_range_check",
            "description": "Filtered records with negative or out-of-range (>10000) volume.",
            "records_dropped": invalid_volume_count
        })

    # 5. Feature Engineering
    # Temperature in Celsius
    df["temp_celsius"] = (df["temp"] - 273.15).round(2)

    # Time features
    df["hour"] = df["date_time"].dt.hour
    df["day_of_week"] = df["date_time"].dt.dayofweek
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["day_name"] = df["day_of_week"].map(lambda d: day_names[d])
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["month"] = df["date_time"].dt.month
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    df["month_name"] = df["month"].map(month_names)
    df["year"] = df["date_time"].dt.year
    df["is_holiday"] = (df["holiday"] != "None").astype(int)

    # Congestion category
    # Defined thresholds:
    # Low: < 1500 veh/h (typical night / light traffic)
    # Moderate: 1500 - 3499 veh/h (midday normal flow)
    # Heavy: 3500 - 4999 veh/h (peak approach)
    # Severe: >= 5000 veh/h (rush hour full capacity)
    def categorize_congestion(vol):
        if vol < 1500:
            return "Low"
        elif vol < 3500:
            return "Moderate"
        elif vol < 5000:
            return "Heavy"
        else:
            return "Severe"

    df["congestion_category"] = df["traffic_volume"].apply(categorize_congestion)

    # Category normalization for weather_main
    df["weather_main"] = df["weather_main"].astype(str).str.strip().str.title()

    final_rows = int(len(df))
    final_cols = int(len(df.columns))

    # Save processed CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Processed dataset saved to: {output_path} ({final_rows} rows, {final_cols} columns)")

    # Build Quality and Cleaning Report
    report = {
        "execution_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_file": raw_path,
        "output_file": output_path,
        "initial_record_count": initial_rows,
        "final_record_count": final_rows,
        "records_removed_total": initial_rows - final_rows,
        "retention_rate_pct": round((final_rows / initial_rows) * 100, 2),
        "columns_added": [
            "temp_celsius", "hour", "day_of_week", "day_name",
            "is_weekend", "month", "month_name", "year", "is_holiday", "congestion_category"
        ],
        "date_range": {
            "start": str(df["date_time"].min()),
            "end": str(df["date_time"].max())
        },
        "traffic_volume_summary": {
            "mean": round(float(df["traffic_volume"].mean()), 2),
            "median": float(df["traffic_volume"].median()),
            "std": round(float(df["traffic_volume"].std()), 2),
            "min": int(df["traffic_volume"].min()),
            "max": int(df["traffic_volume"].max()),
            "unit": "vehicles/hour"
        },
        "congestion_distribution": {k: int(v) for k, v in df["congestion_category"].value_counts().items()},
        "audit_trail": audit_log
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Quality & cleaning report saved to: {report_path}")
    return report


if __name__ == "__main__":
    rep = clean_and_transform()
    print("Clean and transform completed successfully.")
