"""GigScore API — trigger ML model and retrieve scores."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.firebase import get_current_user
from app.models.worker import Worker
from app.models.gigscore import GigScoreRecord
from app.models.income import IncomeRecord
from app.schemas.gigscore import GigScoreRequest, GigScoreOut, GigScoreBreakdown, GigScoreHistory
from app.services.gigscore_engine import GigScoreEngine
from app.services.worker_resolver import resolve_worker_for_user

router = APIRouter()
score_engine = GigScoreEngine()


@router.post("/calculate", response_model=GigScoreOut, status_code=201)
async def calculate_gigscore(
    payload: GigScoreRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger GigScore computation using the ML model."""
    # Fetch worker
    result = await db.execute(
        select(Worker).where(Worker.id == payload.worker_id)
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Fetch income history for feature engineering
    income_result = await db.execute(
        select(IncomeRecord)
        .where(IncomeRecord.worker_id == worker.id)
        .order_by(IncomeRecord.earned_at.desc())
        .limit(500)
    )
    income_records = income_result.scalars().all()

    # Compute score
    score_data = score_engine.compute(worker, income_records)

    # Persist
    record = GigScoreRecord(
        worker_id=worker.id,
        score=score_data["score"],
        income_consistency=score_data["breakdown"]["income_consistency"],
        trip_completion=score_data["breakdown"]["trip_completion"],
        rating_reliability=score_data["breakdown"]["rating_reliability"],
        work_pattern=score_data["breakdown"]["work_pattern"],
        platform_diversity=score_data["breakdown"]["platform_diversity"],
        model_version=score_data.get("model_version", "rf_v1"),
        feature_importance=score_data.get("feature_importance"),
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)

    return GigScoreOut(
        id=record.id,
        worker_id=record.worker_id,
        score=record.score,
        breakdown=GigScoreBreakdown(
            income_consistency=record.income_consistency,
            trip_completion=record.trip_completion,
            rating_reliability=record.rating_reliability,
            work_pattern=record.work_pattern,
            platform_diversity=record.platform_diversity,
        ),
        model_version=record.model_version,
        feature_importance=record.feature_importance,
        computed_at=record.computed_at,
    )


@router.get("/current", response_model=GigScoreOut)
async def get_current_gigscore(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the worker's latest GigScore."""
    worker = await resolve_worker_for_user(db, user)

    score_result = await db.execute(
        select(GigScoreRecord)
        .where(GigScoreRecord.worker_id == worker.id)
        .order_by(GigScoreRecord.computed_at.desc())
        .limit(1)
    )
    record = score_result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="No GigScore computed yet")

    return GigScoreOut(
        id=record.id,
        worker_id=record.worker_id,
        score=record.score,
        breakdown=GigScoreBreakdown(
            income_consistency=record.income_consistency,
            trip_completion=record.trip_completion,
            rating_reliability=record.rating_reliability,
            work_pattern=record.work_pattern,
            platform_diversity=record.platform_diversity,
        ),
        model_version=record.model_version,
        feature_importance=record.feature_importance,
        computed_at=record.computed_at,
    )


@router.get("/history", response_model=GigScoreHistory)
async def get_gigscore_history(
    limit: int = Query(10, ge=1, le=50),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get historical GigScore trend."""
    worker = await resolve_worker_for_user(db, user)

    scores_result = await db.execute(
        select(GigScoreRecord)
        .where(GigScoreRecord.worker_id == worker.id)
        .order_by(GigScoreRecord.computed_at.desc())
        .limit(limit)
    )
    records = scores_result.scalars().all()

    scores = [
        GigScoreOut(
            id=r.id,
            worker_id=r.worker_id,
            score=r.score,
            breakdown=GigScoreBreakdown(
                income_consistency=r.income_consistency,
                trip_completion=r.trip_completion,
                rating_reliability=r.rating_reliability,
                work_pattern=r.work_pattern,
                platform_diversity=r.platform_diversity,
            ),
            model_version=r.model_version,
            feature_importance=r.feature_importance,
            computed_at=r.computed_at,
        )
        for r in records
    ]

    # Determine trend
    trend = "stable"
    if len(scores) >= 2:
        if scores[0].score > scores[-1].score:
            trend = "up"
        elif scores[0].score < scores[-1].score:
            trend = "down"

    return GigScoreHistory(worker_id=worker.id, scores=scores, trend=trend)
