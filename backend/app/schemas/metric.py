from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    metric_id_code: str
    domain: str
    name: str
    definition: str
    units: str | None
    currency_basis: str | None
    inflation_basis_year: int | None
    geographic_scope: str
    coverage_start: date | None
    coverage_end: date | None
    created_at: datetime
    updated_at: datetime
