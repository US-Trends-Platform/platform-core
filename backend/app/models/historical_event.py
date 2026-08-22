from datetime import datetime, date

from sqlalchemy import String, Integer, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ConfidenceClassification, confidence_classification_type


class HistoricalEvent(Base):
    """Historical contextual information. Plan §16, §17."""
    __tablename__ = "historical_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)

    category: Mapped[str] = mapped_column(String(100), nullable=False)  # War, Economic Crisis, etc. — §16
    subcategory: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(4096), nullable=False)

    affected_domains: Mapped[str | None] = mapped_column(String(512))  # comma-separated domain codes, revisit as array/join table
    primary_sources: Mapped[str | None] = mapped_column(String(1024))
    related_legislation: Mapped[str | None] = mapped_column(String(1024))

    confidence: Mapped[ConfidenceClassification] = mapped_column(
        confidence_classification_type, nullable=False
    )
    historical_notes: Mapped[str | None] = mapped_column(String(2048))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
