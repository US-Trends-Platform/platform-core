from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Source(Base):
    """Organizations and source systems. Plan §32, §44, §45."""
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    organization_type: Mapped[str] = mapped_column(String(100), nullable=False)
    priority_tier: Mapped[int] = mapped_column(Integer, nullable=False)  # SourcePriorityTier
    homepage_url: Mapped[str | None] = mapped_column(String(512))
    licensing_notes: Mapped[str | None] = mapped_column(String(1024))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    datasets: Mapped[list["Dataset"]] = relationship(back_populates="source")
