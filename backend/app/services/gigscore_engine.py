"""GigScore Engine — computes gig worker credit score using heuristics / ML model."""

from __future__ import annotations
import random
from typing import Any


class GigScoreEngine:
    """
    Computes a GigScore (0–900) for a gig worker.

    In production, this loads a trained Random Forest model from the ML engine.
    For development, it uses heuristic scoring based on income patterns.
    """

    MAX_SCORE = 900

    def compute(self, worker: Any, income_records: list) -> dict:
        """
        Compute the GigScore from worker profile + income history.

        Returns a dict with score, breakdown, model_version, and feature_importance.
        """
        # ── Feature extraction ────────────────────────────────
        income_consistency = self._income_consistency(income_records)
        trip_completion = self._trip_completion(income_records)
        rating_reliability = self._rating_reliability(worker)
        work_pattern = self._work_pattern(income_records)
        platform_diversity = self._platform_diversity(income_records)

        # ── Weighted score (heuristic — replaced by RF in prod) ─
        weights = {
            "income_consistency": 0.30,
            "trip_completion": 0.25,
            "rating_reliability": 0.20,
            "work_pattern": 0.15,
            "platform_diversity": 0.10,
        }

        weighted_sum = (
            income_consistency * weights["income_consistency"]
            + trip_completion * weights["trip_completion"]
            + rating_reliability * weights["rating_reliability"]
            + work_pattern * weights["work_pattern"]
            + platform_diversity * weights["platform_diversity"]
        )

        score = round(weighted_sum / 100 * self.MAX_SCORE, 1)
        score = max(0, min(self.MAX_SCORE, score))

        return {
            "score": score,
            "breakdown": {
                "income_consistency": round(income_consistency, 1),
                "trip_completion": round(trip_completion, 1),
                "rating_reliability": round(rating_reliability, 1),
                "work_pattern": round(work_pattern, 1),
                "platform_diversity": round(platform_diversity, 1),
            },
            "model_version": "heuristic_v1",
            "feature_importance": weights,
        }

    # ── Sub-score calculators ─────────────────────────────────

    def _income_consistency(self, records: list) -> float:
        """Score based on regularity and variance of earnings."""
        if not records:
            return 20.0  # Minimal score for no data

        amounts = [r.amount for r in records]
        if len(amounts) < 3:
            return 40.0

        avg = sum(amounts) / len(amounts)
        variance = sum((a - avg) ** 2 for a in amounts) / len(amounts)
        cv = (variance ** 0.5) / avg if avg > 0 else 1.0  # coefficient of variation

        # Lower CV = more consistent = higher score
        if cv < 0.2:
            return 95.0
        elif cv < 0.4:
            return 80.0
        elif cv < 0.6:
            return 65.0
        elif cv < 0.8:
            return 50.0
        else:
            return 35.0

    def _trip_completion(self, records: list) -> float:
        """Score based on volume of completed trips/tasks."""
        count = len(records)
        if count >= 200:
            return 95.0
        elif count >= 100:
            return 80.0
        elif count >= 50:
            return 65.0
        elif count >= 20:
            return 50.0
        elif count >= 5:
            return 35.0
        else:
            return 20.0

    def _rating_reliability(self, worker: Any) -> float:
        """
        Score based on platform ratings.
        Placeholder — in prod, pulled from worker profile / screenshots.
        """
        return round(random.uniform(60, 95), 1)

    def _work_pattern(self, records: list) -> float:
        """Score based on work regularity and time distribution."""
        if not records:
            return 20.0

        # Check date spread
        dates = sorted(set(r.earned_at.date() for r in records if r.earned_at))
        if len(dates) < 2:
            return 30.0

        total_days = (dates[-1] - dates[0]).days + 1
        active_ratio = len(dates) / total_days if total_days > 0 else 0

        if active_ratio >= 0.8:
            return 90.0
        elif active_ratio >= 0.6:
            return 75.0
        elif active_ratio >= 0.4:
            return 60.0
        elif active_ratio >= 0.2:
            return 45.0
        else:
            return 30.0

    def _platform_diversity(self, records: list) -> float:
        """Score based on number of distinct platforms used."""
        if not records:
            return 20.0

        platforms = set(r.platform.value for r in records if r.platform)
        count = len(platforms)

        if count >= 4:
            return 95.0
        elif count == 3:
            return 80.0
        elif count == 2:
            return 60.0
        else:
            return 40.0
