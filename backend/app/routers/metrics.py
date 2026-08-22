from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.metric import Metric
from app.schemas.metric import MetricRead

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=list[MetricRead])
def list_metrics(
    domain: str | None = Query(default=None, description="Filter by domain, e.g. 'agriculture'"),
    db: Session = Depends(get_db),
):
    stmt = select(Metric)
    if domain:
        stmt = stmt.where(Metric.domain == domain)
    return db.execute(stmt).scalars().all()


@router.get("/{metric_id_code}", response_model=MetricRead)
def get_metric(metric_id_code: str, db: Session = Depends(get_db)):
    stmt = select(Metric).where(Metric.metric_id_code == metric_id_code)
    metric = db.execute(stmt).scalar_one_or_none()
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric
