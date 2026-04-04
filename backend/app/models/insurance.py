"""Insurance policy model."""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base


class InsuranceType(str, enum.Enum):
    ACCIDENT = "accident"
    HEALTH = "health"
    VEHICLE = "vehicle"
    INCOME_PROTECTION = "income_protection"


class PolicyStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    CANCELLED = "cancelled"
    PENDING = "pending"


class InsurancePolicy(Base):
    """Micro-insurance policy linked to a worker."""

    __tablename__ = "insurance_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )

    # ── Policy details ────────────────────────────────────────
    insurance_type: Mapped[InsuranceType] = mapped_column(
        SAEnum(InsuranceType), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    plan_name: Mapped[str] = mapped_column(String(200), nullable=False)
    premium_daily: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Daily premium in INR"
    )
    coverage_amount: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Max coverage in INR"
    )

    # ── Dates ─────────────────────────────────────────────────
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        SAEnum(PolicyStatus), default=PolicyStatus.ACTIVE
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ─────────────────────────────────────────
    worker = relationship("Worker", back_populates="insurance_policies")

    def __repr__(self) -> str:
        return f"<Insurance {self.insurance_type.value} — ₹{self.premium_daily}/day>"
