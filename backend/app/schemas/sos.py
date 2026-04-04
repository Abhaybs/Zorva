"""Pydantic schemas for SOS domain."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SosTriggerRequest(BaseModel):
    """Trigger an SOS event."""
    worker_id: uuid.UUID
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    message: Optional[str] = None
    emergency_contacts: Optional[list[str]] = Field(
        None, description="Phone numbers to notify"
    )


class SosEventOut(BaseModel):
    """SOS event response."""
    id: uuid.UUID
    worker_id: uuid.UUID
    latitude: float
    longitude: float
    address: Optional[str] = None
    status: str
    message: Optional[str] = None
    emergency_contacts_notified: Optional[str] = None
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SosResolveRequest(BaseModel):
    """Resolve an active SOS event."""
    resolution_note: Optional[str] = None
    is_false_alarm: bool = False
