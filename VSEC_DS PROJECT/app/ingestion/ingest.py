"""
Ingestion module for RoadCast.
Downloads and caches the official UCI Metro Interstate Traffic Volume dataset,
computes cryptographic checksums, preserves the untouched source copy,
and captures ingestion provenance metadata.
"""

import os
import hashlib
import json
import urllib.request
import zipfile
import gzip
import io
import datetime
import pandas as pd

UCI_DATASET_URL = "https://archive.ics.uci.edu/static/public/492/metro+interstate+traffic+volume.zip"
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
METADATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "metadata")


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def ingest_dataset(force_download: bool = False) -> dict:
    """
    Downloads and extracts raw UCI Metro Interstate Traffic Volume dataset
    into data/raw/ if not already present.
    Returns ingestion report.
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)

    raw_csv_path = os.path.join(RAW_DIR, "Metro_Interstate_Traffic_Volume.csv")
    raw_meta_path = os.path.join(RAW_DIR, "ingestion_metadata.json")

    if os.path.exists(raw_csv_path) and not force_download:
        print(f"Raw dataset already exists at: {raw_csv_path}")
        with open(raw_meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Downloading dataset from: {UCI_DATASET_URL}...")
    req = urllib.request.Request(UCI_DATASET_URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        zip_bytes = resp.read()

    print("Extracting gzip CSV from zip...")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        # Locate the gz file
        gz_filename = [n for n in z.namelist() if n.endswith(".csv.gz")][0]
        with gzip.open(z.open(gz_filename), "rb") as gz_in:
            csv_content = gz_in.read()

    with open(raw_csv_path, "wb") as f_out:
        f_out.write(csv_content)

    sha256 = compute_sha256(raw_csv_path)
    file_size_bytes = os.path.getsize(raw_csv_path)

    # Inspect schema
    df_preview = pd.read_csv(raw_csv_path)
    row_count = int(len(df_preview))
    col_count = int(len(df_preview.columns))

    ingestion_report = {
        "dataset_name": "Metro Interstate Traffic Volume",
        "source_url": UCI_DATASET_URL,
        "retrieval_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "storage_path": os.path.relpath(raw_csv_path),
        "file_size_bytes": file_size_bytes,
        "sha256_checksum": sha256,
        "row_count": row_count,
        "column_count": col_count,
        "columns": list(df_preview.columns),
        "data_types": {col: str(dtype) for col, dtype in df_preview.dtypes.items()},
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "citation": "Hogue, John. (2019). Metro Interstate Traffic Volume. UCI Machine Learning Repository. https://doi.org/10.24432/C56S30.",
        "geographic_coverage": "Westbound I-94 between Minneapolis and St. Paul, MN, USA (Station 301)",
        "temporal_coverage": {
            "start": str(df_preview["date_time"].min()),
            "end": str(df_preview["date_time"].max())
        },
        "sampling_frequency": "Hourly",
        "is_synthetic": False
    }

    with open(raw_meta_path, "w", encoding="utf-8") as f:
        json.dump(ingestion_report, f, indent=2)

    print(f"Ingestion complete: {row_count} rows, {col_count} columns. SHA256: {sha256[:12]}...")
    return ingestion_report


if __name__ == "__main__":
    report = ingest_dataset()
    print(json.dumps(report, indent=2))
