"""Insurance Engine API — micro-insurance plans, subscriptions, and claims."""

from __future__ import annotations
import uuid
from datetime import datetime, date, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.supabase import get_current_user
from app.models.worker import Worker
from app.models.insurance import InsurancePolicy, InsuranceType, PolicyStatus
from app.schemas.insurance import (
    InsurancePlanOut,
    InsuranceSubscribeRequest,
    InsuranceClaimRequest,
    InsurancePolicyOut,
)
from app.services.worker_resolver import resolve_worker_for_user

router = APIRouter()

# ── Static micro-insurance plans (would come from provider API in prod) ──
AVAILABLE_PLANS = [
    InsurancePlanOut(
        id="plan_accident_basic",
        insurance_type="accident",
        provider="Zorva SafeNet",
        plan_name="Accident Shield — Basic",
        premium_daily=5.0,
        coverage_amount=100_000.0,
        description="Daily accident protection covering hospitalization up to ₹1,00,000",
    ),
    InsurancePlanOut(
        id="plan_accident_pro",
        insurance_type="accident",
        provider="Zorva SafeNet",
        plan_name="Accident Shield — Pro",
        premium_daily=12.0,
        coverage_amount=500_000.0,
        description="Comprehensive accident protection with ₹5,00,000 coverage + ambulance",
    ),
    InsurancePlanOut(
        id="plan_health_daily",
        insurance_type="health",
        provider="Zorva HealthGuard",
        plan_name="Daily Health Cover",
        premium_daily=8.0,
        coverage_amount=200_000.0,
        description="OPD + hospitalization cover ₹2,00,000 per incident",
    ),
    InsurancePlanOut(
        id="plan_income_protect",
        insurance_type="income_protection",
        provider="Zorva IncomeShield",
        plan_name="Income Protection",
        premium_daily=10.0,
        coverage_amount=50_000.0,
        description="Covers lost income during injury/illness — up to ₹50,000/month",
    ),
    InsurancePlanOut(
        id="plan_vehicle_basic",
        insurance_type="vehicle",
        provider="Zorva AutoGuard",
        plan_name="Vehicle Damage Cover",
        premium_daily=7.0,
        coverage_amount=150_000.0,
        description="Covers vehicle repair costs up to ₹1,50,000 per incident",
    ),
]

_PLANS_MAP = {p.id: p for p in AVAILABLE_PLANS}


@router.get("/plans", response_model=list[InsurancePlanOut])
async def list_plans(user: dict = Depends(get_current_user)):
    """List available micro-insurance plans."""
    return AVAILABLE_PLANS


@router.post("/subscribe", response_model=InsurancePolicyOut, status_code=201)
async def subscribe(
    payload: InsuranceSubscribeRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe a worker to an insurance plan."""
    plan = _PLANS_MAP.get(payload.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Verify worker exists
    result = await db.execute(
        select(Worker).where(Worker.id == payload.worker_id)
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    policy = InsurancePolicy(
        worker_id=worker.id,
        insurance_type=InsuranceType(plan.insurance_type),
        provider=plan.provider,
        plan_name=plan.plan_name,
        premium_daily=plan.premium_daily,
        coverage_amount=plan.coverage_amount,
        start_date=payload.start_date,
        end_date=payload.start_date + timedelta(days=30),  # 30-day policy
        status=PolicyStatus.ACTIVE,
    )
    db.add(policy)
    await db.flush()
    await db.refresh(policy)
    return policy


@router.post("/claim")
async def file_claim(
    payload: InsuranceClaimRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """File a claim against an active policy."""
    result = await db.execute(
        select(InsurancePolicy).where(InsurancePolicy.id == payload.policy_id)
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.status != PolicyStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Policy is {policy.status.value}")

    if payload.claim_amount > policy.coverage_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Claim ₹{payload.claim_amount} exceeds coverage ₹{policy.coverage_amount}",
        )

    # Mark as claimed (simplified — real system would have claims table)
    policy.status = PolicyStatus.CLAIMED
    await db.flush()

    return {
        "message": "Claim filed successfully",
        "policy_id": str(policy.id),
        "claim_amount": payload.claim_amount,
        "status": "under_review",
    }


@router.get("/my-policies", response_model=list[InsurancePolicyOut])
async def my_policies(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all policies for the authenticated worker."""
    worker = await resolve_worker_for_user(db, user)

    policies_result = await db.execute(
        select(InsurancePolicy)
        .where(InsurancePolicy.worker_id == worker.id)
        .order_by(InsurancePolicy.created_at.desc())
    )
    return policies_result.scalars().all()
