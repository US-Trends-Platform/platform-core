from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import ConfidenceTier


class RawObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_observation_id: UUID
    raw_artifact_id: UUID
    dataset_series_id: UUID | None = None
    observation_key: str | None = None
    raw_period_label: str | None = None
    raw_date: date | None = None
    raw_value_text: str | None = None
    raw_value_numeric: float | None = None
    raw_units: str | None = None
    row_number_in_artifact: int | None = None
    created_at: datetime


class StandardizedObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    standardized_observation_id: UUID
    raw_observation_id: UUID
    metric_id: UUID
    dataset_series_id: UUID | None = None
    transformation_run_id: UUID
    observation_date: date
    period_start: date | None = None
    period_end: date | None = None
    standardized_value: float | None = None
    standardized_value_text: str | None = None
    units: str
    currency_code: str | None = None
    inflation_basis_year: int | None = None
    confidence_tier: ConfidenceTier
    observation_status: str = "CURRENT"
    valid_from: datetime
    valid_to: datetime | None = None
    revision_note: str | None = None
    approval_status: str = "PENDING"
    approved_at: datetime | None = None
    approved_by: str | None = None
    created_at: datetime


class MissingDataRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    missing_data_record_id: UUID
    metric_id: UUID
    dataset_series_id: UUID | None = None
    observation_date: date
    missing_data_reason: str
    explanation: str
    earliest_available_date: date | None = None
    source_note: str | None = None
    created_at: datetime
    created_by: str


class ObservationPoint(BaseModel):
    date: date
    value: float | None = None
    confidence_tier: str | None = None


class MissingObservationPoint(BaseModel):
    date: date
    reason: str
    explanation: str


class ObservationSeriesResponse(BaseModel):
    metric: str
    units: str | None = None
    observations: list[ObservationPoint]
    missing: list[MissingObservationPoint]
