"""
Seed `metrics` and `transformation_scripts` from version-controlled sources.

WHY THIS EXISTS
---------------
`alembic upgrade head` builds the schema and seeds domains, licences and
confidence-tier definitions. It does NOT seed `metrics` or
`transformation_scripts`. Those rows were previously created by hand, which
meant a clean clone of this repository could not produce a working database:
the ingestion and standardization scripts both fail immediately without them.

    RuntimeError: Metric 'gdp_nominal' not found.
    RuntimeError: Transformation script 'standardize_fred_gdp' not found.

This script closes that gap. Metric definitions are read from the approved
Phase A data dictionary (docs/phase-a/data-dictionary.yaml), which is the
canonical source of truth per ADR-006 — they are not duplicated here.

DETERMINISTIC IDs
-----------------
metric_id is derived from the metric slug with UUID v5, not generated randomly.
The same slug therefore produces the same UUID on every machine, so two
independently built databases remain comparable and reconcilable. Do not change
NAMESPACE — doing so renames every metric_id in existence.

IDEMPOTENT
----------
Safe to re-run. Existing rows are left untouched (ON CONFLICT DO NOTHING),
matching the pattern used by the ingestion and standardization scripts. It never
updates or deletes anything.

Run from the backend/ folder, with the database already migrated:

    python seed_from_data_dictionary.py
"""

import hashlib
import os
import sys
import uuid
from pathlib import Path

import psycopg
import yaml

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ustp:ustp_dev_password@localhost:5432/ustp_dev",
)

DATA_DICTIONARY = Path(__file__).parent.parent / "docs" / "phase-a" / "data-dictionary.yaml"

# Stable namespace for deterministic metric UUIDs. NEVER change this value.
NAMESPACE = uuid.UUID("6f9619ff-8b86-d011-b42d-00c04fc964ff")

# The dictionary's own worked example in section 2, not a real metric.
TEMPLATE_SLUGS = {"metric_slug"}

VALID_CADENCES = {
    "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "ANNUAL", "BIENNIAL",
    "TRIENNIAL", "QUINQUENNIAL", "DECENNIAL", "IRREGULAR", "EVENT_BASED",
}

# Slugs the transformation scripts hard-code. Checked after seeding so a
# mismatch surfaces loudly here rather than as a RuntimeError mid-ingestion.
SLUGS_REQUIRED_BY_CODE = ["gdp_nominal", "unemployment_rate"]

TRANSFORMATION_SCRIPTS = [
    {
        "name": "standardize_fred_gdp",
        "version": "1.0.0",
        "script_path": "app/transformations/standardize_fred_gdp.py",
        "run_type": "STANDARDIZATION",
        "description": "Standardizes raw FRED GDP observations into "
                       "standardized_observations and missing_data_records.",
        "methodology_notes": "FRED reports missing quarters as '.'; those become "
                             "explicit missing_data_records, never zero or "
                             "interpolated (PRD FR-7, ADR-005).",
    },
    {
        "name": "standardize_fred_unemployment",
        "version": "1.0.0",
        "script_path": "app/transformations/standardize_fred_unemployment.py",
        "run_type": "STANDARDIZATION",
        "description": "Standardizes raw FRED UNRATE observations into "
                       "standardized_observations and missing_data_records.",
        "methodology_notes": "Tagged SURVEY_ESTIMATE rather than "
                             "OFFICIAL_MEASUREMENT: UNRATE derives from the "
                             "Current Population Survey, a sample.",
    },
]


def metric_uuid(slug: str) -> uuid.UUID:
    """Derive a stable metric_id from the slug (see DETERMINISTIC IDs above)."""
    return uuid.uuid5(NAMESPACE, slug)


def as_text(value) -> str | None:
    """Flatten YAML scalars/lists into a single text column value."""
    if value is None:
        return None
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return str(value).strip() or None


def extract_metric_blocks(path: Path) -> list[dict]:
    """
    Pull `metric:` blocks out of the data dictionary.

    The dictionary is a prose document with embedded YAML blocks, not a single
    YAML file, so it cannot be parsed whole. A block starts at a non-indented
    `metric:` line and runs until prose resumes at column 0.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    metrics, i = [], 0

    while i < len(lines):
        if lines[i].strip() == "metric:" and not lines[i].startswith((" ", "\t")):
            body, i = [], i + 1
            while i < len(lines):
                line = lines[i]
                if line.strip() == "" or line.startswith((" ", "\t")):
                    body.append(line)
                    i += 1
                    continue
                break
            try:
                parsed = yaml.safe_load("\n".join(body))
            except yaml.YAMLError as exc:
                raise SystemExit(
                    f"Could not parse a metric block in {path.name}: {exc}\n"
                    "Fix the YAML in the data dictionary and re-run."
                ) from exc
            if isinstance(parsed, dict) and parsed.get("schema_id"):
                metrics.append(parsed)
        else:
            i += 1

    return metrics


def seed_metrics(cur, metrics: list[dict]) -> tuple[int, int, list[str]]:
    cur.execute("SELECT slug, domain_id FROM domains")
    domains = {slug: domain_id for slug, domain_id in cur.fetchall()}

    inserted = skipped = 0
    warnings: list[str] = []

    for m in metrics:
        slug = m["schema_id"]
        if slug in TEMPLATE_SLUGS:
            continue

        domain_slug = m.get("domain")
        if domain_slug not in domains:
            warnings.append(f"{slug}: unknown domain '{domain_slug}' - skipped")
            continue

        cadence = m.get("cadence")
        if cadence not in VALID_CADENCES:
            if cadence:
                warnings.append(f"{slug}: unrecognised cadence '{cadence}' - stored as NULL")
            cadence = None

        cur.execute(
            """
            INSERT INTO metrics (
                metric_id, domain_id, slug, name, short_name, definition,
                units, currency_code, inflation_basis_year, geographic_scope,
                default_cadence, methodology, known_limitations,
                is_monetary, requires_real_and_nominal_display
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            """,
            (
                metric_uuid(slug),
                domains[domain_slug],
                slug,
                as_text(m.get("name")) or slug,
                as_text(m.get("short_name")),
                as_text(m.get("definition")) or "(definition pending)",
                as_text(m.get("units")),
                as_text(m.get("currency_code")),
                m.get("inflation_basis_year"),
                as_text(m.get("geographic_scope")) or "US_NATIONAL",
                cadence,
                as_text(m.get("methodology")),
                as_text(m.get("known_limitations")),
                bool(m.get("is_monetary", False)),
                bool(m.get("requires_real_and_nominal_display", False)),
            ),
        )
        if cur.rowcount:
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped, warnings


def seed_transformation_scripts(cur, backend_dir: Path) -> tuple[int, int, list[str]]:
    inserted = skipped = 0
    warnings: list[str] = []

    for script in TRANSFORMATION_SCRIPTS:
        path = backend_dir / script["script_path"]
        if not path.exists():
            warnings.append(f"{script['name']}: {script['script_path']} not found - skipped")
            continue

        # script_hash is NOT NULL and exists so a run can be tied to the exact
        # code that produced it (ADR-004). Hash the real file, never a stub.
        script_hash = hashlib.sha256(path.read_bytes()).hexdigest()

        cur.execute(
            """
            INSERT INTO transformation_scripts (
                transformation_script_id, name, version, script_path,
                script_hash, run_type, description, methodology_notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name, version) DO NOTHING
            """,
            (
                uuid.uuid5(NAMESPACE, f"{script['name']}@{script['version']}"),
                script["name"],
                script["version"],
                script["script_path"],
                script_hash,
                script["run_type"],
                script["description"],
                script["methodology_notes"],
            ),
        )
        if cur.rowcount:
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped, warnings


def main() -> int:
    backend_dir = Path(__file__).parent

    if not DATA_DICTIONARY.exists():
        print(f"ERROR: data dictionary not found at {DATA_DICTIONARY}")
        return 1

    metrics = extract_metric_blocks(DATA_DICTIONARY)
    print(f"Read {len(metrics)} metric definitions from {DATA_DICTIONARY.name}")

    conn = psycopg.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        m_inserted, m_skipped, m_warnings = seed_metrics(cur, metrics)
        t_inserted, t_skipped, t_warnings = seed_transformation_scripts(cur, backend_dir)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pass

    print(f"metrics:               {m_inserted} inserted, {m_skipped} already present")
    print(f"transformation_scripts: {t_inserted} inserted, {t_skipped} already present")

    for warning in m_warnings + t_warnings:
        print(f"  WARNING: {warning}")

    # Fail loudly if the slugs the code depends on are absent, rather than
    # letting ingestion blow up later with a bare RuntimeError.
    cur.execute(
        "SELECT slug FROM metrics WHERE slug = ANY(%s)", (SLUGS_REQUIRED_BY_CODE,)
    )
    present = {row[0] for row in cur.fetchall()}
    missing = [slug for slug in SLUGS_REQUIRED_BY_CODE if slug not in present]

    cur.close()
    conn.close()

    if missing:
        print()
        print("  ATTENTION - slugs referenced by the transformation scripts are")
        print("  not in the data dictionary, so ingestion will still fail:")
        for slug in missing:
            print(f"    - {slug}")
        print("  Resolve the naming mismatch between the dictionary and the")
        print("  scripts before running ingestion.")
        return 2

    print("\nAll slugs required by the transformation scripts are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
