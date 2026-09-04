from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import Domain
from app.models.metric import Metric
from app.schemas.metric import MetricRead

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=list[MetricRead])
def list_metrics(
    domain_slug: str | None = Query(default=None, description="Filter by domain slug, e.g. 'economy'"),
    db: Session = Depends(get_db),
):
    stmt = select(Metric)
    if domain_slug:
        # Filter on the DOMAIN's slug via the domain_id FK, not the metric's own
        # slug. Comparing Metric.slug here silently returned nothing for every
        # real domain (e.g. 'economy'), since no metric slug equals a domain slug.
        stmt = stmt.join(Metric.domain).where(Domain.slug == domain_slug)
    return db.execute(stmt).scalars().all()


@router.get("/{slug}", response_model=MetricRead)
def get_metric(slug: str, db: Session = Depends(get_db)):
    metric = db.execute(select(Metric).where(Metric.slug == slug)).scalar_one_or_none()
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric
