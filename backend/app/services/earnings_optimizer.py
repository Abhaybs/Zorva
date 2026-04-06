"""Earnings Optimizer Service — wraps ML model for zone/time recommendations."""

from __future__ import annotations

import math
import os
import sys
from datetime import datetime, timezone

# ── Seed zone data ──────────────────────────────────────────────────────────
SEED_ZONES = [
    # Mumbai
    {"zone_name": "Andheri",         "city": "Mumbai",    "latitude": 19.1136, "longitude": 72.8697, "demand_score": 104, "active_workers": 45, "surge_multiplier": 1.5},
    {"zone_name": "Bandra",          "city": "Mumbai",    "latitude": 19.0596, "longitude": 72.8295, "demand_score": 115, "active_workers": 38, "surge_multiplier": 1.8},
    {"zone_name": "Powai",           "city": "Mumbai",    "latitude": 19.1176, "longitude": 72.9060, "demand_score": 88,  "active_workers": 22, "surge_multiplier": 1.3},
    # Bengaluru
    {"zone_name": "MG Road",         "city": "Bengaluru", "latitude": 12.9757, "longitude": 77.6077, "demand_score": 143, "active_workers": 70, "surge_multiplier": 2.0},
    {"zone_name": "Koramangala",     "city": "Bengaluru", "latitude": 12.9352, "longitude": 77.6245, "demand_score": 138, "active_workers": 58, "surge_multiplier": 1.9},
    {"zone_name": "Electronic City", "city": "Bengaluru", "latitude": 12.8399, "longitude": 77.6770, "demand_score": 125, "active_workers": 62, "surge_multiplier": 1.8},
    {"zone_name": "Indiranagar",     "city": "Bengaluru", "latitude": 12.9784, "longitude": 77.6408, "demand_score": 127, "active_workers": 42, "surge_multiplier": 1.7},
    {"zone_name": "HSR Layout",      "city": "Bengaluru", "latitude": 12.9116, "longitude": 77.6389, "demand_score": 118, "active_workers": 39, "surge_multiplier": 1.6},
    {"zone_name": "Marathahalli",    "city": "Bengaluru", "latitude": 12.9591, "longitude": 77.6972, "demand_score": 112, "active_workers": 47, "surge_multiplier": 1.6},
    {"zone_name": "JP Nagar",        "city": "Bengaluru", "latitude": 12.8975, "longitude": 77.5950, "demand_score": 105, "active_workers": 33, "surge_multiplier": 1.5},
    {"zone_name": "Bellandur",       "city": "Bengaluru", "latitude": 12.9264, "longitude": 77.6760, "demand_score": 108, "active_workers": 44, "surge_multiplier": 1.5},
    {"zone_name": "Whitefield",      "city": "Bengaluru", "latitude": 12.9698, "longitude": 77.7499, "demand_score": 98,  "active_workers": 35, "surge_multiplier": 1.4},
    {"zone_name": "Malleshwaram",    "city": "Bengaluru", "latitude": 13.0035, "longitude": 77.5642, "demand_score": 91,  "active_workers": 28, "surge_multiplier": 1.3},
    {"zone_name": "Jayanagar",       "city": "Bengaluru", "latitude": 12.9249, "longitude": 77.5932, "demand_score": 88,  "active_workers": 25, "surge_multiplier": 1.3},
    {"zone_name": "Hebbal",          "city": "Bengaluru", "latitude": 13.0358, "longitude": 77.5970, "demand_score": 82,  "active_workers": 22, "surge_multiplier": 1.2},
    # Delhi
    {"zone_name": "Connaught Pl",    "city": "Delhi",     "latitude": 28.6315, "longitude": 77.2167, "demand_score": 130, "active_workers": 70, "surge_multiplier": 1.9},
    {"zone_name": "Saket",           "city": "Delhi",     "latitude": 28.5244, "longitude": 77.2066, "demand_score": 91,  "active_workers": 42, "surge_multiplier": 1.3},
    # Chennai
    {"zone_name": "Anna Nagar",      "city": "Chennai",   "latitude": 13.0850, "longitude": 80.2101, "demand_score": 83,  "active_workers": 30, "surge_multiplier": 1.2},
    {"zone_name": "T. Nagar",        "city": "Chennai",   "latitude": 13.0418, "longitude": 80.2341, "demand_score": 109, "active_workers": 55, "surge_multiplier": 1.6},
]


def _filter_nearby(zones: list[dict], lat: float, lng: float, radius_km: float) -> list[dict]:
    """Return zones within radius_km of given coordinates using Haversine."""
    R = 6371.0
    result = []
    for z in zones:
        dlat = math.radians(z["latitude"] - lat)
        dlng = math.radians(z["longitude"] - lng)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat))
             * math.cos(math.radians(z["latitude"]))
             * math.sin(dlng / 2) ** 2)
        dist = R * 2 * math.asin(math.sqrt(a))
        if dist <= radius_km:
            result.append(z)
    return result


class EarningsOptimizerService:
    """Thin service that wraps the ML EarningsOptimizer with a heuristic fallback."""

    def __init__(self) -> None:
        self._optimizer = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            ml_engine_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml_engine")
            )
            if ml_engine_path not in sys.path:
                sys.path.insert(0, ml_engine_path)
            from models.earnings.predict import EarningsOptimizer  # type: ignore
            model_dir = os.path.join(ml_engine_path, "models", "earnings")
            self._optimizer = EarningsOptimizer(model_dir=model_dir)
        except Exception:
            self._optimizer = None

    # ── Public API ────────────────────────────────────────────────────────────

    def recommend_zones(self, top_n: int = 5, lat: float | None = None, lng: float | None = None) -> list[dict]:
        """Return top N zones ranked by predicted Rs/hr, filtered to user's city if lat/lng provided."""
        now = datetime.now(timezone.utc)
        hour = now.hour
        dow = now.weekday()

        zones = SEED_ZONES
        if lat is not None and lng is not None:
            nearby = _filter_nearby(zones, lat, lng, radius_km=50)
            if nearby:
                zones = nearby
            # else: fallback to all zones

        if self._optimizer is not None:
            results = self._optimizer.recommend_zones(zones, hour, dow, top_n=top_n)
        else:
            results = self._heuristic_zones(zones, hour, dow, top_n)

        return results

    def best_hours(self, zone_name: str) -> list[dict]:
        """Return hours 6-23 ranked by predicted Rs/hr for the named zone."""
        zone = next((z for z in SEED_ZONES if z["zone_name"].lower() == zone_name.lower()), None)
        if zone is None:
            zone = SEED_ZONES[0]

        now = datetime.now(timezone.utc)
        dow = now.weekday()

        if self._optimizer is not None:
            return self._optimizer.best_hours(zone["latitude"], zone["longitude"], dow)
        else:
            return self._heuristic_hours()

    # ── Deterministic heuristic fallback ─────────────────────────────────────

    @staticmethod
    def _heuristic_zones(zones: list[dict], hour: int, dow: int, top_n: int) -> list[dict]:
        results = []
        for z in zones:
            base = z["demand_score"] * 1.5 + z["surge_multiplier"] * 50 - z["active_workers"] * 0.3
            if hour in [12, 13, 14, 19, 20, 21]:
                base += 40
            results.append({
                **z,
                "predicted_earnings_per_hour": round(base, 2),
                "recommendation_rank": 0,
            })
        results.sort(key=lambda x: x["predicted_earnings_per_hour"], reverse=True)
        for i, r in enumerate(results[:top_n], 1):
            r["recommendation_rank"] = i
        return results[:top_n]

    @staticmethod
    def _heuristic_hours() -> list[dict]:
        peak = {12: 210, 13: 225, 14: 200, 19: 240, 20: 255, 21: 230, 8: 170, 9: 160}
        results = []
        for h in range(6, 24):
            pred = peak.get(h, 110 + (h % 3) * 15)
            results.append({
                "hour": h,
                "label": f"{h:02d}:00",
                "predicted_earnings_per_hour": float(pred),
            })
        results.sort(key=lambda x: x["predicted_earnings_per_hour"], reverse=True)
        return results


# ── Singleton ─────────────────────────────────────────────────────────────────
_optimizer_service: EarningsOptimizerService | None = None


def get_optimizer() -> EarningsOptimizerService:
    global _optimizer_service
    if _optimizer_service is None:
        _optimizer_service = EarningsOptimizerService()
    return _optimizer_service
