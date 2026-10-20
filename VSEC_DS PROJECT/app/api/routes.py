"""
REST API routes for RoadCast.
Provides endpoints for dataset metadata, dynamic filters, summary indicators,
chart-ready aggregates, evidence-backed insights, data quality, and model inference.
"""

import os
import json
import io
import csv
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from app.domain.models import (
    FilterSpec, DatasetMetadata, SummaryMetrics,
    HourlyTrendPoint, TimelinePoint, HeatmapCell,
    WeatherImpactPoint, CongestionDistributionPoint,
    Finding, QualityReport, PredictionRequest, PredictionResponse,
    RouteRequest, RouteResponse
)
from app.analytics.engine import AnalyticsEngine
from app.insights.generator import generate_findings
from app.models.inference import ModelService
from app.routing.service import calculate_route, generate_commuter_traffic_intelligence



router = APIRouter(prefix="/api/v1", tags=["RoadCast Analytics"])

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


@router.get("/metadata", response_model=DatasetMetadata)
def get_metadata():
    """Returns dataset provenance, license, geographic and temporal coverage."""
    engine = AnalyticsEngine.get_instance()
    return engine.manifest


@router.get("/filters/options")
def get_filter_options():
    """Returns available filter options and dataset boundaries."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_filter_options()


@router.post("/summary", response_model=SummaryMetrics)
def get_summary(spec: Optional[FilterSpec] = None):
    """Computes summary indicators for dashboard metric cards based on active filters."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_summary(spec)


@router.post("/charts/hourly", response_model=List[HourlyTrendPoint])
def get_hourly_trend(spec: Optional[FilterSpec] = None):
    """Returns 24-hour average traffic volume curve."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_hourly_trend(spec)


@router.post("/charts/timeline", response_model=List[TimelinePoint])
def get_timeline(spec: Optional[FilterSpec] = None, max_points: int = Query(100, ge=10, le=500)):
    """Returns chronological timeline aggregated by day."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_timeline(spec, max_points=max_points)


@router.post("/charts/heatmap", response_model=List[HeatmapCell])
def get_heatmap(spec: Optional[FilterSpec] = None):
    """Returns 7 days x 24 hours traffic volume matrix."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_heatmap(spec)


@router.post("/charts/weather", response_model=List[WeatherImpactPoint])
def get_weather_impact(spec: Optional[FilterSpec] = None):
    """Returns traffic volume comparison across weather conditions."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_weather_impact(spec)


@router.post("/charts/distribution", response_model=List[CongestionDistributionPoint])
def get_distribution(spec: Optional[FilterSpec] = None):
    """Returns volume distribution by defined congestion tiers."""
    engine = AnalyticsEngine.get_instance()
    return engine.get_distribution(spec)


@router.post("/insights", response_model=List[Finding])
def get_insights(spec: Optional[FilterSpec] = None):
    """Generates evidence-backed historical findings with scientific caveats."""
    engine = AnalyticsEngine.get_instance()
    return generate_findings(engine, spec)


@router.get("/quality", response_model=QualityReport)
def get_quality_report():
    """Returns data cleaning report, row counts, and anomaly handling audit trail."""
    report_path = os.path.join(REPORTS_DIR, "data_quality", "cleaning_report.json")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Quality report not yet generated.")
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/dictionary")
def get_data_dictionary():
    """Returns field dictionary with types, units, and missing value behavior."""
    dict_path = os.path.join(DATA_DIR, "metadata", "data_dictionary.json")
    if not os.path.exists(dict_path):
        raise HTTPException(status_code=404, detail="Data dictionary not found.")
    with open(dict_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/model/evaluation")
def get_model_evaluation():
    """Returns evaluation metrics comparing candidate ML model against baseline."""
    eval_path = os.path.join(REPORTS_DIR, "model", "evaluation_report.json")
    if not os.path.exists(eval_path):
        raise HTTPException(status_code=404, detail="Model evaluation report not found.")
    with open(eval_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.post("/predict", response_model=PredictionResponse)
def predict_traffic(req: PredictionRequest):
    """Generates a labeled historical traffic volume estimate with baseline comparison."""
    service = ModelService.get_instance()
    return service.predict(req)


@router.get("/sample")
def get_sample_records(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("date_time", pattern="^(date_time|traffic_volume|temp_celsius|hour)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Returns paginated rows from the processed dataset for inspection."""
    engine = AnalyticsEngine.get_instance()
    df = engine.df

    ascending = (sort_order == "asc")
    df_sorted = df.sort_values(sort_by, ascending=ascending)

    total_records = len(df_sorted)
    page_records = df_sorted.iloc[offset:offset + limit]

    columns = [
        "date_time", "traffic_volume", "congestion_category", "hour",
        "day_name", "month_name", "weather_main", "temp_celsius", "rain_1h", "snow_1h", "is_holiday"
    ]
    records = page_records[columns].to_dict(orient="records")
    for r in records:
        r["date_time"] = str(r["date_time"])

    return {
        "total": total_records,
        "offset": offset,
        "limit": limit,
        "records": records
    }


@router.post("/export")
def export_filtered_data(spec: Optional[FilterSpec] = None):
    """Exports filtered dataset rows as a CSV file."""
    engine = AnalyticsEngine.get_instance()
    filtered = engine.apply_filters(spec)

    columns = [
        "date_time", "traffic_volume", "congestion_category", "hour",
        "day_name", "temp_celsius", "rain_1h", "snow_1h", "clouds_all",
        "weather_main", "is_holiday", "holiday"
    ]
    sub = filtered[columns].head(10000)  # limit export size for safety

    stream = io.StringIO()
    sub.to_csv(stream, index=False)
    stream.seek(0)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=roadcast_filtered_traffic.csv"
    return response


@router.post("/route", response_model=RouteResponse)
def analyze_commute_route(req: RouteRequest):
    """
    Main commuter route query endpoint.
    Computes driving route geometry, distance, travel duration,
    and returns actionable commuter traffic intelligence:
    - Time-specific traffic conditions
    - Specific choke points and bottleneck places with delays
    - Alternate routes to save travel time
    - Optimal departure windows
    """
    try:
        route_data = calculate_route(req.origin, req.destination)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Routing error: {str(e)}")

    is_supported = route_data["is_supported_corridor"]

    # Generate customer-facing traffic intelligence
    commuter_intel = generate_commuter_traffic_intelligence(
        origin_name=route_data["origin"]["name"],
        dest_name=route_data["destination"]["name"],
        departure_hour=req.departure_hour,
        departure_day=req.departure_day,
        distance_km=route_data["distance_km"],
        duration_minutes=route_data["duration_minutes"]
    )

    estimated_vol = None
    baseline_vol = None
    diff_val = None

    if is_supported:
        try:
            model_service = ModelService.get_instance()
            pred_req = PredictionRequest(
                hour=req.departure_hour,
                day_name=req.departure_day,
                month_name="October",
                temp_celsius=12.0,
                rain_1h=0.0,
                snow_1h=0.0,
                clouds_all=20,
                weather_main=req.weather_condition,
                is_holiday=False
            )
            pred = model_service.predict(pred_req)
            estimated_vol = pred.predicted_volume
            baseline_vol = pred.baseline_volume
            diff_val = pred.difference_from_baseline
        except Exception:
            pass

    return RouteResponse(
        origin=route_data["origin"],
        destination=route_data["destination"],
        distance_km=route_data["distance_km"],
        duration_minutes=route_data["duration_minutes"],
        traffic_category=commuter_intel["traffic_category"],
        traffic_color=commuter_intel["traffic_color"],
        traffic_status_label=commuter_intel["traffic_status_label"],
        traffic_level_text=commuter_intel["traffic_level_text"],
        traffic_outlook=commuter_intel["traffic_outlook"],
        route_coordinates=route_data["route_coordinates"],
        is_supported_corridor=is_supported,
        corridor_name=route_data["corridor_name"],
        traffic_notice=commuter_intel["traffic_outlook"],
        bottlenecks=commuter_intel["bottlenecks"],
        alternate_routes=commuter_intel["alternate_routes"],
        best_departure_window=commuter_intel["best_departure_window"],
        travel_tips=commuter_intel["travel_tips"],
        estimated_volume=estimated_vol,
        baseline_volume=baseline_vol,
        difference_from_baseline=diff_val,
        insights=[
            f"Expected condition: {commuter_intel['traffic_level_text']} at {req.departure_hour:02d}:00.",
            f"Recommended window: {commuter_intel['best_departure_window']}",
            f"Distance: {route_data['distance_km']} km (Estimated driving duration: ~{route_data['duration_minutes']} mins)."
        ]
    )



@router.get("/statistics/hypothesis-test")
def get_hypothesis_test_report():
    """
    Returns empirical hypothesis test results for Weekday vs Weekend Traffic Disparity
    (Two-sample Welch's t-test with formal assumptions, t-stat, p-value, and commuter conclusion).
    """
    from app.analytics.statistical_tests import run_weekday_vs_weekend_hypothesis_test
    return run_weekday_vs_weekend_hypothesis_test()


