"""GigScore record model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class GigScoreRecord(Base):
    """Snapshot of a worker's computed GigScore (0–900)."""

    __tablename__ = "gigscore_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )

    # ── Score ─────────────────────────────────────────────────
    score: Mapped[float] = mapped_column(Float, nullable=False, comment="0-900")
    income_consistency: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Sub-score 0-100"
    )
    trip_completion: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Sub-score 0-100"
    )
    rating_reliability: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Sub-score 0-100"
    )
    work_pattern: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Sub-score 0-100"
    )
    platform_diversity: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Sub-score 0-100"
    )

    # ── ML metadata ───────────────────────────────────────────
    model_version: Mapped[str | None] = mapped_column(default="rf_v1")
    feature_importance: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Feature importance from RF model"
    )

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ─────────────────────────────────────────
    worker = relationship("Worker", back_populates="gigscore_records")

    def __repr__(self) -> str:
        return f"<GigScore {self.score}/900>"
