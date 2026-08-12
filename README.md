File: README.md 
### Action:
```bash
# Replace existing README
cat > README.md << 'EOF'

# U.S. Socioeconomic, Political & Agricultural Trends Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Repo](https://img.shields.io/badge/GitHub-us--trends--platform%2Fplatform--core-blue)](https://github.com/us-trends-platform/platform-core)

A research-grade, open-source platform documenting American socioeconomic, political, and agricultural trends from 1776 to the present.

## Overview

This platform enables researchers, educators, journalists, and the general public to:

- **Explore authoritative historical data** from federal sources (Census, BLS, USDA, FRED, etc.)
- **Understand data provenance** — trace every number back to its source
- **Access complete methodology** — transparent about how data is collected and processed
- **Compare historical periods** without causal assumptions
- **Generate academic citations** in APA, MLA, Chicago, BibTeX formats
- **Download data** in open formats (CSV, JSON, Parquet)

## 🎯 Core Principles

- **Evidence before interpretation** — raw observations never fabricated
- **Sources before claims** — complete provenance chain preserved
- **Raw observations before analytics** — derived metrics clearly labeled
- **Transparency before convenience** — no hidden data cleaning
- **Uncertainty before false precision** — confidence tiers on every observation

## 🏗️ Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy, Pydantic v2 | REST API, data ingestion, validation |
| **Database** | PostgreSQL, DuckDB | Immutable raw storage, analytics engine |
| **Frontend** | Next.js, React, TypeScript, TailwindCSS | Interactive timeline, charts, accessibility |
| **Visualization** | Apache ECharts, D3.js | Time-series, confidence tier indicators |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Containerization, CI/CD, testing |

## 📊 Phase 1 Scope

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
- **Metrics:** 100+ core indicators
- **Sources:** 15+ authoritative federal agencies

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 16+
- Docker & Docker Compose (recommended)

### Quick Start (Docker)
```bash
# Clone repo
git clone https://github.com/us-trends-platform/platform-core
cd platform-core

# Start services
docker-compose up -d

# Backend at http://localhost:8000
# Frontend at http://localhost:3000
# API docs at http://localhost:8000/docs
Manual Setup
bash


# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev

📖 Documentation
Document	Purpose
ADRs 001–005 	Architectural decisions: database, storage, ingestion, provenance, confidence tiers
Engineering Standards 	Code style, testing, Git workflows, accessibility
Database Schema 	PostgreSQL DDL, indexes, immutable storage rules
Source Registry 	All data sources, datasets, access methods, licenses
Data Dictionary 	Metric definitions, methodologies, limitations, series mappings
PRD 	Product requirements, user stories, acceptance criteria
🔗 API Documentation
Interactive:  http://localhost:8000/docs  (Swagger UI)
Alternative:  http://localhost:8000/redoc  (ReDoc)

Example Queries
bash


# Get all metrics
curl http://localhost:8000/api/v1/metrics

# Get unemployment rate observations (1990–2024)
curl "http://localhost:8000/api/v1/observations?metric_id=unemployment_rate_total&start_date=1990-01-01&end_date=2024-12-31"

# Get provenance for a specific observation
curl http://localhost:8000/api/v1/observations/{observation_id}/provenance

# Generate APA citation
curl -X POST http://localhost:8000/api/v1/citations \
  -H "Content-Type: application/json" \
  -d '{"metric_id": "unemployment_rate_total", "format": "apa"}'
🧪 Testing
bash


# Backend unit tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up
♿ Accessibility
WCAG 2.2 AA compliant
Keyboard navigable (Tab, Enter, Arrow keys)
Screen reader compatible (NVDA, JAWS)
High color contrast (4.5:1 normal text)
Color-blind safe palette
📋 Data Governance
Immutability Policy
Raw observations: never updated or deleted
Standardized observations: append-only (new versions, not overwrites)
Revisions: marked with reason; old versions preserved
Confidence Tiers
OFFICIAL_MEASUREMENT — Direct government measurement
ADMINISTRATIVE_RECORD — Government administrative data
SURVEY_ESTIMATE — Sampled government survey
HISTORICAL_RECONSTRUCTION — Reconstructed from historical documents
ACADEMIC_ESTIMATE — Published peer-reviewed research
MODELED_DERIVED — Calculated from other observations
UNKNOWN — Cannot be classified
🔐 Security
HTTPS/TLS 1.2+ required
Input validation on all endpoints
Secrets in environment variables (no hardcoding)
Weekly dependency vulnerability scans
Rate limiting: 1,000 req/min per IP

📈 Roadmap
Phase	Focus	Timeline
A	Foundation (docs, schema, sources)	✅ Complete
B	Platform shell (UI, timeline, charts)	Q4 2026
C	Data infrastructure (ingestion, validation)	Q1 2027
D	Phase 1 data (1990–present)	Q2 2027
E	Historical backfill (1776–1989)	Q3 2027
F	Enhancements (search, export, audits)	Q4 2027
G	Open-source prep (community, CI, licensing)	Q1 2028

🤝 Contributing
We welcome contributions! See  CONTRIBUTING.md  for guidelines.

How to Contribute
Fork the repository
Create a feature branch (git checkout -b feature/your-feature)
Commit changes (git commit -m "feat: description")
Push to branch (git push origin feature/your-feature)
Open a Pull Request
📜 License
This project is licensed under the MIT License — see  LICENSE  for details.

All data published by the platform is public domain or openly licensed (per authoritative source terms).

📞 Support
Issues: GitHub Issues for bugs and feature requests
Discussions: GitHub Discussions for questions and ideas
Documentation: See /docs directory
🙏 Acknowledgments
U.S. Census Bureau, Bureau of Labor Statistics, USDA, Federal Reserve, and all contributing federal agencies
Open-source community for FastAPI, React, PostgreSQL, and all dependencies
WCAG accessibility guidelines and best practices
Built with evidence. Published with transparency. Maintained for the public good.

EOF
