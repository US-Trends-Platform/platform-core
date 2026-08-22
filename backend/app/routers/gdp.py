from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/gdp", tags=["gdp"])


@router.get("")
def get_gdp_series(db: Session = Depends(get_db)):
    """
    Returns standardized GDP observations + missing-data gaps, straight from
    the real canonical tables (raw_observations -> standardized_observations,
    per ADR-002/ADR-005). Missing quarters are returned explicitly, never
    silently dropped or shown as zero (per PRD FR-7).
    """
    standardized = db.execute(text("""
        SELECT observation_date, standardized_value, confidence_tier
        FROM standardized_observations so
        JOIN metrics m ON so.metric_id = m.metric_id
        WHERE m.slug = 'gdp_nominal'
        ORDER BY observation_date
    """)).fetchall()

    missing = db.execute(text("""
        SELECT observation_date, missing_data_reason, explanation
        FROM missing_data_records mdr
        JOIN metrics m ON mdr.metric_id = m.metric_id
        WHERE m.slug = 'gdp_nominal'
        ORDER BY observation_date
    """)).fetchall()

    return {
        "metric": "gdp_nominal",
        "units": "billions_of_dollars",
        "observations": [
            {"date": str(row.observation_date), "value": float(row.standardized_value), "confidence_tier": row.confidence_tier}
            for row in standardized
        ],
        "missing": [
            {"date": str(row.observation_date), "reason": row.missing_data_reason, "explanation": row.explanation}
            for row in missing
        ],
    }
