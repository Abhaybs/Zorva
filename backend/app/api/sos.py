"""SOS Router API — emergency SOS with GPS broadcast and peer alerts."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.firebase import get_current_user
from app.models.worker import Worker
from app.models.sos import SosEvent, SosStatus
from app.schemas.sos import SosTriggerRequest, SosEventOut, SosResolveRequest

router = APIRouter()


@router.post("/trigger", response_model=SosEventOut, status_code=201)
async def trigger_sos(
    payload: SosTriggerRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger an SOS event.

    In production this would:
    1. Save GPS coordinates
    2. Send FCM push notifications to emergency contacts
    3. Broadcast to nearby peer workers via Firebase RTDB
    4. Optionally notify local authorities
    """
    # Verify worker
    result = await db.execute(
        select(Worker).where(Worker.id == payload.worker_id)
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    contacts_str = None
    if payload.emergency_contacts:
        contacts_str = ",".join(payload.emergency_contacts)

    event = SosEvent(
        worker_id=worker.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        message=payload.message,
        emergency_contacts_notified=contacts_str,
        status=SosStatus.TRIGGERED,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)

    # TODO: Integrate Firebase Cloud Messaging (FCM) for push notifications
    # TODO: Write to Firebase Realtime DB for live tracking
    # TODO: Reverse geocode to populate address field

    return event


@router.get("/status/{event_id}", response_model=SosEventOut)
async def get_sos_status(
    event_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current status of an SOS event."""
    result = await db.execute(
        select(SosEvent).where(SosEvent.id == event_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="SOS event not found")
    return event


@router.put("/resolve/{event_id}", response_model=SosEventOut)
async def resolve_sos(
    event_id: uuid.UUID,
    payload: SosResolveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resolve an active SOS event."""
    result = await db.execute(
        select(SosEvent).where(SosEvent.id == event_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="SOS event not found")

    if event.status == SosStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Event already resolved")

    event.status = SosStatus.FALSE_ALARM if payload.is_false_alarm else SosStatus.RESOLVED
    event.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(event)

    return event


@router.get("/active", response_model=list[SosEventOut])
async def get_active_sos(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all active (unresolved) SOS events for the worker."""
    result = await db.execute(
        select(Worker).where(Worker.firebase_uid == user["uid"])
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    events_result = await db.execute(
        select(SosEvent)
        .where(SosEvent.worker_id == worker.id)
        .where(SosEvent.status.in_([SosStatus.TRIGGERED, SosStatus.ACKNOWLEDGED, SosStatus.RESPONDING]))
        .order_by(SosEvent.triggered_at.desc())
    )
    return events_result.scalars().all()
