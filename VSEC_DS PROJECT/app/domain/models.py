"""
Domain models and schema contracts for RoadCast.
Adheres strictly to PRD and architecture specifications:
- Distinguishes observed, derived, synthetic, and predicted measures.
- Enforces units, boundaries, and historical notices.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FilterSpec(BaseModel):
    """Normalized filter specification shared across all analytics, charts, and findings."""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    hours: Optional[List[int]] = Field(None, description="List of hours (0-23)")
    days_of_week: Optional[List[int]] = Field(None, description="List of days of week (0=Mon, 6=Sun)")
    weather_main: Optional[List[str]] = Field(None, description="List of weather categories (e.g., Clear, Rain, Snow)")
    is_holiday: Optional[bool] = Field(None, description="Filter for holiday occurrences")
    is_weekend: Optional[bool] = Field(None, description="Filter for weekends (Sat-Sun)")
    congestion_category: Optional[List[str]] = Field(None, description="Filter by congestion level (Low, Moderate, Heavy, Severe)")


class DatasetMetadata(BaseModel):
    """Dataset provenance and coverage information."""
    dataset_id: str
    name: str
    version: str
    description: str
    source_url: str
    retrieval_date: str
    license: str
    attribution: str
    geographic_coverage: Dict[str, Any]
    temporal_coverage: Dict[str, Any]
    observation_count_raw: int
    observation_count_clean: int
    sampling_frequency: str
    is_synthetic: bool
    disclaimer: str


class SummaryMetrics(BaseModel):
    """High-level summary indicators for the dashboard metric cards."""
    average_volume: float = Field(..., description="Average traffic volume in vehicles per hour")
    median_volume: float = Field(..., description="Median traffic volume in vehicles per hour")
    peak_hour: int = Field(..., description="Hour of the day with the highest average traffic volume (0-23)")
    peak_volume: int = Field(..., description="Single highest recorded hourly volume in the filtered selection")
    total_observations: int = Field(..., description="Total matching hourly records")
    total_days: int = Field(..., description="Count of distinct days represented")
    congestion_distribution: Dict[str, int] = Field(..., description="Counts per congestion tier")
    unit: str = "vehicles per hour"
    historical_notice: str = "Historical observation data from I-94 ATR 301 station."


class HourlyTrendPoint(BaseModel):
    hour: int
    mean_volume: float
    median_volume: float
    min_volume: int
    max_volume: int
    count: int
    congestion_category: str


class TimelinePoint(BaseModel):
    date: str
    mean_volume: float
    peak_volume: int
    count: int


class HeatmapCell(BaseModel):
    day_of_week: int
    day_name: str
    hour: int
    mean_volume: float
    congestion_category: str
    observation_count: int


class WeatherImpactPoint(BaseModel):
    weather_main: str
    mean_volume: float
    median_volume: float
    count: int
    pct_of_total: float
    volume_diff_pct_from_avg: float


class CongestionDistributionPoint(BaseModel):
    category: str
    count: int
    percentage: float
    definition: str
    threshold: str


class Finding(BaseModel):
    id: str
    title: str
    statement: str
    evidence: str
    supporting_metric: str
    time_scope: str
    caveat: str
    category: str


class QualityReport(BaseModel):
    execution_timestamp: str
    initial_record_count: int
    final_record_count: int
    records_removed_total: int
    retention_rate_pct: float
    columns_added: List[str]
    date_range: Dict[str, str]
    traffic_volume_summary: Dict[str, Any]
    congestion_distribution: Dict[str, int]
    audit_trail: List[Dict[str, Any]]


class PredictionRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)")
    day_name: str = Field("Tuesday", description="Day of week (Monday to Sunday)")
    month_name: str = Field("October", description="Month name (January to December)")
    temp_celsius: float = Field(15.0, description="Air temperature in Celsius")
    rain_1h: float = Field(0.0, ge=0.0, description="Precipitation accumulation in mm")
    snow_1h: float = Field(0.0, ge=0.0, description="Snow accumulation in mm")
    clouds_all: int = Field(20, ge=0, le=100, description="Cloud cover percentage (0-100)")
    weather_main: str = Field("Clear", description="Weather condition (Clear, Clouds, Rain, Snow, Mist, Fog, etc.)")
    is_holiday: bool = Field(False, description="Is it an observed national holiday")


class PredictionResponse(BaseModel):
    predicted_volume: float
    baseline_volume: float
    difference_from_baseline: float
    pct_difference: float
    congestion_category: str
    confidence_interval: Dict[str, float]
    model_name: str
    model_version: str
    unit: str = "vehicles per hour"
    historical_estimate_notice: str
    limitations: List[str]


class RouteRequest(BaseModel):
    """Commuter route search request."""
    origin: str = Field(..., description="Starting location name or address")
    destination: str = Field(..., description="Destination name or address")
    departure_hour: int = Field(8, ge=0, le=23, description="Departure hour of day (0-23)")
    departure_day: str = Field("Tuesday", description="Day of week")
    weather_condition: str = Field("Clear", description="Observed/expected weather")


class RouteResponse(BaseModel):
    """Commuter route analysis response with interactive geometry and traffic insights."""
    origin: Dict[str, Any]
    destination: Dict[str, Any]
    distance_km: float
    duration_minutes: int
    traffic_category: str = Field(..., description="Low, Moderate, Heavy, or Severe")
    traffic_color: str = Field(..., description="Hex color: #65D69A, #FFC46B, #FF727F")
    traffic_status_label: str = Field(..., description="Short commute summary")
    route_coordinates: List[List[float]] = Field(..., description="Array of [lat, lon] coordinates for map polyline")
    is_supported_corridor: bool = False
    corridor_name: str = ""
    traffic_notice: str = ""
    traffic_outlook: str = ""
    traffic_level_text: str = ""
    bottlenecks: List[Dict[str, str]] = Field(default_factory=list)
    alternate_routes: List[Dict[str, Any]] = Field(default_factory=list)
    best_departure_window: str = ""
    travel_tips: List[str] = Field(default_factory=list)
    estimated_volume: Optional[float] = None
    baseline_volume: Optional[float] = None
    difference_from_baseline: Optional[float] = None
    insights: List[str] = Field(default_factory=list)


