from datetime import datetime, date

from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import DatasetLifecycleStatus


class Dataset(Base):
    """Individual datasets published by sources. Plan §32, §21, §30."""
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)

    dataset_id_external: Mapped[str | None] = mapped_column(String(255))  # source's own dataset/series ID
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2048))

    coverage_start: Mapped[date | None] = mapped_column(Date)
    coverage_end: Mapped[date | None] = mapped_column(Date)
    update_frequency: Mapped[str | None] = mapped_column(String(50))

    lifecycle_status: Mapped[DatasetLifecycleStatus] = mapped_column(
        SAEnum(DatasetLifecycleStatus, name="dataset_lifecycle_status"),
        default=DatasetLifecycleStatus.IDENTIFIED,
        nullable=False,
    )
    responsible_workstream: Mapped[str | None] = mapped_column(String(100))  # §30 - taxonomy TBD, see open question
    validation_status: Mapped[str | None] = mapped_column(String(50))
    approval_status: Mapped[str | None] = mapped_column(String(50))
    deprecation_status: Mapped[str | None] = mapped_column(String(50))

    retrieval_date: Mapped[date | None] = mapped_column(Date)
    last_source_update: Mapped[date | None] = mapped_column(Date)
    checksum: Mapped[str | None] = mapped_column(String(128))

    licensing: Mapped[str | None] = mapped_column(String(512))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # §21 - revisions create new versions

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source: Mapped["Source"] = relationship(back_populates="datasets")
    metrics: Mapped[list["Metric"]] = relationship(back_populates="dataset")
