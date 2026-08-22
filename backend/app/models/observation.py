from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import Integer, DateTime, Date, ForeignKey, Numeric, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ConfidenceClassification, confidence_classification_type


class Observation(Base):
    """Values associated with metrics and dates. Plan §32.

    Raw observations (§22) are immutable: is_raw=True rows are never updated
    in place. Derived values (§24) reference their source observation(s) via
    derived_from_observation_id and set is_raw=False.
    """
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_id: Mapped[int] = mapped_column(ForeignKey("metrics.id"), nullable=False)

    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))  # NULL = missing, never 0 (§23)

    confidence: Mapped[ConfidenceClassification] = mapped_column(
        confidence_classification_type, nullable=False
    )
    is_raw: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    derived_from_observation_id: Mapped[int | None] = mapped_column(ForeignKey("observations.id"))

    retrieval_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_version: Mapped[str | None] = mapped_column(String(100))
    revision_of_id: Mapped[int | None] = mapped_column(ForeignKey("observations.id"))  # §21 new version, not overwrite

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    metric: Mapped["Metric"] = relationship(back_populates="observations")
