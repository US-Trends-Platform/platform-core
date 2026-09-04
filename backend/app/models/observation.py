from datetime import datetime, date
from uuid import UUID

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ConfidenceTier, confidence_tier_type


class RawObservation(Base):
    """Immutable raw data file rows captured from source artifacts."""

    __tablename__ = "raw_observations"

    raw_observation_id: Mapped[UUID] = mapped_column(primary_key=True)
    raw_artifact_id: Mapped[UUID] = mapped_column(ForeignKey("raw_artifacts.raw_artifact_id"), nullable=False)
    dataset_series_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_series.dataset_series_id"))
    observation_key: Mapped[str | None] = mapped_column(String(255))
    raw_period_label: Mapped[str | None] = mapped_column(String(64))
    raw_date: Mapped[date | None] = mapped_column(Date)
    raw_value_text: Mapped[str | None] = mapped_column(String)
    raw_value_numeric: Mapped[float | None] = mapped_column(Numeric)
    raw_units: Mapped[str | None] = mapped_column(String(128))
    raw_record: Mapped[dict] = mapped_column(JSON, nullable=False)
    row_number_in_artifact: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    standardized_observations: Mapped[list["StandardizedObservation"]] = relationship(back_populates="raw_observation")


class StandardizedObservation(Base):
    """Standardized observations with a required confidence tier."""

    __tablename__ = "standardized_observations"

    standardized_observation_id: Mapped[UUID] = mapped_column(primary_key=True)
    raw_observation_id: Mapped[UUID] = mapped_column(ForeignKey("raw_observations.raw_observation_id"), nullable=False)
    metric_id: Mapped[UUID] = mapped_column(ForeignKey("metrics.metric_id"), nullable=False)
    dataset_series_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_series.dataset_series_id"))
    transformation_run_id: Mapped[UUID] = mapped_column(ForeignKey("transformation_runs.transformation_run_id"), nullable=False)
    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date)
    period_end: Mapped[date | None] = mapped_column(Date)
    standardized_value: Mapped[float | None] = mapped_column(Numeric)
    standardized_value_text: Mapped[str | None] = mapped_column(String)
    units: Mapped[str] = mapped_column(String(128), nullable=False)
    currency_code: Mapped[str | None] = mapped_column(String(3))
    inflation_basis_year: Mapped[int | None] = mapped_column()
    confidence_tier: Mapped[ConfidenceTier] = mapped_column(confidence_tier_type, nullable=False)
    observation_status: Mapped[str] = mapped_column(String(32), default="CURRENT", nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime)
    revision_note: Mapped[str | None] = mapped_column(String)
    approval_status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    approved_by: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    raw_observation: Mapped["RawObservation"] = relationship(back_populates="standardized_observations")
    metric: Mapped["Metric"] = relationship(back_populates="standardized_observations")


class MissingDataRecord(Base):
    """Explicit missing-data gaps for a metric and date."""

    __tablename__ = "missing_data_records"

    missing_data_record_id: Mapped[UUID] = mapped_column(primary_key=True)
    metric_id: Mapped[UUID] = mapped_column(ForeignKey("metrics.metric_id"), nullable=False)
    dataset_series_id: Mapped[UUID | None] = mapped_column(ForeignKey("dataset_series.dataset_series_id"))
    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    missing_data_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    explanation: Mapped[str] = mapped_column(String, nullable=False)
    earliest_available_date: Mapped[date | None] = mapped_column(Date)
    source_note: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), default="system", nullable=False)

    metric: Mapped["Metric"] = relationship(back_populates="missing_data_records")
