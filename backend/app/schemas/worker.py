"""Pydantic schemas for Worker domain."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkerCreate(BaseModel):
    """Payload to register a new gig worker."""
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    email: Optional[str] = None
    city: Optional[str] = None
    platforms: Optional[str] = Field(None, description="Comma-separated platform names")


class WorkerUpdate(BaseModel):
    """Payload to update worker profile."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    platforms: Optional[str] = None
    last_lat: Optional[float] = None
    last_lng: Optional[float] = None


class WorkerOut(BaseModel):
    """Worker response schema."""
    id: uuid.UUID
    firebase_uid: str
    name: str
    phone: str
    email: Optional[str] = None
    city: Optional[str] = None
    platforms: Optional[str] = None
    last_lat: Optional[float] = None
    last_lng: Optional[float] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
