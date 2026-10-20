"""
RoadCast — Main Application Runner
Executes prerequisite data pipeline steps if needed and starts the unified FastAPI server.
Usage:
    python run.py
"""

import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "Metro_Interstate_Traffic_Volume.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "metro_traffic_processed.csv")
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "models", "traffic_model.joblib")


def ensure_pipeline():
    """Checks and runs prerequisite data ingestion, cleaning, and model training if not present."""
    if not os.path.exists(RAW_DATA_PATH):
        print("[RoadCast] Downloading raw UCI dataset...")
        from app.ingestion.ingest import ingest_dataset
        ingest_dataset()

    if not os.path.exists(PROCESSED_DATA_PATH):
        print("[RoadCast] Cleaning and preprocessing dataset...")
        from app.transformation.cleaner import clean_and_transform
        clean_and_transform()

    if not os.path.exists(MODEL_PATH):
        print("[RoadCast] Training baseline and ML models...")
        from app.models.train_evaluate import train_and_evaluate
        train_and_evaluate()


if __name__ == "__main__":
    ensure_pipeline()
    print("\n" + "=" * 60)
    print("  RoadCast — Historical Traffic Intelligence Workspace")
    print("  Server launching at: http://127.0.0.1:8000")
    print("  Interactive API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
