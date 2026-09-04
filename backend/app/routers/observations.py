from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import ObservationStatus
from app.models.metric import Metric
from app.models.observation import MissingDataRecord, StandardizedObservation
from app.schemas.observation import ObservationSeriesResponse

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get("", response_model=ObservationSeriesResponse)
def get_metric_observations(
    metric: str = Query(..., description="Metric slug, e.g. 'gdp_nominal' or 'unemployment_rate'"),
    db: Session = Depends(get_db),
):
    metric_row = db.execute(select(Metric).where(Metric.slug == metric)).scalar_one_or_none()
    if metric_row is None:
        raise HTTPException(status_code=404, detail="Metric not found")

    standardized_rows = db.execute(
        select(
            StandardizedObservation.observation_date,
            StandardizedObservation.standardized_value,
            StandardizedObservation.confidence_tier,
        )
        # Return only the CURRENT version of each observation. Per ADR-002 a
        # revision supersedes rather than overwrites: the old row is kept with
        # valid_to set. Without this filter, the first time a source revises a
        # figure the chart would show two values for the same date.
        .where(
            StandardizedObservation.metric_id == metric_row.metric_id,
            StandardizedObservation.valid_to.is_(None),
            StandardizedObservation.observation_status == ObservationStatus.CURRENT,
        )
        .order_by(StandardizedObservation.observation_date)
    ).all()

    missing_rows = db.execute(
        select(
            MissingDataRecord.observation_date,
            MissingDataRecord.missing_data_reason,
            MissingDataRecord.explanation,
        )
        .where(MissingDataRecord.metric_id == metric_row.metric_id)
        .order_by(MissingDataRecord.observation_date)
    ).all()

    return {
        "metric": metric_row.slug,
        "units": metric_row.units,
        "observations": [
            {
                "date": str(row.observation_date),
                "value": float(row.standardized_value) if row.standardized_value is not None else None,
                "confidence_tier": row.confidence_tier.value if hasattr(row.confidence_tier, "value") else row.confidence_tier,
            }
            for row in standardized_rows
        ],
        "missing": [
            {
                "date": str(row.observation_date),
                "reason": getattr(row.missing_data_reason, "value", row.missing_data_reason),
                "explanation": row.explanation,
            }
            for row in missing_rows
        ],
    }
