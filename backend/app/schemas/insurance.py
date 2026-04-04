"""Pydantic schemas for Insurance domain."""

from __future__ import annotations
import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class InsurancePlanOut(BaseModel):
    """Available insurance plan."""
    id: str
    insurance_type: str
    provider: str
    plan_name: str
    premium_daily: float
    coverage_amount: float
    description: str


class InsuranceSubscribeRequest(BaseModel):
    """Subscribe to an insurance plan."""
    worker_id: uuid.UUID
    plan_id: str
    start_date: date


class InsuranceClaimRequest(BaseModel):
    """File an insurance claim."""
    policy_id: uuid.UUID
    description: str
    claim_amount: float = Field(..., gt=0)


class InsurancePolicyOut(BaseModel):
    """Worker's insurance policy."""
    id: uuid.UUID
    worker_id: uuid.UUID
    insurance_type: str
    provider: str
    plan_name: str
    premium_daily: float
    coverage_amount: float
    start_date: date
    end_date: date
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
