"""
Automated test suite for RoadCast backend and data contracts.
Tests ingestion artifacts, cleaning audit trail, analytics calculations,
API response contracts, and ML evaluation criteria.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient
import pandas as pd

from app.main import app
from app.analytics.engine import AnalyticsEngine
from app.domain.models import FilterSpec, PredictionRequest

client = TestClient(app)


def test_health_endpoint():
    """Verify health check returns valid JSON status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Historical" in data["disclaimer"]


def test_metadata_endpoint():
    """Verify dataset metadata matches PRD requirements."""
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == "uci_metro_interstate"
    assert "Interstate 94" in data["geographic_coverage"]["road_name"]
    assert data["is_synthetic"] is False
    assert "HISTORICAL" in data["disclaimer"]
    assert data["observation_count_clean"] > 40000


def test_filter_options_endpoint():
    """Verify filter options returns available years, weather categories, etc."""
    response = client.get("/api/v1/filters/options")
    assert response.status_code == 200
    data = response.json()
    assert "date_range" in data
    assert 2012 in data["years"]
    assert 2018 in data["years"]
    assert "Clear" in data["weather_categories"]
    assert "Snow" in data["weather_categories"]


def test_summary_endpoint():
    """Verify summary calculations."""
    payload = {"weather_main": ["Clear"]}
    response = client.post("/api/v1/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["average_volume"] > 0
    assert 0 <= data["peak_hour"] <= 23
    assert data["total_observations"] > 0
    assert "vehicles per hour" in data["unit"]


def test_empty_filter_state():
    """Verify empty result handling when filters match zero records."""
    # Impossible date filter
    payload = {"start_date": "1990-01-01", "end_date": "1990-01-02"}
    response = client.post("/api/v1/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_observations"] == 0
    assert data["average_volume"] == 0.0


def test_hourly_trend_endpoint():
    """Verify 24 hourly data points are returned with correct ranges."""
    response = client.post("/api/v1/charts/hourly", json={})
    assert response.status_code == 200
    points = response.json()
    assert len(points) == 24
    for pt in points:
        assert 0 <= pt["hour"] <= 23
        assert pt["mean_volume"] >= 0
        assert pt["congestion_category"] in ["Low", "Moderate", "Heavy", "Severe"]


def test_heatmap_endpoint():
    """Verify 7x24 = 168 heatmap cells are generated."""
    response = client.post("/api/v1/charts/heatmap", json={})
    assert response.status_code == 200
    cells = response.json()
    assert len(cells) == 168
    for c in cells:
        assert 0 <= c["day_of_week"] <= 6
        assert 0 <= c["hour"] <= 23
        assert c["mean_volume"] >= 0


def test_weather_impact_endpoint():
    """Verify weather comparison chart endpoint."""
    response = client.post("/api/v1/charts/weather", json={})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    categories = [w["weather_main"] for w in data]
    assert "Clear" in categories


def test_deterministic_insights():
    """Verify insights are generated with supporting metrics and caveats."""
    response = client.post("/api/v1/insights", json={})
    assert response.status_code == 200
    findings = response.json()
    assert len(findings) >= 3
    for f in findings:
        assert len(f["title"]) > 0
        assert len(f["statement"]) > 0
        assert len(f["evidence"]) > 0
        assert len(f["caveat"]) > 0


def test_quality_and_dictionary():
    """Verify data quality audit report and data dictionary."""
    q_resp = client.get("/api/v1/quality")
    assert q_resp.status_code == 200
    q_data = q_resp.json()
    assert q_data["initial_record_count"] == 48204
    assert q_data["final_record_count"] == 40575
    assert len(q_data["audit_trail"]) > 0

    d_resp = client.get("/api/v1/dictionary")
    assert d_resp.status_code == 200
    d_data = d_resp.json()
    assert "fields" in d_data
    field_names = [f["name"] for f in d_data["fields"]]
    assert "traffic_volume" in field_names
    assert "date_time" in field_names


def test_model_evaluation_and_predict():
    """Verify ML model evaluation report and inference endpoint."""
    eval_resp = client.get("/api/v1/model/evaluation")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["candidate_ml_evaluation"]["mae"] < eval_data["baseline_evaluation"]["mae"]
    assert eval_data["candidate_ml_evaluation"]["r2_score"] > 0.90

    # Test inference
    pred_req = {
        "hour": 8,
        "day_name": "Tuesday",
        "month_name": "October",
        "temp_celsius": 12.0,
        "rain_1h": 0.0,
        "snow_1h": 0.0,
        "clouds_all": 20,
        "weather_main": "Clear",
        "is_holiday": False
    }
    pred_resp = client.post("/api/v1/predict", json=pred_req)
    assert pred_resp.status_code == 200
    pred_data = pred_resp.json()
    assert pred_data["predicted_volume"] > 3000
    assert "ESTIMATE ONLY" in pred_data["historical_estimate_notice"]
    assert len(pred_data["limitations"]) > 0


def test_commuter_route_supported_corridor():
    """Verify route planning on the supported I-94 testbed corridor."""
    payload = {
        "origin": "Minneapolis, MN",
        "destination": "St. Paul, MN",
        "departure_hour": 8,
        "departure_day": "Tuesday",
        "weather_condition": "Clear"
    }
    response = client.post("/api/v1/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_supported_corridor"] is True
    assert data["distance_km"] > 0
    assert data["duration_minutes"] > 0
    assert len(data["route_coordinates"]) > 0
    assert data["traffic_category"] in ["Low", "Moderate", "Heavy", "Severe"]
    assert data["estimated_volume"] is not None
    assert len(data["bottlenecks"]) > 0
    assert len(data["alternate_routes"]) > 0
    assert "best_departure_window" in data
    assert "traffic_outlook" in data


def test_commuter_route_unsupported_road():
    """Verify route planning on arbitrary roads (e.g. Pune) with commuter choke points and alternate routes."""
    payload = {
        "origin": "PCCOE Akurdi",
        "destination": "Shivajinagar Pune",
        "departure_hour": 8,
        "departure_day": "Tuesday",
        "weather_condition": "Clear"
    }
    response = client.post("/api/v1/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_supported_corridor"] is False
    assert data["distance_km"] > 0
    assert data["duration_minutes"] > 0
    assert len(data["route_coordinates"]) > 0
    assert len(data["bottlenecks"]) > 0
    assert len(data["alternate_routes"]) > 0
    assert "best_departure_window" in data


def test_statistical_hypothesis_endpoint():
    """Verify statistical hypothesis testing endpoint returns Welch's t-test report."""
    response = client.get("/api/v1/statistics/hypothesis-test")
    assert response.status_code == 200
    data = response.json()
    assert "Two-Sample Welch's t-Test" in data["test_name"]
    assert data["hypotheses"]["significance_level_alpha"] == 0.05
    assert data["sample_statistics"]["weekday"]["sample_size_N"] > 20000
    assert data["sample_statistics"]["weekend"]["sample_size_N"] > 10000
    assert data["test_results"]["is_statistically_significant"] is True
    assert "Reject H0" in data["test_results"]["decision"]


def test_sqlite_persistence_query():
    """Verify processed records can be queried directly via SQLite."""
    from app.persistence.sqlite_db import query_traffic_by_filters, get_sqlite_summary
    summary = get_sqlite_summary()
    assert summary["total_records"] > 40000
    assert summary["avg_volume"] > 0

    rows = query_traffic_by_filters(hour=8, limit=10)
    assert len(rows) == 10
    assert rows[0]["hour"] == 8

