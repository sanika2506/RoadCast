# RoadCast — Commuter Traffic Intelligence & Route Analytics
### Mini-Project for S.Y. B.Tech Information Technology, PCCoE Pune
**Course:** Data Science Tools and Environment (Semester IV)  
**Institution:** Pimpri Chinchwad College of Engineering (PCCoE), Nigdi, Pune  
**Technology Stack:** Python 3.12, Pandas, NumPy, Matplotlib, Seaborn, SciPy, scikit-learn, SQLite, FastAPI, Leaflet.js, OpenStreetMap  

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![Tests Passing](https://img.shields.io/badge/pytest-15%20passed-brightgreen.svg)](tests/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **Academic Notice:** RoadCast is an educational traffic data science and analytics platform built to demonstrate the complete curriculum of *Data Science Tools and Environment*. It analyzes empirical highway traffic sensor records. It is **not** an active GPS live navigation service. Historical models must never be confused with live turn-by-turn routing or guaranteed travel durations.

---

## 1. Problem Statement
Highway traffic congestion imposes severe socio-economic burdens: millions of wasted commuter hours, excess carbon emissions, and elevated collision rates. While professional engineers utilize complex data warehousing tools, ordinary commuters and transport planners require a simple, intuitive **"Know Before You Go"** interface that:
1. Accepts a starting location and destination.
2. Displays the driving route on an interactive map.
3. Estimates realistic journey distance and driving duration.
4. Delivers rigorous historical traffic intelligence and machine-learning predictions without burying the commuter under complex technical dashboards.

---

## 2. Objectives
- **Simplicity for Commuters:** Provide a minimalist 4-step workflow: *Enter Origin &rarr; Enter Destination &rarr; Click "Show My Route" &rarr; View interactive map and traffic insights.*
- **Complete Data Science Workflow:** Demonstrate the full syllabus lifecycle:
  $$\text{Data Acquisition} \rightarrow \text{Data Cleaning} \rightarrow \text{EDA} \rightarrow \text{Visualization} \rightarrow \text{Statistical Hypothesis Testing} \rightarrow \text{ML Modeling} \rightarrow \text{Model Evaluation} \rightarrow \text{Web UI Integration}$$
- **Relational Storage:** Integrate SQLite (`data/traffic.db`) demonstrating database table creation, indexing, and SQL aggregation queries.
- **Hypothesis Testing:** Conduct formal hypothesis testing (Welch's two-sample t-test) to mathematically quantify the weekday vs. weekend traffic volume disparity.
- **Machine Learning Rigor:** Train and evaluate a `HistGradientBoostingRegressor` against an Hour $\times$ Day historical baseline using a strict chronological split (80% train, 20% test) to prevent future data leakage, supplemented by 4-tier congestion classification metrics.
- **Geographic Boundary Transparency:** Explicitly delineate between the calibrated sensor testbed (Interstate 94 ATR 301) and arbitrary road networks (e.g., Pune, Mumbai), preventing fabricated live traffic claims.

---

## 3. Dataset & Data Source
| Metadata Attribute | Empirical Specification |
|---|---|
| **Dataset Title** | Metro Interstate Traffic Volume |
| **Data Repository** | UCI Machine Learning Repository / MnDOT |
| **Source DOI** | [10.24432/C56S30](https://doi.org/10.24432/C56S30) (John Hogue, 2019) |
| **Measurement Station** | Westbound Interstate 94 at ATR Station 301 (Minneapolis–St. Paul, MN) |
| **Temporal Span** | October 2, 2012 to September 30, 2018 (6 full years of continuous hourly monitoring) |
| **Raw Record Count** | 48,204 hourly rows |
| **Clean Deduplicated Records** | **40,575 verified hourly records** (84.17% retention rate) |

### Key Fields & Units
- `traffic_volume` *(int)*: Hourly vehicle throughput (**vehicles per hour / veh/h**).
- `date_time` *(datetime)*: ISO 8601 timestamp.
- `temp_celsius` *(float)*: Ambient air temperature in **Degrees Celsius (°C)**.
- `weather_main` *(str)*: High-level weather category (*Clear, Clouds, Rain, Snow, Drizzle, Mist, Fog, Thunderstorm*).
- `congestion_category` *(str)*: Standardized highway capacity tiers:
  - **Low** (Green): $< 1,500$ veh/h (Nighttime free-flow)
  - **Moderate** (Yellow): $1,500 – 3,499$ veh/h (Midday steady flow)
  - **Heavy** (Red): $3,500 – 4,999$ veh/h (Peak commuter approach)
  - **Severe** (Purple): $\ge 5,000$ veh/h (Highway operating at maximum capacity)

---

## 4. Data Acquisition & Cleaning
### A. Ingestion
- Raw CSV records ingested using **Pandas** (`pd.read_csv`).
- Dataset provenance and geographic metadata parsed from **JSON** (`dataset_manifest.json`).
- Processed records stored into **SQLite** (`data/traffic.db`) with indexes on `hour`, `day_of_week`, and `congestion_category`.

### B. Cleaning & Feature Engineering Decisions
1. **Missing Data Imputation:** Null values in `holiday` represent regular non-holiday operating days and are normalized to `"None"`.
2. **Timestamp Deduplication:** 7,629 duplicate hourly timestamps were identified and removed, retaining the primary sensor observation.
3. **Physical Sensor Error Removal:** Sensor failure records recording 0 Kelvin temperature or rain spikes of 9,832mm were identified and filtered.
4. **IQR Outlier Domain Justification:** Standard IQR flags traffic volume above 4,800 veh/h as upper outliers. In highway engineering, these represent **valid rush-hour peak capacity** rather than measurement errors. Blindly deleting them would destroy the model's ability to forecast peak congestion. They are strictly preserved.
5. **Feature Derivation:** Extracted `hour` (0–23), `day_of_week` (0–6), `day_name`, `month`, `month_name`, `is_weekend`, `is_holiday`, and `congestion_category`.

---

## 5. Exploratory Data Analysis (EDA) Findings
Using **Matplotlib** and **Seaborn**, six publication-grade visualizations are generated and saved to `reports/figures/`:
1. **Traffic Volume Distribution (`1_traffic_volume_distribution.png`):** Bimodal distribution with an overall historical mean of **3,291 veh/h** and median of **3,380 veh/h**.
2. **24-Hour Commuter Rush Curve (`2_average_traffic_by_hour.png`):** Twin peak structure with a morning rush at **07:00** (~4,700 veh/h) and evening rush at **17:00** (~4,800 veh/h). Free-flow minimum occurs at 03:00 (~500 veh/h).
3. **Weekday vs. Weekend Disparity (`3_weekday_vs_weekend.png`):** Weekdays show pronounced twin commute peaks; weekends show a smooth, unimodal plateau peaking at midday (~4,300 veh/h).
4. **Multi-Year Timeline (`4_traffic_trends_over_time.png`):** A 7-day rolling average confirms stable recurring annual seasonal demand across all 6 years (2012–2018).
5. **Correlation Matrix (`5_correlation_heatmap.png`):** Demonstrates strong positive correlation between `hour` and `traffic_volume` ($r = +0.62$) and negative correlation with `is_weekend` ($r = -0.28$).
6. **Weather Condition Impact (`6_weather_impact_traffic.png`):** Severe weather conditions (snow, thunderstorms, heavy rain) depress average hourly highway throughput by 8% to 14% due to speed drops and trip cancellations.

---

## 6. Statistical Hypothesis Testing
### Research Question: Does average highway traffic volume differ significantly between weekdays and weekends?
- **Null Hypothesis ($H_0$):** $\mu_{\text{weekday}} = \mu_{\text{weekend}}$ (No difference in population mean volume).
- **Alternative Hypothesis ($H_1$):** $\mu_{\text{weekday}} \neq \mu_{\text{weekend}}$ (Statistically significant difference exists).
- **Significance Level:** $\alpha = 0.05$.
- **Test Selection:** Two-sample Welch's t-test (two-tailed, unpooled variances).

### Test Assumptions Verified:
1. **Sample Size Adequacy:** $N_{\text{weekday}} = 28,983$, $N_{\text{weekend}} = 11,592$. Both $N > 30$, satisfying the Central Limit Theorem.
2. **Variance Homogeneity:** Levene's test yielded $W = 68.4$, $p < 0.0001$. Variances are unequal ($\sigma^2_{\text{weekday}} \neq \sigma^2_{\text{weekend}}$), directly justifying Welch's unpooled degrees of freedom.

### Empirical Results:
| Group | Sample Size ($N$) | Mean Volume | Standard Deviation | Welch's $t$-Statistic | $p$-Value | Decision ($\alpha = 0.05$) |
|---|---|---|---|---|---|---|
| **Weekdays (Mon–Fri)** | 28,983 | 3,485 veh/h | 2,012 veh/h | **$t = +49.52$** | **$p < 0.0001$** ($10^{-300}$) | **Reject $H_0$** (Extremely Significant) |
| **Weekends (Sat–Sun)** | 11,592 | 2,694 veh/h | 1,847 veh/h | | | |

**Commuter & Scientific Takeaway:** With $t = +49.52$ and $p < 0.0001$, we reject the null hypothesis at the 5% significance level. Weekday hourly volume averages **~791 vehicles/hour higher** than weekends due to mandatory work/school commutes.

---

## 7. Machine Learning Algorithm
- **Chronological Train/Test Split (80% Train, 20% Test):**
  - **Train Set:** 32,460 observations (Oct 2, 2012 to Oct 26, 2017).
  - **Test Set:** 8,115 observations (Oct 26, 2017 to Sep 30, 2018).
  - *No future data leakage*: The model never sees future timestamps during training.
- **Features Used:**
  - Categorical (OneHotEncoded): `weather_main`, `day_name`, `month_name`.
  - Numeric (Passthrough): `hour`, `day_of_week`, `month`, `temp_celsius`, `rain_1h`, `snow_1h`, `clouds_all`, `is_weekend`, `is_holiday`.
- **Model Architecture:** `HistGradientBoostingRegressor` with 150 boosting stages, learning rate 0.08, max depth 8, and monotonic non-negative clipping.

---

## 8. Model Evaluation Metrics
### A. Regression Evaluation (vs. Historical Baseline)
| Model | MAE (veh/h) | RMSE (veh/h) | $R^2$ Score | Performance Gain |
|---|---|---|---|---|
| **Historical Baseline** (Hour $\times$ Day Mean) | 277.16 | 497.82 | 0.9361 | Reference |
| **Candidate ML Model** (`HistGradientBoosting`) | **265.35** | **461.77** | **0.9451** | **4.26% MAE reduction, 7.24% RMSE reduction** |

### B. Congestion Tier Classification Evaluation
Predictions mapped into 4 standardized capacity tiers:
- **Classification Accuracy:** **87.50%**
- **Macro Precision:** 87.50%
- **Macro Recall:** 87.40%
- **Macro F1-Score:** **87.44%**
- **Confusion Matrix:** Generated and saved to `reports/figures/7_confusion_matrix_model.png`.

---

## 9. System Architecture
RoadCast implements a lightweight modular monolith:
```
VSEC_DS PROJECT/
├── app/
│   ├── api/
│   │   └── routes.py              # REST API endpoints (/api/v1/route, /statistics/hypothesis-test)
│   ├── domain/
│   │   └── models.py              # Pydantic schemas (RouteRequest, RouteResponse, etc.)
│   ├── routing/
│   │   └── service.py             # OpenStreetMap Nominatim & OSRM integration with corridor detection
│   ├── persistence/
│   │   └── sqlite_db.py           # SQLite relational database storage and SQL query layer
│   ├── analytics/
│   │   ├── engine.py              # In-memory query engine
│   │   ├── eda_visualizer.py      # Matplotlib/Seaborn plot generator
│   │   └── statistical_tests.py   # Welch's t-test hypothesis evaluation
│   ├── models/
│   │   ├── train_evaluate.py      # ML training, baseline comparison, metrics export
│   │   └── inference.py           # Model inference service
│   ├── static/
│   │   ├── index.html             # Simplified commuter UI + EDA tabs
│   │   ├── css/main.css           # Responsive styling (Mobile, Tablet, Desktop)
│   │   ├── js/app.js              # Leaflet OpenStreetMap controller
│   │   └── figures/               # Static EDA charts for web presentation
│   └── main.py                    # FastAPI server entry point
├── data/
│   ├── raw/                       # Original UCI CSV records
│   ├── processed/                 # Cleaned dataset (40,575 rows)
│   └── traffic.db                 # SQLite database
├── notebooks/
│   └── RoadCast_Data_Science_Pipeline.ipynb # Complete Jupyter Notebook
├── reports/
│   ├── figures/                   # High-resolution PNG visualizations
│   └── model/evaluation_report.json # Serialized evaluation metrics
├── tests/
│   └── test_backend.py            # 15 automated pytest tests
├── requirements.txt               # Pinned dependencies
└── run.py                         # One-click startup runner
```

---

## 10. Limitations & Future Scope
### Academic Limitations
1. **Geographic Sensor Boundary:** Model weights are calibrated strictly on westbound Interstate 94 ATR Station 301. They must not be claimed as valid predictions for Pune, Mumbai, or arbitrary municipal roads without local inductive loop sensor data.
2. **Historical vs. Live Data:** RoadCast models expected empirical patterns; it does not replace live GPS navigation feeds.
3. **Severe Anomalies:** Major multi-lane catastrophic incidents or extreme blizzards exceeding 30 inches can cause real-time travel times to deviate from historical expectations.

### Future Scope
1. Ingest municipal smart city sensor feeds from Pune Smart City Development Corporation (PSCDCL).
2. Train localized models on Indian urban corridors (e.g., Pune-Mumbai Expressway, Hinjewadi IT corridor).
3. Integrate real-time weather radar APIs for short-term 30-minute precipitation forecasting.

---

## 11. Installation & Execution Steps

### Prerequisites
- Python 3.10+ (Recommended: Python 3.12)
- Git & Windows PowerShell / Linux Terminal

### Step 1: Clone or Open the Project
```bash
cd "VSEC_DS PROJECT"
```

### Step 2: Set Up Virtual Environment & Dependencies
```bash
# Using standard Python
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate (Linux/macOS)

pip install -r requirements.txt
```

### Step 3: Run Full Automated Test Suite (15 Tests)
```bash
python -m pytest
```

### Step 4: Launch the Web Application
```bash
python run.py
```
Open your browser and navigate to:
- **Interactive Commuter Web App:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Interactive ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Step 5: Explore the Jupyter Notebook
Open [`notebooks/RoadCast_Data_Science_Pipeline.ipynb`](notebooks/RoadCast_Data_Science_Pipeline.ipynb) in VS Code or Jupyter Lab to run all data acquisition, cleaning, EDA, statistical testing, and ML cells step-by-step.
