"""Worker identity resolution helpers for authenticated requests."""

from __future__ import annotations

import hashlib

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.worker import Worker

settings = get_settings()


def _dev_phone_from_uid(uid: str) -> str:
    """Generate a deterministic 10-digit phone number for local dev profiles."""
    digest = hashlib.sha256(uid.encode("utf-8")).hexdigest()
    value = int(digest[:12], 16)
    return str(7000000000 + (value % 2999999999))


async def resolve_worker_for_user(db: AsyncSession, user: dict) -> Worker:
    """
    Resolve worker linked to authenticated user.

    In non-production environments, create a minimal profile when missing
    so local development flows work without a separate onboarding call.
    """
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid auth payload")

    result = await db.execute(select(Worker).where(Worker.firebase_uid == uid))
    worker = result.scalar_one_or_none()
    if worker:
        return worker

    if settings.app_env.lower() == "production":
        raise HTTPException(status_code=404, detail="Worker profile not found")

    worker = Worker(
        firebase_uid=uid,
        name=(user.get("name") or "Gig Worker")[:255],
        phone=_dev_phone_from_uid(uid),
        email=user.get("email"),
        platforms="other",
    )
    db.add(worker)
    await db.flush()
    await db.refresh(worker)
    return worker
