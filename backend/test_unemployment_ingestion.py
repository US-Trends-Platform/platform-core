"""
FRED ingestion script for Unemployment Rate (series UNRATE).
Same pattern as test_fred_ingestion.py — raw storage only, immutable.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import requests


def load_env(env_path: str = ".env") -> dict:
    values = {}
    path = Path(env_path)
    if not path.exists():
        raise FileNotFoundError(f"Could not find {env_path}. Run from backend/ folder.")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def fetch_fred_series(api_key: str, series_id: str) -> dict:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "observations" not in data:
        raise RuntimeError(f"Unexpected FRED response: {data}")
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
        ("FRED", "Federal Reserve Bank of St. Louis", "https://fred.stlouisfed.org", "https://api.stlouisfed.org/fred"),
    )
    return cur.fetchone()[0]


def get_or_create_dataset(cur, source_id: str) -> str:
    cur.execute("SELECT dataset_id FROM datasets WHERE slug = %s", ("fred_unemployment",))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        INSERT INTO datasets (source_id, slug, name, description, cadence,
                               retrieval_method, lifecycle_state)
        VALUES (%s, %s, %s, %s, 'MONTHLY', 'API', 'RETRIEVED')
        RETURNING dataset_id
        """,
        (source_id, "fred_unemployment", "Unemployment Rate", "Civilian unemployment rate, seasonally adjusted, via FRED (originally BLS CPS)"),
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
        "INSERT INTO dataset_versions (dataset_id, source_version_label, is_current) VALUES (%s, %s, TRUE) RETURNING dataset_version_id",
        (dataset_id, "v1"),
    )
    return cur.fetchone()[0]


def get_or_create_dataset_series(cur, dataset_id: str) -> str:
    cur.execute(
        "SELECT dataset_series_id FROM dataset_series WHERE dataset_id = %s AND series_code = %s",
        (dataset_id, "UNRATE"),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        INSERT INTO dataset_series (dataset_id, series_code, series_name, units, cadence)
        VALUES (%s, %s, %s, %s, 'MONTHLY')
        RETURNING dataset_series_id
        """,
        (dataset_id, "UNRATE", "Unemployment Rate", "percent"),
    )
    return cur.fetchone()[0]


def record_ingestion_event(cur, dataset_version_id: str, row_count: int, checksum: str) -> str:
    cur.execute(
        """
        INSERT INTO ingestion_events (dataset_version_id, retrieval_method, retrieved_at,
                                       initiated_by, source_http_status, source_checksum,
                                       row_count, status)
        VALUES (%s, 'API', %s, 'ingest_unemployment.py', 200, %s, %s, 'SUCCESS')
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
            ingestion_event_id, "fred_unemployment_observations.json",
            f"inline://fred_unemployment/{ingestion_event_id}", len(raw_bytes), checksum,
            json.dumps({"source": "FRED", "series_id": "UNRATE"}),
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
                raw_value_numeric = None
        cur.execute(
            """
            INSERT INTO raw_observations (raw_artifact_id, dataset_series_id, observation_key,
                                           raw_date, raw_value_text, raw_value_numeric,
                                           raw_units, raw_record, row_number_in_artifact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (raw_artifact_id, dataset_series_id, f"UNRATE_{obs.get('date')}", obs.get("date"),
             raw_value_text, raw_value_numeric, "percent", json.dumps(obs), i),
        )
        inserted += 1
    return inserted


def main():
    env = load_env(".env")
    database_url = env.get("DATABASE_URL")
    fred_api_key = env.get("FRED_API_KEY")

    if not database_url or not fred_api_key:
        print("ERROR: DATABASE_URL or FRED_API_KEY missing from .env")
        sys.exit(1)

    print("Step 1: Fetching Unemployment Rate (UNRATE) from FRED...")
    raw_json = fetch_fred_series(fred_api_key, "UNRATE")
    observations = raw_json["observations"]
    checksum = hashlib.sha256(json.dumps(raw_json).encode("utf-8")).hexdigest()
    print(f"  Got {len(observations)} observations. Checksum: {checksum[:16]}...")

    conn_str = database_url.replace("postgresql+psycopg://", "postgresql://")
    conn = psycopg.connect(conn_str)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            print("Step 2: Registering source/dataset/series...")
            source_id = get_or_create_source(cur)
            dataset_id = get_or_create_dataset(cur, source_id)
            dataset_version_id = get_or_create_dataset_version(cur, dataset_id)
            dataset_series_id = get_or_create_dataset_series(cur, dataset_id)

            print("Step 3: Recording ingestion event...")
            ingestion_event_id = record_ingestion_event(cur, dataset_version_id, len(observations), checksum)

            print("Step 4: Storing raw artifact...")
            raw_artifact_id = store_raw_artifact(cur, ingestion_event_id, raw_json, checksum)

            print("Step 5: Storing raw observations...")
            count = store_raw_observations(cur, raw_artifact_id, dataset_series_id, observations)
            print(f"  Inserted {count} raw_observations rows")

        conn.commit()
        print("\nSUCCESS.")
    except Exception:
        conn.rollback()
        print("\nFAILED. Rolled back.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
