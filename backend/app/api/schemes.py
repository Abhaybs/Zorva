"""Government Scheme Matcher API — match workers to welfare schemes."""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.firebase import get_current_user
from app.models.worker import Worker
from app.services.scheme_matcher import SchemeMatcher

router = APIRouter()
matcher = SchemeMatcher()


@router.get("/all")
async def list_all_schemes(user: dict = Depends(get_current_user)):
    """List all known government welfare schemes for gig workers."""
    return {"schemes": matcher.get_all_schemes()}


@router.get("/eligible")
async def get_eligible_schemes(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Match the worker's profile to eligible government welfare schemes.

    Checks factors like: income level, platform type, city, age, etc.
    """
    result = await db.execute(
        select(Worker).where(Worker.firebase_uid == user["uid"])
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    eligible = matcher.match_schemes(worker)
    return {
        "worker_id": str(worker.id),
        "eligible_count": len(eligible),
        "schemes": eligible,
    }
