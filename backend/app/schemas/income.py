"""Pydantic schemas for Income domain."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IncomeRecordCreate(BaseModel):
    """Payload to add an income entry."""
    amount: float = Field(..., gt=0)
    platform: str = Field(..., description="Platform enum value")
    source: str = Field(..., description="How data was captured")
    description: Optional[str] = None
    transaction_ref: Optional[str] = None
    earned_at: datetime


class IncomeRecordOut(BaseModel):
    """Single income record response."""
    id: uuid.UUID
    worker_id: uuid.UUID
    amount: float
    currency: str
    platform: str
    source: str
    description: Optional[str] = None
    transaction_ref: Optional[str] = None
    earned_at: datetime
    recorded_at: datetime

    model_config = {"from_attributes": True}


class IncomeSummary(BaseModel):
    """Aggregated income summary."""
    worker_id: uuid.UUID
    total_earnings: float
    average_daily: float
    total_records: int
    platforms_used: list[str]
    period_start: datetime
    period_end: datetime
