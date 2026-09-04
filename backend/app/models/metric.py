from datetime import datetime, date

from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import CadenceType, cadence_type


class Metric(Base):
    """Canonical metric metadata for the live database schema."""

    __tablename__ = "metrics"

    metric_id: Mapped[UUID] = mapped_column(primary_key=True)
    domain_id: Mapped[UUID] = mapped_column(ForeignKey("domains.domain_id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(128))
    definition: Mapped[str] = mapped_column(String, nullable=False)
    units: Mapped[str | None] = mapped_column(String(128))
    currency_code: Mapped[str | None] = mapped_column(String(3))
    inflation_basis_year: Mapped[int | None] = mapped_column(Integer)
    geographic_scope: Mapped[str] = mapped_column(String(128), default="US_NATIONAL", nullable=False)
    default_cadence: Mapped[CadenceType | None] = mapped_column(cadence_type)
    methodology: Mapped[str | None] = mapped_column(String)
    known_limitations: Mapped[str | None] = mapped_column(String)
    comparison_note: Mapped[str | None] = mapped_column(String)
    first_available_date: Mapped[date | None] = mapped_column(Date)
    last_available_date: Mapped[date | None] = mapped_column(Date)
    is_monetary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_real_and_nominal_display: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    domain: Mapped["Domain"] = relationship(back_populates="metrics")
    standardized_observations: Mapped[list["StandardizedObservation"]] = relationship(back_populates="metric")
    missing_data_records: Mapped[list["MissingDataRecord"]] = relationship(back_populates="metric")