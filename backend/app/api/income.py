"""Income Aggregation API — cross-platform earnings management."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.supabase import get_current_user
from app.models.income import IncomeRecord, IncomeSource, IncomePlatform
from app.schemas.income import IncomeRecordCreate, IncomeRecordOut, IncomeSummary
from app.services.worker_resolver import resolve_worker_for_user

router = APIRouter()


@router.post("/record", response_model=IncomeRecordOut, status_code=201)
async def add_income_record(
    payload: IncomeRecordCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new income entry from any source (OCR, SMS, manual, etc.)."""
    worker = await resolve_worker_for_user(db, user)

    record = IncomeRecord(
        worker_id=worker.id,
        amount=payload.amount,
        platform=IncomePlatform(payload.platform),
        source=IncomeSource(payload.source),
        description=payload.description,
        transaction_ref=payload.transaction_ref,
        earned_at=payload.earned_at,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.get("/summary", response_model=IncomeSummary)
async def get_income_summary(
    days: int = Query(30, ge=1, le=365, description="Lookback period in days"),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated income summary for the given period."""
    worker = await resolve_worker_for_user(db, user)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Fetch records in period
    records_result = await db.execute(
        select(IncomeRecord)
        .where(IncomeRecord.worker_id == worker.id)
        .where(IncomeRecord.earned_at >= cutoff)
        .order_by(IncomeRecord.earned_at.desc())
    )
    records = records_result.scalars().all()

    total = sum(r.amount for r in records)
    platforms = list(set(r.platform.value for r in records))

    return IncomeSummary(
        worker_id=worker.id,
        total_earnings=total,
        average_daily=total / max(days, 1),
        total_records=len(records),
        platforms_used=platforms,
        period_start=cutoff,
        period_end=datetime.now(timezone.utc),
    )


@router.get("/history", response_model=list[IncomeRecordOut])
async def get_income_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    platform: str | None = Query(None, description="Filter by platform"),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed income history with optional platform filter."""
    worker = await resolve_worker_for_user(db, user)

    query = (
        select(IncomeRecord)
        .where(IncomeRecord.worker_id == worker.id)
        .order_by(IncomeRecord.earned_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if platform:
        query = query.where(IncomeRecord.platform == IncomePlatform(platform))

    records_result = await db.execute(query)
    return records_result.scalars().all()
