"""Earnings Optimizer API — zone recommendations and best working hours."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.auth.supabase import get_current_user
from app.services.earnings_optimizer import get_optimizer, SEED_ZONES

router = APIRouter()


@router.get("/zones")
async def recommend_zones(
    top_n: int = Query(5, ge=1, le=10),
    lat: Optional[float] = Query(None, description="User latitude"),
    lng: Optional[float] = Query(None, description="User longitude"),
    user: dict = Depends(get_current_user),
):
    """Return top zones ranked by predicted ₹/hr, filtered to the user's city if lat/lng provided."""
    optimizer = get_optimizer()
    zones = optimizer.recommend_zones(top_n=top_n, lat=lat, lng=lng)
    return {
        "zones": zones,
        "zone_count": len(zones),
    }


@router.get("/best-hours")
async def best_hours(
    zone: str = Query(..., description="Zone name, e.g. 'Andheri'"),
    user: dict = Depends(get_current_user),
):
    """Return hours 6am–11pm ranked by predicted ₹/hr for a given zone."""
    optimizer = get_optimizer()
    hours = optimizer.best_hours(zone_name=zone)
    # Return top 5 and full list separately for UI convenience
    return {
        "zone": zone,
        "top_hours": hours[:5],
        "all_hours": hours,
    }


@router.get("/zones/list")
async def list_zones(user: dict = Depends(get_current_user)):
    """Return the full list of available zone names for the client dropdown."""
    return {
        "zones": [
            {"zone_name": z["zone_name"], "city": z["city"]}
            for z in SEED_ZONES
        ]
    }
