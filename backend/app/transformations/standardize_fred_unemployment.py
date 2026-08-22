"""
Standardization: FRED raw Unemployment Rate observations -> standardized_observations
Never touches raw_observations. Safe to re-run.
"""
import os
import psycopg
from datetime import datetime, timezone

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://ustp:ustp_dev_password@localhost:5432/ustp_dev")
TRANSFORMATION_SCRIPT_NAME = "standardize_fred_unemployment"
METRIC_SLUG = "unemployment_rate"
DATASET_SLUG = "fred_unemployment"


def main():
    conn = psycopg.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("SELECT metric_id FROM metrics WHERE slug = %s", (METRIC_SLUG,))
    metric_id = cur.fetchone()[0]

    cur.execute("SELECT transformation_script_id FROM transformation_scripts WHERE name = %s", (TRANSFORMATION_SCRIPT_NAME,))
    transformation_script_id = cur.fetchone()[0]

    cur.execute("SELECT dataset_id FROM datasets WHERE slug = %s", (DATASET_SLUG,))
    dataset_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO transformation_runs (transformation_script_id, input_scope, started_at, status) VALUES (%s, %s, %s, 'RUNNING') RETURNING transformation_run_id",
        (transformation_script_id, f"dataset:{DATASET_SLUG}", datetime.now(timezone.utc)),
    )
    transformation_run_id = cur.fetchone()[0]

    cur.execute(
        """
        SELECT ro.raw_observation_id, ro.dataset_series_id, ro.raw_date, ro.raw_value_numeric, ro.raw_units
        FROM raw_observations ro
        JOIN dataset_series ds ON ro.dataset_series_id = ds.dataset_series_id
        WHERE ds.dataset_id = %s
        ORDER BY ro.raw_date
        """,
        (dataset_id,),
    )
    raw_rows = cur.fetchall()

    standardized_count = 0
    missing_count = 0
    skipped_count = 0

    for raw_observation_id, dataset_series_id, raw_date, raw_value_numeric, raw_units in raw_rows:
        cur.execute("SELECT 1 FROM standardized_observations WHERE raw_observation_id = %s", (raw_observation_id,))
        if cur.fetchone():
            skipped_count += 1
            continue
        cur.execute("SELECT 1 FROM missing_data_records WHERE metric_id = %s AND observation_date = %s", (metric_id, raw_date))
        if cur.fetchone():
            skipped_count += 1
            continue

        if raw_value_numeric is not None:
            cur.execute(
                """
                INSERT INTO standardized_observations
                    (raw_observation_id, metric_id, dataset_series_id, transformation_run_id,
                     observation_date, standardized_value, units, confidence_tier, approval_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'SURVEY_ESTIMATE', 'APPROVED')
                """,
                (raw_observation_id, metric_id, dataset_series_id, transformation_run_id, raw_date, raw_value_numeric, raw_units),
            )
            standardized_count += 1
        else:
            cur.execute(
                """
                INSERT INTO missing_data_records (metric_id, dataset_series_id, observation_date, missing_data_reason, explanation)
                VALUES (%s, %s, %s, 'HISTORICAL_DATA_UNAVAILABLE', %s)
                """,
                (metric_id, dataset_series_id, raw_date, "No value reported by FRED for this date."),
            )
            missing_count += 1

    cur.execute("UPDATE transformation_runs SET completed_at = %s, status = 'SUCCESS' WHERE transformation_run_id = %s", (datetime.now(timezone.utc), transformation_run_id))
    conn.commit()
    cur.close()
    conn.close()

    print(f"Standardized: {standardized_count}")
    print(f"Missing data records: {missing_count}")
    print(f"Skipped (already done): {skipped_count}")


if __name__ == "__main__":
    main()
