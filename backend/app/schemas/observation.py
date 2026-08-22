from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import ConfidenceClassification


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    metric_id: int
    observation_date: date
    value: Decimal | None  # null == missing (§23), never coerced to 0
    confidence: ConfidenceClassification
    is_raw: bool
    created_at: datetime
