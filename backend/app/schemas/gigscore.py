"""Pydantic schemas for GigScore domain."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GigScoreRequest(BaseModel):
    """Trigger GigScore calculation."""
    worker_id: uuid.UUID


class GigScoreBreakdown(BaseModel):
    """Detailed sub-score breakdown."""
    income_consistency: float = Field(..., ge=0, le=100)
    trip_completion: float = Field(..., ge=0, le=100)
    rating_reliability: float = Field(..., ge=0, le=100)
    work_pattern: float = Field(..., ge=0, le=100)
    platform_diversity: float = Field(..., ge=0, le=100)


class GigScoreOut(BaseModel):
    """GigScore response."""
    id: uuid.UUID
    worker_id: uuid.UUID
    score: float = Field(..., ge=0, le=900)
    breakdown: GigScoreBreakdown
    model_version: Optional[str] = None
    feature_importance: Optional[dict] = None
    computed_at: datetime

    model_config = {
        "from_attributes": True,
        "protected_namespaces": (),
    }


class GigScoreHistory(BaseModel):
    """Historical GigScore trend."""
    worker_id: uuid.UUID
    scores: list[GigScoreOut]
    trend: str = Field(..., description="up, down, or stable")
