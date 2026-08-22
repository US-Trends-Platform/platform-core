from datetime import datetime, date

from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Metric(Base):
    """Standardized measurements. Plan §32, §19 (metadata standard)."""
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)

    metric_id_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # e.g. "employment.unemployment_rate"
    domain: Mapped[str] = mapped_column(String(50), nullable=False)  # one of the 10 domains, plan §7-16
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(String(2048), nullable=False)

    units: Mapped[str | None] = mapped_column(String(100))
    currency_basis: Mapped[str | None] = mapped_column(String(20))
    inflation_basis_year: Mapped[int | None] = mapped_column(Integer)
    geographic_scope: Mapped[str] = mapped_column(String(50), default="national", nullable=False)

    coverage_start: Mapped[date | None] = mapped_column(Date)
    coverage_end: Mapped[date | None] = mapped_column(Date)

    transformation_methodology: Mapped[str | None] = mapped_column(String(2048))
    known_limitations: Mapped[str | None] = mapped_column(String(2048))
    citation_info: Mapped[str | None] = mapped_column(String(1024))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    dataset: Mapped["Dataset"] = relationship(back_populates="metrics")
    observations: Mapped[list["Observation"]] = relationship(back_populates="metric")
