"""
Standalone FRED ingestion test script.

What this does, step by step:
1. Reads DATABASE_URL and FRED_API_KEY from backend/.env
2. Calls the real FRED API for the GDP series (series_id = "GDP", nominal GDP,
   billions of dollars — matches source-registry.yaml's fred_gdp dataset)
3. Registers the source/dataset/series in the database if not already there
   (safe to run more than once — won't create duplicate source/dataset rows)
4. Records one ingestion_event for this run
5. Stores the raw API response as one raw_artifact (never modified again)
6. Stores each data point as one row in raw_observations (immutable, per
   ADR-002 — this script only ever INSERTs into raw tables, never UPDATEs)

This does NOT do standardization or confidence-tier assignment yet — that's
the next step after this one is confirmed working. This script only proves
the ingestion pipeline (fetch -> raw storage -> provenance) works end to end.

Run from the backend/ folder:
    python test_fred_ingestion.py
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import requests


def load_env(env_path: str = ".env") -> dict:
    """Minimal .env reader — avoids requiring python-dotenv as a dependency."""
    values = {}
    path = Path(env_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {env_path}. Run this script from the backend/ folder."
        )
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def fetch_fred_gdp(api_key: str) -> dict:
    """Fetch the GDP series from FRED's public API."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "GDP",
        "api_key": api_key,
        "file_type": "json",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "observations" not in data:
        raise RuntimeError(f"Unexpected FRED response, no 'observations' key: {data}")
    return data


def get_or_create_source(cur) -> str:
    cur.execute(
        "SELECT source_id FROM sources WHERE name = %s AND agency_name = %s",
        ("FRED", "Federal Reserve Bank of St. Louis"),
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO sources (name, agency_name, agency_level, homepage_url,
                              api_base_url, priority_rank, is_authoritative)
        VALUES (%s, %s, 'FEDERAL', %s, %s, 1, TRUE)
        RETURNING source_id
        """,
        (
            "FRED",
            "Federal Reserve Bank of St. Louis",
            "https://fred.stlouisfed.org",
            "https://api.stlouisfed.org/fred",
        ),
    )
    return cur.fetchone()[0]


def get_or_create_dataset(cur, source_id: str) -> str:
    cur.execute("SELECT dataset_id FROM datasets WHERE slug = %s", ("fred_gdp",))
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO datasets (source_id, slug, name, description, cadence,
                               retrieval_method, lifecycle_state)
        VALUES (%s, %s, %s, %s, 'QUARTERLY', 'API', 'RETRIEVED')
        RETURNING dataset_id
        """,
        (
            source_id,
            "fred_gdp",
            "Gross Domestic Product",
            "Aggregated GDP series from BEA via FRED",
        ),
    )
    return cur.fetchone()[0]


def get_or_create_dataset_version(cur, dataset_id: str) -> str:
    cur.execute(
        "SELECT dataset_version_id FROM dataset_versions WHERE dataset_id = %s AND is_current = TRUE",
        (dataset_id,),
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO dataset_versions (dataset_id, source_version_label, is_current)
        VALUES (%s, %s, TRUE)
        RETURNING dataset_version_id
        """,
        (dataset_id, "v1"),
    )
    return cur.fetchone()[0]


def get_or_create_dataset_series(cur, dataset_id: str) -> str:
    cur.execute(
        "SELECT dataset_series_id FROM dataset_series WHERE dataset_id = %s AND series_code = %s",
        (dataset_id, "GDP"),
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO dataset_series (dataset_id, series_code, series_name, units, cadence)
        VALUES (%s, %s, %s, %s, 'QUARTERLY')
        RETURNING dataset_series_id
        """,
        (dataset_id, "GDP", "Gross Domestic Product (billions of dollars)", "billions_of_dollars"),
    )
    return cur.fetchone()[0]


def record_ingestion_event(cur, dataset_version_id: str, row_count: int, checksum: str) -> str:
    cur.execute(
        """
        INSERT INTO ingestion_events (dataset_version_id, retrieval_method, retrieved_at,
                                       initiated_by, source_http_status, source_checksum,
                                       row_count, status)
        VALUES (%s, 'API', %s, 'test_fred_ingestion.py', 200, %s, %s, 'SUCCESS')
        RETURNING ingestion_event_id
        """,
        (dataset_version_id, datetime.now(timezone.utc), checksum, row_count),
    )
    return cur.fetchone()[0]


def store_raw_artifact(cur, ingestion_event_id: str, raw_json: dict, checksum: str) -> str:
    raw_bytes = json.dumps(raw_json).encode("utf-8")
    cur.execute(
        """
        INSERT INTO raw_artifacts (ingestion_event_id, artifact_name, artifact_storage_type,
                                    storage_uri, mime_type, file_size_bytes, checksum_sha256,
                                    artifact_metadata)
        VALUES (%s, %s, 'INLINE_JSON', %s, 'application/json', %s, %s, %s)
        RETURNING raw_artifact_id
        """,
        (
            ingestion_event_id,
            "fred_gdp_observations.json",
            f"inline://fred_gdp/{ingestion_event_id}",
            len(raw_bytes),
            checksum,
            json.dumps({"source": "FRED", "series_id": "GDP"}),
        ),
    )
    return cur.fetchone()[0]


def store_raw_observations(cur, raw_artifact_id: str, dataset_series_id: str, observations: list) -> int:
    inserted = 0
    for i, obs in enumerate(observations):
        raw_value_text = obs.get("value")
        raw_value_numeric = None
        if raw_value_text not in (None, ".", ""):
            try:
                raw_value_numeric = float(raw_value_text)
            except ValueError:
                raw_value_numeric = None  # FRED uses "." for missing data points

        cur.execute(
            """
            INSERT INTO raw_observations (raw_artifact_id, dataset_series_id, observation_key,
                                           raw_date, raw_value_text, raw_value_numeric,
                                           raw_units, raw_record, row_number_in_artifact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                raw_artifact_id,
                dataset_series_id,
                f"GDP_{obs.get('date')}",
                obs.get("date"),
                raw_value_text,
                raw_value_numeric,
                "billions_of_dollars",
                json.dumps(obs),
                i,
            ),
        )
        inserted += 1
    return inserted


def main():
    env = load_env(".env")

    database_url = env.get("DATABASE_URL")
    fred_api_key = env.get("FRED_API_KEY")

    if not database_url:
        print("ERROR: DATABASE_URL not found in .env")
        sys.exit(1)
    if not fred_api_key:
        print("ERROR: FRED_API_KEY not found in .env")
        sys.exit(1)

    print("Step 1: Fetching GDP data from FRED...")
    raw_json = fetch_fred_gdp(fred_api_key)
    observations = raw_json["observations"]
    checksum = hashlib.sha256(json.dumps(raw_json).encode("utf-8")).hexdigest()
    print(f"  Got {len(observations)} observations. Checksum: {checksum[:16]}...")

    print("Step 2: Connecting to database...")
    # psycopg accepts postgresql:// or postgresql+psycopg:// — strip the +psycopg part if present
    conn_str = database_url.replace("postgresql+psycopg://", "postgresql://")
    conn = psycopg.connect(conn_str)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            print("Step 3: Registering source/dataset/series (skips if already present)...")
            source_id = get_or_create_source(cur)
            dataset_id = get_or_create_dataset(cur, source_id)
            dataset_version_id = get_or_create_dataset_version(cur, dataset_id)
            dataset_series_id = get_or_create_dataset_series(cur, dataset_id)
            print(f"  source_id={source_id}")
            print(f"  dataset_id={dataset_id}")
            print(f"  dataset_series_id={dataset_series_id}")

            print("Step 4: Recording ingestion event...")
            ingestion_event_id = record_ingestion_event(
                cur, dataset_version_id, len(observations), checksum
            )
            print(f"  ingestion_event_id={ingestion_event_id}")

            print("Step 5: Storing raw artifact (the full API response, untouched)...")
            raw_artifact_id = store_raw_artifact(cur, ingestion_event_id, raw_json, checksum)
            print(f"  raw_artifact_id={raw_artifact_id}")

            print("Step 6: Storing raw observations (immutable, one row per data point)...")
            count = store_raw_observations(cur, raw_artifact_id, dataset_series_id, observations)
            print(f"  Inserted {count} raw_observations rows")

        conn.commit()
        print("\nSUCCESS. All changes committed.")
        print(f"Run this to see the data yourself:")
        print(
            f"  docker exec -it ustp_postgres psql -U ustp -d ustp_dev -c "
            f"\"SELECT raw_date, raw_value_text FROM raw_observations "
            f"ORDER BY raw_date DESC LIMIT 5;\""
        )
    except Exception:
        conn.rollback()
        print("\nFAILED. Rolled back — no partial data was saved.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()