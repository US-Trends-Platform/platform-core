from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_id: UUID
    domain_id: UUID
    slug: str
    name: str
    short_name: str | None = None
    definition: str
    units: str | None = None
    currency_code: str | None = None
    inflation_basis_year: int | None = None
    geographic_scope: str
    default_cadence: str | None = None
    methodology: str | None = None
    known_limitations: str | None = None
    comparison_note: str | None = None
    first_available_date: date | None = None
    last_available_date: date | None = None
    is_monetary: bool = False
    requires_real_and_nominal_display: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
