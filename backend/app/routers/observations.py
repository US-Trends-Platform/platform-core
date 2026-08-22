from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.metric import Metric
from app.models.observation import Observation
from app.schemas.observation import ObservationRead

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get("", response_model=list[ObservationRead])
def list_observations(
    metric_id_code: str = Query(..., description="Metric code, e.g. 'employment.unemployment_rate'"),
    start_date: date | None = None,
    end_date: date | None = None,
    raw_only: bool = Query(default=False, description="Return only immutable raw observations (§22)"),
    db: Session = Depends(get_db),
):
    metric = db.execute(
        select(Metric).where(Metric.metric_id_code == metric_id_code)
    ).scalar_one_or_none()
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")

    stmt = select(Observation).where(Observation.metric_id == metric.id)
    if start_date:
        stmt = stmt.where(Observation.observation_date >= start_date)
    if end_date:
        stmt = stmt.where(Observation.observation_date <= end_date)
    if raw_only:
        stmt = stmt.where(Observation.is_raw.is_(True))
    stmt = stmt.order_by(Observation.observation_date)

    return db.execute(stmt).scalars().all()
