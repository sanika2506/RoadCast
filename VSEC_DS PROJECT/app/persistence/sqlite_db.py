"""
SQLite persistence module for RoadCast.
Demonstrates relational database integration (Syllabus: Data Acquisition & Storage)
Stores cleaned traffic records into traffic.db and provides structured SQL query interfaces.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "traffic.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns an active SQLite database connection."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def store_processed_data_to_sqlite(df: pd.DataFrame, db_path: str = DB_PATH, table_name: str = "metro_traffic") -> int:
    """
    Saves or updates processed traffic records into SQLite table.
    Demonstrates Pandas DataFrame to SQL conversion.
    """
    conn = get_connection(db_path)
    try:
        # Write dataframe to SQL table
        df_to_save = df.copy()
        if "date_time" in df_to_save.columns:
            df_to_save["date_time"] = df_to_save["date_time"].astype(str)

        df_to_save.to_sql(table_name, conn, if_exists="replace", index=False)

        # Create indexes for fast query performance
        cursor = conn.cursor()
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_hour ON {table_name}(hour);")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_day ON {table_name}(day_of_week);")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_congestion ON {table_name}(congestion_category);")
        conn.commit()

        count_cursor = conn.cursor()
        count_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = count_cursor.fetchone()[0]
        print(f"[SQLite] Successfully stored {total} records into {db_path} ({table_name}).")
        return total
    finally:
        conn.close()


def query_traffic_by_filters(
    hour: Optional[int] = None,
    day_of_week: Optional[int] = None,
    weather: Optional[str] = None,
    limit: int = 50,
    db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """
    Queries records using parameterized SQL statements.
    """
    conn = get_connection(db_path)
    try:
        query = "SELECT date_time, traffic_volume, congestion_category, hour, day_name, temp_celsius, weather_main FROM metro_traffic WHERE 1=1"
        params = []

        if hour is not None:
            query += " AND hour = ?"
            params.append(hour)
        if day_of_week is not None:
            query += " AND day_of_week = ?"
            params.append(day_of_week)
        if weather is not None:
            query += " AND weather_main = ?"
            params.append(weather)

        query += " ORDER BY date_time DESC LIMIT ?"
        params.append(limit)

        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_sqlite_summary(db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Executes aggregation queries directly using SQL.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                ROUND(AVG(traffic_volume), 2) as avg_volume,
                MIN(traffic_volume) as min_volume,
                MAX(traffic_volume) as max_volume,
                COUNT(DISTINCT weather_main) as distinct_weather_types
            FROM metro_traffic
        """)
        row = cursor.fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()
