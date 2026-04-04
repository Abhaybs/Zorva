"""SOS event model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base


class SosStatus(str, enum.Enum):
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESPONDING = "responding"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class SosEvent(Base):
    """Emergency SOS event with GPS location."""

    __tablename__ = "sos_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )

    # ── Location ──────────────────────────────────────────────
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Event ─────────────────────────────────────────────────
    status: Mapped[SosStatus] = mapped_column(
        SAEnum(SosStatus), default=SosStatus.TRIGGERED
    )
    message: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, comment="Optional distress message"
    )
    emergency_contacts_notified: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Comma-separated phone numbers"
    )

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ─────────────────────────────────────────
    worker = relationship("Worker", back_populates="sos_events")

    def __repr__(self) -> str:
        return f"<SOS {self.status.value} at ({self.latitude}, {self.longitude})>"
