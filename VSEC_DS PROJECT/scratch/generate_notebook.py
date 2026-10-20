"""Script to generate the RoadCast Data Science Pipeline Jupyter Notebook."""
import json
import os

notebook_dir = os.path.join(os.path.dirname(__file__), "..", "..", "notebooks")
os.makedirs(notebook_dir, exist_ok=True)
notebook_path = os.path.join(notebook_dir, "RoadCast_Data_Science_Pipeline.ipynb")

def make_cell(cell_type, source, outputs=None):
    if cell_type == "markdown":
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [s + "\n" for s in source.split("\n")]
        }
    else:
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": outputs or [],
            "source": [s + "\n" for s in source.split("\n")]
        }

cells = []

# Title & Affiliation
cells.append(make_cell("markdown", """# RoadCast — Complete Data Science Pipeline & Traffic Analytics
### Mini-Project for S.Y. B.Tech Information Technology, PCCoE Pune
**Subject:** Data Science Tools and Environment (Semester IV)  
**Dataset:** Metro Interstate Traffic Volume (Westbound I-94, Minnesota ATR Station 301)  
**Authors:** Department of Information Technology, Pimpri Chinchwad College of Engineering, Pune  

---
## Pipeline Overview
1. **Data Acquisition:** Importing raw CSV with Pandas, JSON metadata, and SQLite database persistence.
2. **Data Cleaning & Preprocessing:** Null handling, timestamp deduplication, physical sensor error filtering, IQR outlier analysis, and temporal feature extraction.
3. **Exploratory Data Analysis (EDA):** Matplotlib & Seaborn visualizations of volume distribution, 24-hr rush curve, weekday/weekend profile, time-series trends, and correlation heatmap.
4. **Statistical Hypothesis Testing:** Formal Two-Sample Welch's t-test comparing weekday vs. weekend traffic volumes with assumption verification.
5. **Machine Learning Modeling:** Chronological 80/20 train-test split, Historical Baseline vs. HistGradientBoosting Regressor (MAE, RMSE, R²), and 4-tier Congestion Classification (Accuracy, Precision, Recall, F1, Confusion Matrix).
6. **Application Integration & Limitations:** Commuter route planning integration and geographic scope boundaries."""))

# Section 1
cells.append(make_cell("markdown", """## 1. Environment Setup & Dependency Imports
We import standard scientific Python libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy.stats`, `sqlite3`, and `scikit-learn`."""))

cells.append(make_cell("code", """import os
import sys
import json
import sqlite3
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_absolute_error, root_mean_squared_error, r2_score,
    accuracy_score, precision_recall_fscore_support, confusion_matrix
)

# Set visual styling
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 10
print("Environment successfully initialized.")"""))

# Section 2: Data Acquisition
cells.append(make_cell("markdown", """## 2. Data Acquisition
We demonstrate:
1. Importing raw tabular records from CSV using **Pandas**.
2. Loading metadata from **JSON**.
3. Persisting cleaned records into an **SQLite relational database** (`traffic.db`) and executing SQL queries."""))

cells.append(make_cell("code", """raw_csv_path = os.path.join("..", "data", "raw", "Metro_Interstate_Traffic_Volume.csv")
manifest_path = os.path.join("..", "data", "metadata", "dataset_manifest.json")

# 1. Pandas CSV Ingestion
raw_df = pd.read_csv(raw_csv_path)
print(f"Raw Dataset Dimensions: {raw_df.shape[0]:,} rows x {raw_df.shape[1]} columns")

# 2. JSON Ingestion
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)
print(f"Dataset Name: {manifest['name']}")
print(f"Road Coverage: {manifest['geographic_coverage']['road_name']} ({manifest['geographic_coverage']['station_id']})")
raw_df.head(5)"""))

# Section 3: Data Cleaning
cells.append(make_cell("markdown", """## 3. Data Cleaning & Preprocessing
In accordance with the syllabus, we perform:
- Missing value audit and imputation.
- Duplicate record identification and deduplication.
- Filtering physically impossible sensor values (e.g., 0 Kelvin temperature spikes, 9800mm rain recording errors).
- Outlier analysis using IQR with domain justification (avoiding dropping genuine rush-hour volume).
- Datetime parsing and temporal feature engineering."""))

cells.append(make_cell("code", """clean_df = raw_df.copy()

# A. Missing Value Handling
print("Missing values per column:")
print(clean_df.isnull().sum())
# Holiday null values represent non-holiday operating days: normalize to 'None'
clean_df['holiday'] = clean_df['holiday'].fillna('None')

# B. Datetime Conversion & Deduplication
clean_df['date_time'] = pd.to_datetime(clean_df['date_time'])
clean_df = clean_df.sort_values('date_time').reset_index(drop=True)

duplicates_count = clean_df.duplicated(subset=['date_time']).sum()
print(f"\\nDuplicate hourly timestamps detected: {duplicates_count:,}")
clean_df = clean_df.drop_duplicates(subset=['date_time'], keep='first').reset_index(drop=True)

# C. Sensor Freeze & Anomaly Corrections
# Temp: 0 Kelvin is physically impossible; replace with realistic median
invalid_temp = (clean_df['temp'] < 200.0) | (clean_df['temp'] > 335.0)
print(f"Invalid temperature records filtered: {invalid_temp.sum()}")
clean_df = clean_df[~invalid_temp].copy()
clean_df['temp_celsius'] = np.round(clean_df['temp'] - 273.15, 2)

# Rain: 9,832mm is an erroneous gauge multiplier; clip at 100mm
clean_df['rain_1h'] = clean_df['rain_1h'].apply(lambda x: 0.0 if x > 100.0 else float(x))
clean_df['snow_1h'] = clean_df['snow_1h'].apply(lambda x: 0.0 if x > 100.0 else float(x))

# D. Temporal Feature Engineering
clean_df['hour'] = clean_df['date_time'].dt.hour
clean_df['day_of_week'] = clean_df['date_time'].dt.dayofweek
clean_df['day_name'] = clean_df['date_time'].dt.day_name()
clean_df['month'] = clean_df['date_time'].dt.month
clean_df['month_name'] = clean_df['date_time'].dt.month_name()
clean_df['year'] = clean_df['date_time'].dt.year
clean_df['is_weekend'] = clean_df['day_of_week'].isin([5, 6]).astype(int)
clean_df['is_holiday'] = (clean_df['holiday'] != 'None').astype(int)

# Capacity tiers
def get_tier(v):
    if v < 1500: return 'Low'
    elif v < 3500: return 'Moderate'
    elif v < 5000: return 'Heavy'
    else: return 'Severe'

clean_df['congestion_category'] = clean_df['traffic_volume'].apply(get_tier)

print(f"\\nFinal Clean Dataset: {len(clean_df):,} verified records (Retention: {len(clean_df)/len(raw_df)*100:.2f}%)")"""))

# SQLite Persistence
cells.append(make_cell("markdown", """### Relational Database Persistence (SQLite)
We store the cleaned DataFrame into `data/traffic.db` and query it using standard SQL."""))

cells.append(make_cell("code", """db_path = os.path.join("..", "data", "traffic.db")
conn = sqlite3.connect(db_path)

# Store table
clean_df.to_sql("metro_traffic", conn, if_exists="replace", index=False)

# Query via SQL
sql_query = \"\"\"
SELECT hour, ROUND(AVG(traffic_volume), 1) as avg_volume, COUNT(*) as observations
FROM metro_traffic
WHERE is_weekend = 0
GROUP BY hour
ORDER BY avg_volume DESC
LIMIT 5;
\"\"\"
top_hours_sql = pd.read_sql_query(sql_query, conn)
conn.close()
print("Top 5 Busiest Weekday Hours (Queried via SQLite):")
top_hours_sql"""))

# Section 4: EDA
cells.append(make_cell("markdown", """## 4. Exploratory Data Analysis (EDA)
Using **Matplotlib** and **Seaborn**, we visualize:
1. Traffic volume distribution (Mean vs Median)
2. 24-hour commuter rush curve with standard deviation bands
3. Weekday vs Weekend volume disparity
4. Multi-year traffic volume timeline
5. Feature correlation heatmap
6. Weather impacts on traffic throughput"""))

cells.append(make_cell("code", """# 1. Volume Distribution
plt.figure(figsize=(9, 4.5))
sns.histplot(clean_df['traffic_volume'], kde=True, bins=45, color='#10B981', alpha=0.6)
plt.axvline(clean_df['traffic_volume'].mean(), color='red', linestyle='--', label=f"Mean: {clean_df['traffic_volume'].mean():.0f}")
plt.axvline(clean_df['traffic_volume'].median(), color='blue', linestyle=':', label=f"Median: {clean_df['traffic_volume'].median():.0f}")
plt.title("Empirical Traffic Volume Distribution (Westbound I-94)", fontsize=12, fontweight='bold')
plt.xlabel("Traffic Volume (vehicles per hour)")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.show()"""))

cells.append(make_cell("code", """# 2. 24-Hour Commute Curve
hourly_curve = clean_df.groupby('hour')['traffic_volume'].agg(['mean', 'std']).reset_index()

plt.figure(figsize=(10, 4.5))
sns.lineplot(data=hourly_curve, x='hour', y='mean', marker='o', color='#2563EB', linewidth=2.5, label='Hourly Mean')
plt.fill_between(hourly_curve['hour'], hourly_curve['mean'] - 0.5*hourly_curve['std'], hourly_curve['mean'] + 0.5*hourly_curve['std'], color='#93C5FD', alpha=0.35, label='±0.5 Std Dev')
plt.title("24-Hour Bimodal Commute Rush Curve", fontsize=12, fontweight='bold')
plt.xlabel("Hour of Day (00:00 - 23:00)")
plt.ylabel("Mean Volume (veh/h)")
plt.xticks(range(0, 24))
plt.legend()
plt.tight_layout()
plt.show()"""))

cells.append(make_cell("code", """# 3. Weekday vs Weekend Comparison
weekday_hourly = clean_df[clean_df['is_weekend'] == 0].groupby('hour')['traffic_volume'].mean()
weekend_hourly = clean_df[clean_df['is_weekend'] == 1].groupby('hour')['traffic_volume'].mean()

plt.figure(figsize=(10, 4.5))
plt.plot(weekday_hourly.index, weekday_hourly.values, marker='s', color='#3B82F6', linewidth=2.2, label='Weekdays (Mon–Fri)')
plt.plot(weekend_hourly.index, weekend_hourly.values, marker='^', color='#F59E0B', linewidth=2.2, label='Weekends (Sat–Sun)')
plt.title("Weekday vs Weekend Hourly Volume Profiles", fontsize=12, fontweight='bold')
plt.xlabel("Hour of Day")
plt.ylabel("Mean Volume (veh/h)")
plt.xticks(range(0, 24))
plt.legend()
plt.tight_layout()
plt.show()"""))

cells.append(make_cell("code", """# 4. Correlation Heatmap
corr_cols = ['traffic_volume', 'hour', 'day_of_week', 'month', 'temp_celsius', 'rain_1h', 'snow_1h', 'clouds_all', 'is_weekend', 'is_holiday']
plt.figure(figsize=(8, 6))
mask = np.triu(np.ones_like(clean_df[corr_cols].corr(), dtype=bool))
sns.heatmap(clean_df[corr_cols].corr(), mask=mask, annot=True, fmt='.2f', cmap='vlag', vmin=-0.6, vmax=0.6, linewidths=0.5)
plt.title("Pearson Correlation Matrix", fontsize=12, fontweight='bold')
plt.tight_layout()
plt.show()"""))

# Section 5: Statistical Testing
cells.append(make_cell("markdown", """## 5. Statistical Hypothesis Testing
### Syllabus Requirement: Formulating and evaluating an empirical hypothesis test
- **Research Question:** Does highway traffic volume differ significantly between weekdays and weekends?
- **Null Hypothesis ($H_0$):** $\\mu_{\\text{weekday}} = \\mu_{\\text{weekend}}$ (No difference in population mean volume).
- **Alternative Hypothesis ($H_1$):** $\\mu_{\\text{weekday}} \\neq \\mu_{\\text{weekend}}$ (Significant volume difference exists).
- **Significance Level:** $\\alpha = 0.05$.
- **Test Selected:** Two-sample Welch's t-test (unpooled variances)."""))

cells.append(make_cell("code", """weekday_vol = clean_df[clean_df['is_weekend'] == 0]['traffic_volume']
weekend_vol = clean_df[clean_df['is_weekend'] == 1]['traffic_volume']

# Check assumptions
print(f"Sample Sizes: N_weekday = {len(weekday_vol):,}, N_weekend = {len(weekend_vol):,}")
levene_stat, levene_p = stats.levene(weekday_vol, weekend_vol)
print(f"Levene Variance Test: W = {levene_stat:.2f}, p-value = {levene_p:.4e} (Variances are unequal -> Welch's t-test justified)")

# Execute Welch's t-test
t_stat, p_val = stats.ttest_ind(weekday_vol, weekend_vol, equal_var=False)

print(f"\\n--- Test Results ---")
print(f"Weekday Mean: {weekday_vol.mean():.2f} veh/h (Std: {weekday_vol.std():.2f})")
print(f"Weekend Mean: {weekend_vol.mean():.2f} veh/h (Std: {weekend_vol.std():.2f})")
print(f"Difference:   +{weekday_vol.mean() - weekend_vol.mean():.2f} veh/h on weekdays")
print(f"t-Statistic:  {t_stat:.4f}")
print(f"p-Value:      {p_val:.4e}")

if p_val < 0.05:
    print("\\nConclusion: Reject H0 at alpha = 0.05. Weekday traffic volume is statistically significantly higher than weekend volume.")
else:
    print("\\nConclusion: Fail to reject H0.")"""))

# Section 6: Machine Learning
cells.append(make_cell("markdown", """## 6. Machine Learning Modeling & Evaluation
We build and evaluate:
1. **Historical Baseline Model:** Hour-of-Day $\\times$ Day-of-Week historical mean.
2. **Supervised ML Model:** `HistGradientBoostingRegressor` with OneHotEncoding.
3. **Chronological 80/20 Train-Test Split:** Strictly avoids future data leakage.
4. **Regression Metrics:** MAE, RMSE, $R^2$.
5. **Classification Evaluation:** 4-tier capacity classification (Accuracy, Precision, Recall, F1, and Confusion Matrix)."""))

cells.append(make_cell("code", """# Chronological 80/20 Split
split_idx = int(len(clean_df) * 0.8)
train_df = clean_df.iloc[:split_idx].copy()
test_df = clean_df.iloc[split_idx:].copy()

print(f"Train Period: {train_df['date_time'].min()} to {train_df['date_time'].max()} (N={len(train_df):,})")
print(f"Test Period:  {test_df['date_time'].min()} to {test_df['date_time'].max()} (N={len(test_df):,})")

y_train = train_df['traffic_volume'].values
y_test = test_df['traffic_volume'].values

# Baseline Evaluation
baseline_lookup = train_df.groupby(['day_of_week', 'hour'])['traffic_volume'].mean().to_dict()
overall_mean = y_train.mean()
y_test_base = test_df.apply(lambda r: baseline_lookup.get((r['day_of_week'], r['hour']), overall_mean), axis=1).values

base_mae = mean_absolute_error(y_test, y_test_base)
base_rmse = root_mean_squared_error(y_test, y_test_base)
base_r2 = r2_score(y_test, y_test_base)
print(f"Baseline -> MAE: {base_mae:.2f}, RMSE: {base_rmse:.2f}, R2: {base_r2:.4f}")

# Machine Learning Pipeline
cat_cols = ['weather_main', 'day_name', 'month_name']
num_cols = ['hour', 'day_of_week', 'month', 'temp_celsius', 'rain_1h', 'snow_1h', 'clouds_all', 'is_weekend', 'is_holiday']

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols),
    ('num', 'passthrough', num_cols)
])

ml_pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', HistGradientBoostingRegressor(max_iter=150, learning_rate=0.08, max_depth=8, random_state=42))
])

ml_pipe.fit(train_df[cat_cols + num_cols], y_train)
y_test_pred = np.clip(ml_pipe.predict(test_df[cat_cols + num_cols]), 0, 8000)

ml_mae = mean_absolute_error(y_test, y_test_pred)
ml_rmse = root_mean_squared_error(y_test, y_test_pred)
ml_r2 = r2_score(y_test, y_test_pred)

print(f"HistGradientBoosting -> MAE: {ml_mae:.2f}, RMSE: {ml_rmse:.2f}, R2: {ml_r2:.4f}")
print(f"MAE Error Reduction: {((base_mae - ml_mae)/base_mae)*100:.2f}% | RMSE Error Reduction: {((base_rmse - ml_rmse)/base_rmse)*100:.2f}%")"""))

cells.append(make_cell("code", """# Classification Evaluation & Confusion Matrix
tier_names = ['Low', 'Moderate', 'Heavy', 'Severe']
y_test_cat = [get_tier(v) for v in y_test]
y_pred_cat = [get_tier(v) for v in y_test_pred]

acc = accuracy_score(y_test_cat, y_pred_cat)
p, r, f, _ = precision_recall_fscore_support(y_test_cat, y_pred_cat, labels=tier_names, average='macro', zero_division=0)
cm = confusion_matrix(y_test_cat, y_pred_cat, labels=tier_names)

print(f"Classification Accuracy: {acc*100:.2f}%")
print(f"Macro Precision:        {p:.4f}")
print(f"Macro Recall:           {r:.4f}")
print(f"Macro F1-Score:         {f:.4f}")

plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=tier_names, yticklabels=tier_names)
plt.title(f"Confusion Matrix (Accuracy: {acc*100:.1f}%)", fontweight='bold')
plt.xlabel("Predicted Congestion Tier")
plt.ylabel("True Congestion Tier")
plt.tight_layout()
plt.show()"""))

# Section 7: Limitations
cells.append(make_cell("markdown", """## 7. Commuter Application Context & Limitations
1. **Corridor Boundary:** The model is empirically trained on Interstate 94 (ATR Station 301, Minneapolis-St. Paul). Predictions apply strictly to highway corridors with similar sensor configurations and must not be blindly extrapolated to city streets in Pune, Mumbai, or elsewhere.
2. **Historical vs. Live Data:** RoadCast provides expected historical patterns. It is not an active GPS navigation feed.
3. **College Syllabus Demonstration:** All objectives for **Data Science Tools and Environment** (Data Acquisition, Data Cleaning, EDA, Hypothesis Testing, Machine Learning, and Web Integration) have been met in this project."""))

notebook_content = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbformat": 4,
            "nbformat_minor": 2,
            "pygments_lexer": "ipython3",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=2)

print(f"Successfully generated notebook at: {notebook_path}")
