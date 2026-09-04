from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/unemployment", tags=["unemployment"])


@router.get("")
def get_unemployment_series(db: Session = Depends(get_db)):
    """
    Returns standardized Unemployment Rate observations + missing-data gaps,
    from the real canonical tables. Same pattern as gdp.py.
    """
    standardized = db.execute(text("""
        SELECT observation_date, standardized_value, confidence_tier
        FROM standardized_observations so
        JOIN metrics m ON so.metric_id = m.metric_id
        WHERE m.slug = 'unemployment_rate'
          -- Current version only; revisions supersede, never overwrite (ADR-002)
          AND so.valid_to IS NULL
          AND so.observation_status = 'CURRENT'
        ORDER BY observation_date
    """)).fetchall()

    missing = db.execute(text("""
        SELECT observation_date, missing_data_reason, explanation
        FROM missing_data_records mdr
        JOIN metrics m ON mdr.metric_id = m.metric_id
        WHERE m.slug = 'unemployment_rate'
        ORDER BY observation_date
    """)).fetchall()

    return {
        "metric": "unemployment_rate",
        "units": "percent",
        "observations": [
            {"date": str(row.observation_date), "value": float(row.standardized_value), "confidence_tier": row.confidence_tier}
            for row in standardized
        ],
        "missing": [
            {"date": str(row.observation_date), "reason": row.missing_data_reason, "explanation": row.explanation}
            for row in missing
        ],
    }
