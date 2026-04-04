"""Fatigue Detector — prediction interface."""

import os
import numpy as np
import joblib


class FatiguePredictor:
    """Predicts fatigue risk level and provides recommendations."""

    RISK_LEVELS = {
        0: {"level": "low", "emoji": "🟢", "recommendation": "You're doing well. Keep up the healthy work pattern."},
        1: {"level": "medium", "emoji": "🟡", "recommendation": "Consider taking a break soon. You've been working extended hours."},
        2: {"level": "high", "emoji": "🔴", "recommendation": "Please take a rest. Fatigue increases accident risk significantly."},
    }

    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.dirname(__file__)

        model_path = os.path.join(model_dir, "fatigue_model.joblib")
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.metadata = joblib.load(
                os.path.join(model_dir, "fatigue_metadata.joblib")
            )
            self.is_loaded = True
        else:
            self.model = None
            self.metadata = None
            self.is_loaded = False

    def predict(
        self,
        hours_worked: float,
        consecutive_work_days: int,
        total_distance_km: float,
        avg_speed_kmh: float,
        break_minutes: int,
        late_night_hours: float,
    ) -> dict:
        """
        Predict fatigue risk level.

        Returns risk level (low/medium/high), confidence, and recommendation.
        """
        features = np.array([[
            hours_worked,
            consecutive_work_days,
            total_distance_km,
            avg_speed_kmh,
            break_minutes,
            late_night_hours,
        ]])

        if self.is_loaded:
            prob = self.model.predict_proba(features)[0]
            is_fatigued = bool(self.model.predict(features)[0])
            confidence = float(max(prob))
        else:
            # Heuristic fallback
            fatigue_score = (
                (hours_worked / 16) * 0.35
                + (consecutive_work_days / 14) * 0.25
                + (late_night_hours / hours_worked if hours_worked > 0 else 0) * 0.2
                + max(0, 1 - break_minutes / 60) * 0.2
            )
            is_fatigued = fatigue_score > 0.6
            confidence = fatigue_score

        # Determine risk level
        if not is_fatigued and confidence < 0.7:
            risk_key = 0
        elif is_fatigued and confidence > 0.8:
            risk_key = 2
        else:
            risk_key = 1

        risk = self.RISK_LEVELS[risk_key]

        return {
            "is_fatigued": is_fatigued,
            "risk_level": risk["level"],
            "risk_emoji": risk["emoji"],
            "confidence": round(confidence, 3),
            "recommendation": risk["recommendation"],
            "input_summary": {
                "hours_worked": hours_worked,
                "consecutive_days": consecutive_work_days,
                "distance_km": total_distance_km,
                "break_minutes": break_minutes,
            },
            "model_version": self.metadata["version"] if self.metadata else "heuristic",
        }


if __name__ == "__main__":
    predictor = FatiguePredictor()

    # Test cases
    test_cases = [
        {"hours_worked": 4, "consecutive_work_days": 2, "total_distance_km": 30,
         "avg_speed_kmh": 25, "break_minutes": 60, "late_night_hours": 0},
        {"hours_worked": 10, "consecutive_work_days": 6, "total_distance_km": 120,
         "avg_speed_kmh": 30, "break_minutes": 20, "late_night_hours": 2},
        {"hours_worked": 14, "consecutive_work_days": 12, "total_distance_km": 200,
         "avg_speed_kmh": 20, "break_minutes": 5, "late_night_hours": 5},
    ]

    for i, tc in enumerate(test_cases):
        result = predictor.predict(**tc)
        print(f"\nTest {i+1}: {result['risk_emoji']} {result['risk_level'].upper()}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Recommendation: {result['recommendation']}")
