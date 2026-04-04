"""GigScore prediction — loads trained model and returns score + breakdown."""

import os
import pandas as pd
import numpy as np
import joblib

from models.gigscore.features import engineer_features, features_to_dataframe, FEATURE_NAMES


class GigScorePredictor:
    """Loads the trained GigScore RF model and predicts scores."""

    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.dirname(__file__)

        model_path = os.path.join(model_dir, "gigscore_rf_model.joblib")
        metadata_path = os.path.join(model_dir, "gigscore_metadata.joblib")

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.metadata = joblib.load(metadata_path)
            self.is_loaded = True
        else:
            self.model = None
            self.metadata = None
            self.is_loaded = False
            print("Warning: No trained model found. Using heuristic fallback.")

    def predict(self, worker: dict, income_df: pd.DataFrame) -> dict:
        """
        Predict GigScore for a worker.

        Returns dict with score (0-900), sub-score breakdown, and feature importance.
        """
        worker_series = pd.Series(worker)
        features = engineer_features(worker_series, income_df)

        if self.is_loaded:
            X = features_to_dataframe(features)[FEATURE_NAMES]
            score = float(np.clip(self.model.predict(X)[0], 0, 900))
            importance = dict(zip(FEATURE_NAMES, self.model.feature_importances_))
        else:
            score = self._heuristic_score(features)
            importance = {"note": "Using heuristic — no trained model loaded"}

        # Compute sub-scores
        breakdown = self._compute_breakdown(features)

        return {
            "score": round(score, 1),
            "breakdown": breakdown,
            "features": {k: round(v, 4) if isinstance(v, float) else v
                        for k, v in features.items()},
            "feature_importance": importance,
            "model_version": self.metadata["version"] if self.metadata else "heuristic",
        }

    def _compute_breakdown(self, features: dict) -> dict:
        """Compute human-readable sub-score breakdown (each 0-100)."""
        cv = features.get("income_cv", 1.0)
        income_consistency = max(0, min(100, 100 - cv * 80))

        trips = features.get("total_trips", 0)
        trip_completion = min(100, trips / 5)

        rating = features.get("avg_rating", 3.0)
        rating_reliability = max(0, (rating - 1) / 4 * 100)

        active_ratio = features.get("active_day_ratio", 0)
        work_pattern = active_ratio * 100

        n_plat = features.get("num_platforms", 1)
        platform_diversity = min(100, n_plat * 25)

        return {
            "income_consistency": round(income_consistency, 1),
            "trip_completion": round(trip_completion, 1),
            "rating_reliability": round(rating_reliability, 1),
            "work_pattern": round(work_pattern, 1),
            "platform_diversity": round(platform_diversity, 1),
        }

    def _heuristic_score(self, features: dict) -> float:
        """Fallback heuristic scoring when model is not available."""
        score = 0.0
        cv = features.get("income_cv", 1.0)
        score += max(0, 100 - cv * 100) * 2.7
        score += min(100, features.get("total_trips", 0) / 5) * 2.25
        score += ((features.get("avg_rating", 3.0) - 1) / 4 * 100) * 1.8
        score += features.get("active_day_ratio", 0) * 100 * 1.35
        score += min(100, features.get("num_platforms", 1) * 25) * 0.9
        return np.clip(score, 0, 900)


if __name__ == "__main__":
    predictor = GigScorePredictor()

    # Test with sample worker
    sample_worker = {
        "worker_id": "W00001",
        "avg_rating": 4.5,
        "num_platforms": 3,
        "account_age_days": 365,
    }
    sample_income = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=60, freq="D").strftime("%Y-%m-%d").tolist(),
        "amount": np.random.uniform(300, 1200, 60).tolist(),
        "platform": np.random.choice(["swiggy", "zomato", "uber"], 60).tolist(),
        "trips_completed": np.random.randint(3, 15, 60).tolist(),
        "hours_worked": np.random.uniform(4, 12, 60).tolist(),
    })

    result = predictor.predict(sample_worker, sample_income)
    print(f"\nGigScore: {result['score']}/900")
    print(f"Breakdown: {result['breakdown']}")
    print(f"Model: {result['model_version']}")
