# Phase C — Backend Schema Fix Plan
Status: NOT STARTED. Written 2026-08-23. Read this before touching backend/app/{models,schemas,routers}.

## The problem, in one sentence
Two competing designs exist for how the API talks to the database. One is REAL
and WORKING (used by ingestion scripts, standardization scripts, gdp.py,
unemployment.py). The other is OLDER, BROKEN, and currently unused — but still
sitting in the codebase, unfixed.

## Proof this is real, not theoretical
Live database, confirmed via direct SQL queries this project:
- `metrics` table: primary key `metric_id` (UUID), column `domain_id` (UUID,
  foreign key to `domains` table), column `slug` (text).
- Data is split across three separate tables: `raw_observations`,
  `standardized_observations`, `missing_data_records` — NOT one table.
- `standardized_observations` has a column `confidence_tier` (a fixed set of 7
  text values: OFFICIAL_MEASUREMENT, ADMINISTRATIVE_RECORD, SURVEY_ESTIMATE,
  HISTORICAL_RECONSTRUCTION, ACADEMIC_ESTIMATE, MODELED_DERIVED, UNKNOWN).

The OLD, BROKEN backend code (never fixed, still in the repo, NOT currently
loaded by main.py) expects something different:
- `backend/app/models/metric.py` — expects `id` (plain number), `dataset_id`
  (number), `metric_id_code` (text), `domain` (plain text column, not a link
  to a separate domains table).
- `backend/app/models/observation.py` — expects ONE table called `observations`
  with a single `confidence` column and an `is_raw` true/false flag, instead of
  three separate tables.
- `backend/app/schemas/metric.py`, `backend/app/schemas/observation.py` — match
  the wrong shape above.
- `backend/app/routers/metrics.py`, `backend/app/routers/observations.py` —
  would error immediately if used, because they query columns/tables that do
  not exist in the real database.

These 6 files currently sit unused — `main.py` does NOT import them. Not
deleted, per project owner's explicit instruction: fix permanently, don't
delete.

## What's temporarily working around this (also needs cleanup)
`backend/app/routers/gdp.py` and `backend/app/routers/unemployment.py` — each
is a hand-written, one-off file querying the correct real tables directly with
raw SQL. This works but doesn't scale: every new metric currently means a new
router file + a new frontend chart file. Two exist so far; this does not scale
to 100+ metrics per the Data Dictionary.

## The permanent fix — two parts

### Part A: Rebuild models/schemas to match the REAL schema
Replace (not delete — same filenames, new correct content):

**`backend/app/models/metric.py`** should map to the real `metrics` table:
- `metric_id` (UUID, primary key)
- `domain_id` (UUID, foreign key -> `domains.domain_id`)
- `slug`, `name`, `short_name`, `definition`, `units`, `currency_code`,
  `inflation_basis_year`, `geographic_scope`, `default_cadence`, `methodology`,
  `known_limitations`, `first_available_date`, `last_available_date`,
  `is_monetary`, `is_active`, `created_at`, `updated_at`
- Relationship to a new `Domain` model (see below)

**`backend/app/models/observation.py`** should become THREE models, not one:
- `RawObservation` -> maps to `raw_observations` table (immutable — no update
  method should exist on this model, per ADR-002)
- `StandardizedObservation` -> maps to `standardized_observations` table,
  includes `confidence_tier` (use the same enum values as the DB: 7 tiers)
- `MissingDataRecord` -> maps to `missing_data_records` table

**New file: `backend/app/models/domain.py`** — maps to the `domains` table
(currently has no model at all). Needed since `metrics.domain_id` is a real
foreign key to it.

**`backend/app/schemas/metric.py`, `backend/app/schemas/observation.py`** —
rewrite the Pydantic response shapes to match the corrected models above
(mirror the JSON shape already proven working in `gdp.py`'s hand-written
response — that shape is a good template, since it's tested and confirmed
correct).

### Part B: One reusable endpoint instead of one-off files per metric
Replace `gdp.py` and `unemployment.py` with a single generic endpoint:

```
GET /api/v1/observations?metric=gdp_nominal
GET /api/v1/observations?metric=unemployment_rate
```

Design: same query logic as `gdp.py`/`unemployment.py` today, but the metric
slug becomes a parameter instead of being hardcoded per file. Once this exists
and is tested against BOTH gdp_nominal and unemployment_rate (must match the
old one-off endpoints' output exactly before deleting them), `gdp.py` and
`unemployment.py` can be safely removed.

### Frontend equivalent
Replace `GdpChart.tsx` and `UnemploymentChart.tsx` with one
`MetricChart.tsx` component that takes a metric slug + display name + line
color/style as props, fetches from the new generic endpoint, and renders.
Confidence-tier-to-line-style mapping (solid/dashed/dotted) should be looked
up from `ConfidenceBadge.tsx`'s existing `TIER_META` — don't duplicate that
mapping a third time.

## Suggested order of work (don't skip steps or test at the end only)
1. Write `models/domain.py` (new). Test: can query all 10 domains via SQLAlchemy.
2. Rewrite `models/metric.py`. Test: can query the 2 existing metrics
   (gdp_nominal, unemployment_rate) via SQLAlchemy, values match what raw SQL
   returns.
3. Rewrite `models/observation.py` as three models. Test each against real
   data (318 GDP standardized rows, 4 GDP missing rows, etc. — exact counts
   must match what direct SQL queries already confirmed in this project).
4. Rewrite the two schema files. Test: FastAPI can serialize a query result
   without errors.
5. Build the ONE generic `/api/v1/observations?metric=` endpoint. Test: output
   for `?metric=gdp_nominal` matches `gdp.py`'s current output byte-for-byte
   (same observations, same missing records, same confidence tiers).
6. Only after step 5 passes: delete `gdp.py`, `unemployment.py`, wire the
   generic endpoint into `main.py` instead.
7. Build `MetricChart.tsx`, confirm it renders identically to the two old
   chart components, then delete `GdpChart.tsx`/`UnemploymentChart.tsx`.
8. Old `routers/metrics.py` and `routers/observations.py` — decide if still
   needed given the new generic endpoint covers their purpose, or retire them
   too (discuss with project owner before deleting — same "fix, don't delete
   without asking" rule as everything else in this project).

## Ground truth references (don't guess at table structure — check these)
- Canonical schema: `data_schema.txt` in project docs (also
  `backend/db/schema/initial.sql` in the repo) — sections 10 (metrics),
  11 (raw_observations), 13 (standardized_observations, derived_observations),
  14 (missing_data_records).
- Confirm current live structure directly if in doubt:
  `docker exec -it ustp_postgres psql -U ustp -d ustp_dev -c "\d metrics"`
  (repeat for any table name to see its real, current columns)
