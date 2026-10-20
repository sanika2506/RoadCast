"""
Exploratory Data Analysis (EDA) and Visualization Generator for RoadCast.
Generates Matplotlib and Seaborn plots covering the complete Data Science Tools & Environment syllabus.
Outputs high-resolution charts to reports/figures/ and app/static/figures/.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set consistent styling
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "metro_traffic_processed.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "..", "..", "reports", "figures")
STATIC_FIGURES_DIR = os.path.join(BASE_DIR, "..", "static", "figures")


def ensure_dirs():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(STATIC_FIGURES_DIR, exist_ok=True)


def save_figure(fig, filename: str):
    p1 = os.path.join(FIGURES_DIR, filename)
    p2 = os.path.join(STATIC_FIGURES_DIR, filename)
    fig.savefig(p1, dpi=200, bbox_inches="tight")
    fig.savefig(p2, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[EDA] Generated figure: {filename}")


def generate_all_eda_visualizations(data_path: str = PROCESSED_DATA_PATH):
    """Generates all 6 syllabus-mandated EDA visualizations using Pandas, Matplotlib, and Seaborn."""
    ensure_dirs()
    print(f"[EDA] Loading processed dataset from: {data_path}")
    df = pd.read_csv(data_path)
    df["date_time"] = pd.to_datetime(df["date_time"])

    # 1. Traffic Volume Distribution Plot
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(df["traffic_volume"], kde=True, bins=45, color="#10B981", ax=ax, edgecolor="#047857", alpha=0.6)
    ax.set_title("1. Empirical Traffic Volume Distribution (Westbound I-94)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Traffic Volume (vehicles per hour)", fontsize=11)
    ax.set_ylabel("Frequency (Hourly Observations)", fontsize=11)
    mean_vol = df["traffic_volume"].mean()
    median_vol = df["traffic_volume"].median()
    ax.axvline(mean_vol, color="#EF4444", linestyle="--", linewidth=1.5, label=f"Mean: {mean_vol:.0f} veh/h")
    ax.axvline(median_vol, color="#3B82F6", linestyle=":", linewidth=1.8, label=f"Median: {median_vol:.0f} veh/h")
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")
    save_figure(fig, "1_traffic_volume_distribution.png")

    # 2. Average Traffic by Hour (24-Hour Commute Rush Curve)
    fig, ax = plt.subplots(figsize=(10, 5))
    hourly_stats = df.groupby("hour")["traffic_volume"].agg(["mean", "std", "count"]).reset_index()
    sns.lineplot(data=hourly_stats, x="hour", y="mean", color="#2563EB", linewidth=2.5, marker="o", ax=ax, label="Hourly Mean")
    ax.fill_between(hourly_stats["hour"], hourly_stats["mean"] - 0.5 * hourly_stats["std"], hourly_stats["mean"] + 0.5 * hourly_stats["std"], color="#93C5FD", alpha=0.35, label="±0.5 Std Dev Band")
    # Annotate peaks
    ax.annotate("Morning Rush Peak\n07:00 (~4,700 veh/h)", xy=(7, 4700), xytext=(2, 5300),
                arrowprops=dict(facecolor="#EF4444", shrink=0.08, width=1.5, headwidth=6),
                fontweight="bold", color="#B91C1C", fontsize=9.5)
    ax.annotate("Evening Rush Peak\n17:00 (~4,800 veh/h)", xy=(17, 4800), xytext=(18, 5400),
                arrowprops=dict(facecolor="#EF4444", shrink=0.08, width=1.5, headwidth=6),
                fontweight="bold", color="#B91C1C", fontsize=9.5)
    ax.set_title("2. 24-Hour Bimodal Commute Rush Curve", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day (00:00 - 23:00)", fontsize=11)
    ax.set_ylabel("Average Volume (vehicles per hour)", fontsize=11)
    ax.set_xticks(range(0, 24))
    ax.legend(frameon=True, facecolor="#FFFFFF")
    save_figure(fig, "2_average_traffic_by_hour.png")

    # 3. Traffic on Weekdays versus Weekends
    fig, ax = plt.subplots(figsize=(10, 5))
    weekday_df = df[df["is_weekend"] == 0].groupby("hour")["traffic_volume"].mean().reset_index()
    weekend_df = df[df["is_weekend"] == 1].groupby("hour")["traffic_volume"].mean().reset_index()
    sns.lineplot(data=weekday_df, x="hour", y="traffic_volume", color="#3B82F6", linewidth=2.5, marker="s", label="Weekdays (Mon–Fri)", ax=ax)
    sns.lineplot(data=weekend_df, x="hour", y="traffic_volume", color="#F59E0B", linewidth=2.5, marker="^", label="Weekends (Sat–Sun)", ax=ax)
    ax.set_title("3. Traffic Volume Disparity: Weekdays vs. Weekends", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day (00:00 - 23:00)", fontsize=11)
    ax.set_ylabel("Mean Traffic Volume (veh/h)", fontsize=11)
    ax.set_xticks(range(0, 24))
    ax.legend(frameon=True, facecolor="#FFFFFF")
    save_figure(fig, "3_weekday_vs_weekend.png")

    # 4. Traffic Trends Over Time (Multi-Year Weekly Rolling Average)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    daily_traffic = df.set_index("date_time").resample("D")["traffic_volume"].mean().dropna()
    rolling_7d = daily_traffic.rolling(window=7, min_periods=3).mean()
    ax.plot(daily_traffic.index, daily_traffic.values, color="#94A3B8", alpha=0.3, label="Daily Mean")
    ax.plot(rolling_7d.index, rolling_7d.values, color="#059669", linewidth=2, label="7-Day Rolling Trend")
    ax.set_title("4. Multi-Year Traffic Volume Timeline (2012–2018)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Traffic Volume (veh/h)", fontsize=11)
    ax.legend(frameon=True, facecolor="#FFFFFF")
    save_figure(fig, "4_traffic_trends_over_time.png")

    # 5. Correlation Heatmap
    fig, ax = plt.subplots(figsize=(8, 6.5))
    corr_cols = ["traffic_volume", "hour", "day_of_week", "month", "temp_celsius", "rain_1h", "snow_1h", "clouds_all", "is_weekend", "is_holiday"]
    corr_matrix = df[corr_cols].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="vlag", vmin=-0.6, vmax=0.6,
                linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title("5. Pearson Correlation Matrix of Traffic & Environmental Features", fontsize=12.5, fontweight="bold", pad=12)
    save_figure(fig, "5_correlation_heatmap.png")

    # 6. Traffic Patterns for Different Weather Conditions
    fig, ax = plt.subplots(figsize=(10, 5))
    weather_stats = df.groupby("weather_main")["traffic_volume"].agg(["mean", "std", "count"]).reset_index()
    weather_stats = weather_stats.sort_values(by="mean", ascending=False)
    palette = sns.color_palette("mako", len(weather_stats))
    sns.barplot(data=weather_stats, x="weather_main", y="mean", palette=palette, ax=ax, edgecolor="#334155")
    ax.set_title("6. Impact of Weather Conditions on Average Traffic Volume", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Reported Weather Main Condition", fontsize=11)
    ax.set_ylabel("Mean Traffic Volume (veh/h)", fontsize=11)
    for i, row in enumerate(weather_stats.itertuples()):
        ax.text(i, row.mean + 60, f"{row.mean:.0f}\n(N={row.count})", ha="center", fontsize=8.5, color="#1E293B")
    ax.set_ylim(0, max(weather_stats["mean"]) * 1.18)
    save_figure(fig, "6_weather_impact_traffic.png")

    print("[EDA] All 6 syllabus visualizations generated successfully.")


if __name__ == "__main__":
    generate_all_eda_visualizations()
