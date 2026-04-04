"""Income record model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base


class IncomeSource(str, enum.Enum):
    """How the income data was captured."""
    SCREENSHOT_OCR = "screenshot_ocr"
    SMS_PARSE = "sms_parse"
    MANUAL_ENTRY = "manual_entry"
    BANK_AA = "bank_aa"         # Account Aggregator
    API_SYNC = "api_sync"       # Future direct platform API


class IncomePlatform(str, enum.Enum):
    """Known gig platforms."""
    SWIGGY = "swiggy"
    ZOMATO = "zomato"
    OLA = "ola"
    UBER = "uber"
    DUNZO = "dunzo"
    ZEPTO = "zepto"
    RAPIDO = "rapido"
    BLINKIT = "blinkit"
    OTHER = "other"
    CASH = "cash"
    UPI_DIRECT = "upi_direct"


class IncomeRecord(Base):
    """Single income entry from any source / platform."""

    __tablename__ = "income_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )

    # ── Core data ─────────────────────────────────────────────
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    platform: Mapped[IncomePlatform] = mapped_column(
        SAEnum(IncomePlatform), nullable=False
    )
    source: Mapped[IncomeSource] = mapped_column(
        SAEnum(IncomeSource), nullable=False
    )

    # ── Metadata ──────────────────────────────────────────────
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transaction_ref: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="UPI ref / trip ID"
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ─────────────────────────────────────────
    worker = relationship("Worker", back_populates="income_records")

    def __repr__(self) -> str:
        return f"<Income ₹{self.amount} from {self.platform.value}>"
