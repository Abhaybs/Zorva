"""Worker profile model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Worker(Base):
    """Gig worker profile — the central entity in the system."""

    __tablename__ = "workers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )

    # ── Profile ───────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Location (latest known) ───────────────────────────────
    last_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Platforms ─────────────────────────────────────────────
    platforms: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Comma-separated platform names"
    )

    # ── Status ────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ─────────────────────────────────────────
    income_records = relationship("IncomeRecord", back_populates="worker")
    gigscore_records = relationship("GigScoreRecord", back_populates="worker")
    insurance_policies = relationship("InsurancePolicy", back_populates="worker")
    sos_events = relationship("SosEvent", back_populates="worker")

    def __repr__(self) -> str:
        return f"<Worker {self.name} ({self.phone})>"
