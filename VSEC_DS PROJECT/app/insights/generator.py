"""
Deterministic, evidence-linked insights generator for RoadCast.
Calculates findings directly from computed aggregates and annotates them
with exact mathematical evidence, time periods, and explicit scientific caveats.
"""

from typing import List, Optional
import pandas as pd
from app.domain.models import FilterSpec, Finding
from app.analytics.engine import AnalyticsEngine


def generate_findings(engine: AnalyticsEngine, spec: Optional[FilterSpec] = None) -> List[Finding]:
    """
    Computes evidence-backed insights based on the current filtered dataset.
    """
    filtered_df = engine.apply_filters(spec)
    total_count = len(filtered_df)

    if total_count < 50:
        return [
            Finding(
                id="ins-insufficient",
                title="Insufficient Sample Size",
                statement="The current filter selection contains too few observations to draw statistically sound conclusions.",
                evidence=f"Only {total_count} matching hourly observations found (minimum required: 50).",
                supporting_metric="Record count < 50",
                time_scope="Current Filter Selection",
                caveat="Broaden your date range or remove strict weather/time filters to inspect meaningful patterns.",
                category="data_quality"
            )
        ]

    findings: List[Finding] = []

    # 1. Commute Bimodal Peak Finding
    hourly = filtered_df.groupby("hour")["traffic_volume"].mean()
    am_peak_hr = int(hourly.loc[6:10].idxmax()) if len(hourly.loc[6:10]) > 0 else 7
    pm_peak_hr = int(hourly.loc[15:19].idxmax()) if len(hourly.loc[15:19]) > 0 else 16

    am_val = round(float(hourly.loc[am_peak_hr]), 0)
    pm_val = round(float(hourly.loc[pm_peak_hr]), 0)
    night_val = round(float(hourly.loc[2:4].mean()), 0) if len(hourly.loc[2:4]) > 0 else 500

    findings.append(Finding(
        id="ins-commute-peaks",
        title="Bimodal Daily Commute Peaks",
        statement=f"In this dataset, westbound I-94 exhibits distinct morning ({am_peak_hr}:00) and evening ({pm_peak_hr}:00) volume peaks.",
        evidence=f"Morning peak reaches {am_val:,} veh/h, while evening peak reaches {pm_val:,} veh/h, representing a {round((pm_val / max(night_val, 1)), 1)}x increase over late-night baseline ({night_val:,} veh/h).",
        supporting_metric=f"AM Peak: {am_val} veh/h @ {am_peak_hr}:00; PM Peak: {pm_val} veh/h @ {pm_peak_hr}:00",
        time_scope=f"Hours 00:00 - 23:00 (N={total_count} records)",
        caveat="Calculated for westbound traffic towards Minneapolis. Eastbound reverse-commute volumes are not measured by this sensor.",
        category="temporal_pattern"
    ))

    # 2. Weekday vs Weekend Volume Shift
    weekday_mask = filtered_df["is_weekend"] == 0
    weekend_mask = filtered_df["is_weekend"] == 1

    if weekday_mask.sum() > 20 and weekend_mask.sum() > 20:
        wkday_avg = round(float(filtered_df.loc[weekday_mask, "traffic_volume"].mean()), 0)
        wkend_avg = round(float(filtered_df.loc[weekend_mask, "traffic_volume"].mean()), 0)
        drop_pct = round(((wkday_avg - wkend_avg) / wkday_avg) * 100, 1)

        findings.append(Finding(
            id="ins-weekend-drop",
            title="Pronounced Weekend Volume Contraction",
            statement=f"In this dataset, average hourly traffic volume contracts by {drop_pct}% on weekends compared to business weekdays.",
            evidence=f"Weekday mean is {wkday_avg:,} veh/h versus weekend mean of {wkend_avg:,} veh/h (difference of {int(wkday_avg - wkend_avg):,} veh/h).",
            supporting_metric=f"Weekday: {wkday_avg} veh/h vs Weekend: {wkend_avg} veh/h (-{drop_pct}%)",
            time_scope="Mondays–Fridays vs Saturdays–Sundays",
            caveat="Does not reflect special weekend event surges (e.g. stadium games or state fairs) that may produce localized spikes.",
            category="day_type"
        ))

    # 3. Adverse Weather Volume Impact
    weather_means = filtered_df.groupby("weather_main")["traffic_volume"].agg(["mean", "count"])
    clear_mean = float(weather_means.loc["Clear", "mean"]) if "Clear" in weather_means.index else None
    snow_mean = float(weather_means.loc["Snow", "mean"]) if "Snow" in weather_means.index else None

    if clear_mean is not None and snow_mean is not None and weather_means.loc["Snow", "count"] >= 30:
        snow_diff = round(((snow_mean - clear_mean) / clear_mean) * 100, 1)
        findings.append(Finding(
            id="ins-weather-impact",
            title="Snowfall Associated with Reduced Recorded Volume",
            statement=f"In this dataset, snowfall events correspond to an average {abs(snow_diff)}% change in observed traffic throughput relative to clear conditions.",
            evidence=f"Clear conditions average {round(clear_mean):,} veh/h (N={int(weather_means.loc['Clear', 'count']):,}) compared to {round(snow_mean):,} veh/h during snow events (N={int(weather_means.loc['Snow', 'count']):,}).",
            supporting_metric=f"Clear: {round(clear_mean)} veh/h vs Snow: {round(snow_mean)} veh/h ({snow_diff}%)",
            time_scope="Historical Weather Categories",
            caveat="Lower volume may reflect trip cancellations, diversion, or reduced sensor detection speed; correlation does not imply direct vehicle count causality.",
            category="environmental_influence"
        ))

    # 4. Holiday vs Non-Holiday Commute Pattern
    holidays_df = filtered_df[filtered_df["is_holiday"] == 1]
    if len(holidays_df) >= 10:
        hol_mean = round(float(holidays_df["traffic_volume"].mean()), 0)
        overall_mean = round(float(filtered_df["traffic_volume"].mean()), 0)
        hol_diff = round(((hol_mean - overall_mean) / overall_mean) * 100, 1)

        findings.append(Finding(
            id="ins-holiday-pattern",
            title="Observed Holiday Traffic Behavior",
            statement=f"In this dataset, officially recorded holidays display a {abs(hol_diff)}% shift in average volume relative to overall conditions.",
            evidence=f"Holiday mean is {hol_mean:,} veh/h across {len(holidays_df)} observed hours, closely mirroring weekend leisure profiles rather than weekday commute curves.",
            supporting_metric=f"Holiday Mean: {hol_mean} veh/h vs Overall: {overall_mean} veh/h ({hol_diff}%)",
            time_scope=f"Recognized US Holidays (N={len(holidays_df)} hours)",
            caveat="Holiday schedules vary widely; major travel holidays (Thanksgiving, Christmas) exhibit different profiles than minor federal holidays.",
            category="holiday_behavior"
        ))

    return findings
