"""Government Scheme Matcher API — match workers to welfare schemes."""

from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.supabase import get_current_user
from app.services.scheme_matcher import SchemeMatcher
from app.services.worker_resolver import resolve_worker_for_user

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
    worker = await resolve_worker_for_user(db, user)

    eligible = matcher.match_schemes(worker)
    return {
        "worker_id": str(worker.id),
        "eligible_count": len(eligible),
        "schemes": eligible,
    }
