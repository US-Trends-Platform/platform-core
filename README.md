# U.S. Socioeconomic, Political & Agricultural Trends Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Repo](https://img.shields.io/badge/GitHub-US--Trends--Platform%2Fplatform--core-blue)](https://github.com/US-Trends-Platform/platform-core)

A research-grade, open-source platform documenting American socioeconomic, political, and agricultural trends from 1776 to the present.

## Overview

This platform enables researchers, educators, journalists, and the general public to:

- **Explore authoritative historical data** from federal sources (Census, BLS, USDA, FRED, etc.)
- **Understand data provenance** — trace every number back to its source
- **Access complete methodology** — transparent about how data is collected and processed
- **Compare historical periods** without causal assumptions
- **Generate academic citations** in APA, MLA, Chicago, BibTeX formats
- **Download data** in open formats (CSV, JSON, Parquet)

## Core Principles

- **Evidence before interpretation** — raw observations never fabricated
- **Sources before claims** — complete provenance chain preserved
- **Raw observations before analytics** — derived metrics clearly labeled
- **Transparency before convenience** — no hidden data cleaning
- **Uncertainty before false precision** — confidence tiers on every observation

## Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy, Pydantic v2 | REST API, data ingestion, validation |
| **Database** | PostgreSQL, DuckDB | Immutable raw storage, analytics engine |
| **Frontend** | Next.js, React, TypeScript, TailwindCSS | Interactive timeline, charts, accessibility |
| **Visualization** | Apache ECharts, D3.js | Time-series, confidence tier indicators |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Containerization, CI/CD, testing |

## Phase 1 Scope

### Domains (10)

1. Demographics
2. Employment
3. Economy
4. Inflation & Cost of Living
5. Healthcare
6. Education
7. Politics & Government
8. Immigration
9. Agriculture & Farming
10. Historical Events & Legislation

### Coverage

- **Geographic:** U.S. national/federal level
- **Temporal:** 1776–present (some metrics from 1840s for agriculture)
- **Metrics:** 100+ core indicators planned; 31 defined in the Data Dictionary
- **Sources:** 15+ authoritative federal agencies

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- Docker Desktop (for PostgreSQL)

### 1. Start PostgreSQL

```bash
cd backend
docker compose up -d
```

This starts PostgreSQL 16 on port 5432 (database `ustp_dev`, user `ustp`).

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
```

Then edit `backend/.env` and set your `FRED_API_KEY` (free from
[fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)).
Never commit this file.

### 3. Create the schema

```bash
cd backend
python -m venv .venv
```

Activate it — on Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Then install dependencies and build the schema:

```bash
pip install -r requirements.txt
alembic upgrade head
```

`alembic upgrade head` loads `backend/db/schema/initial.sql` — 31 tables covering
sources, datasets, the three observation layers, provenance, and governance.

### 4. Run the backend

```bash
uvicorn app.main:app --reload
```

API at http://localhost:8000 · interactive docs at http://localhost:8000/docs

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend at http://localhost:3000

## Documentation

| Document | Purpose |
|---|---|
| [ADRs 001–005](docs/phase-a/adrs-001-005.md) | Database, storage, ingestion, provenance, confidence tiers |
| [ADR-006](docs/phase-a/adr-006.md) | Resolution of the duplicate schema draft |
| [Engineering Standards](docs/phase-a/engineering-standards.md) | Code style, testing, Git workflow, accessibility |
| [Database Schema](docs/phase-a/database-schema.sql) | PostgreSQL DDL, indexes, immutable storage rules |
| [Source Registry](docs/phase-a/source-registry.yaml) | Data sources, datasets, access methods, licenses |
| [Data Dictionary](docs/phase-a/data-dictionary.yaml) | Metric definitions, methodologies, limitations |
| [PRD](docs/phase-a/prd.md) | Product requirements, user stories, acceptance criteria |
| [Phase C Schema Fix Plan](docs/phase-c/schema-fix-plan.md) | Backend/database convergence plan |

## API

Interactive documentation is generated automatically:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Available now

```bash
# Health check
curl http://localhost:8000/health

# List all metrics
curl http://localhost:8000/api/v1/metrics

# Observations for a metric, with explicit missing-data gaps
curl "http://localhost:8000/api/v1/observations?metric=gdp_nominal"
curl "http://localhost:8000/api/v1/observations?metric=unemployment_rate"
```

### Planned

Provenance chains, citation generation, filtering by date range and confidence
tier, and CSV/JSON export are specified in the PRD but not yet implemented.

## Accessibility

Targeting WCAG 2.2 AA:

- Keyboard navigable (Tab, Enter, Arrow keys)
- Screen reader compatible
- Color contrast 4.5:1 for normal text
- Color-blind safe palette

The Phase B shell has passed a manual accessibility review — see
[the Phase B checklist](docs/phase-a/phase-b-a11y-checklist.md).

## Data Governance

### Immutability policy

- **Raw observations:** never updated or deleted
- **Standardized observations:** append-only (new versions, not overwrites)
- **Revisions:** marked with a reason; old versions preserved

### Confidence tiers

Every observation carries exactly one tier:

| Tier | Meaning |
|---|---|
| `OFFICIAL_MEASUREMENT` | Direct government measurement |
| `ADMINISTRATIVE_RECORD` | Government administrative data |
| `SURVEY_ESTIMATE` | Sampled government survey |
| `HISTORICAL_RECONSTRUCTION` | Reconstructed from historical documents |
| `ACADEMIC_ESTIMATE` | Published peer-reviewed research |
| `MODELED_DERIVED` | Calculated from other observations |
| `UNKNOWN` | Cannot be classified |

### Missing data

Gaps are recorded explicitly in `missing_data_records` with a reason and
explanation. Missing data is never shown as zero, blank, or interpolated.

## Roadmap

| Phase | Focus | Status |
|---|---|---|
| A | Foundation (docs, schema, sources) | Complete |
| B | Platform shell (UI, timeline, charts) | Complete |
| C | Data infrastructure (ingestion, validation) | In progress |
| D | Phase 1 data (1990–present) | Planned |
| E | Historical backfill (1776–1989) | Planned |
| F | Enhancements (search, export, audits) | Planned |
| G | Open-source prep (community, CI, licensing) | Planned |

Two metrics are live end to end: **nominal GDP** (FRED `GDP`) and the
**unemployment rate** (FRED `UNRATE`).

## Contributing

Contribution workflow opens in Phase G. Until then, see the
[Engineering Standards](docs/phase-a/engineering-standards.md) for coding,
commit, and review conventions.

Branch naming: `feature/*`, `fix/*`, `data/*`, `docs/*`, `chore/*`, `test/*`.
Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

## License

Code is licensed under the MIT License — see [LICENSE](LICENSE).

Data published by the platform is public domain or openly licensed, per each
authoritative source's terms. The curated dataset is intended for release under
CC-BY.

## Acknowledgments

U.S. Census Bureau, Bureau of Labor Statistics, USDA, Federal Reserve, and all
contributing federal agencies. Built on FastAPI, React, PostgreSQL, Apache
ECharts, and the wider open-source community.

---

*Built with evidence. Published with transparency. Maintained for the public good.*
