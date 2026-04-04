"""Earnings Zone Optimizer — predict best zones and times to work."""

import os
import numpy as np
import pandas as pd
import joblib


class EarningsOptimizer:
    """Recommends optimal zones and times for maximum earnings."""

    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.dirname(__file__)

        model_path = os.path.join(model_dir, "earnings_model.joblib")
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            self.metadata = joblib.load(
                os.path.join(model_dir, "earnings_metadata.joblib")
            )
            self.is_loaded = True
        else:
            self.model = None
            self.metadata = None
            self.is_loaded = False

    def recommend_zones(
        self,
        zones: list[dict],
        hour: int,
        day_of_week: int,
        top_n: int = 5,
    ) -> list[dict]:
        """
        Given a list of zones and a time slot, rank them by predicted earnings.

        Each zone dict should have: latitude, longitude, demand_score,
        active_workers, surge_multiplier.
        """
        if not zones:
            return []

        rows = []
        for zone in zones:
            rows.append({
                "latitude": zone["latitude"],
                "longitude": zone["longitude"],
                "hour": hour,
                "day_of_week": day_of_week,
                "demand_score": zone.get("demand_score", 50),
                "active_workers": zone.get("active_workers", 30),
                "surge_multiplier": zone.get("surge_multiplier", 1.0),
            })

        df = pd.DataFrame(rows)

        if self.is_loaded:
            predictions = self.model.predict(df)
        else:
            # Heuristic fallback
            predictions = (
                df["demand_score"] * 1.5
                + df["surge_multiplier"] * 50
                - df["active_workers"] * 0.3
            ).values

        results = []
        for i, zone in enumerate(zones):
            results.append({
                **zone,
                "predicted_earnings_per_hour": round(float(predictions[i]), 2),
                "recommendation_rank": 0,
            })

        results.sort(key=lambda x: x["predicted_earnings_per_hour"], reverse=True)
        for rank, r in enumerate(results[:top_n], 1):
            r["recommendation_rank"] = rank

        return results[:top_n]

    def best_hours(self, latitude: float, longitude: float, day_of_week: int) -> list[dict]:
        """Predict the best hours to work at a given location."""
        hours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        results = []

        for hour in hours:
            features = {
                "latitude": latitude,
                "longitude": longitude,
                "hour": hour,
                "day_of_week": day_of_week,
                "demand_score": 50,
                "active_workers": 30,
                "surge_multiplier": 1.0,
            }

            if self.is_loaded:
                df = pd.DataFrame([features])
                predicted = float(self.model.predict(df)[0])
            else:
                # Time-based heuristic (meal times = high earnings)
                if hour in [12, 13, 14]:
                    predicted = 200 + np.random.uniform(0, 80)
                elif hour in [19, 20, 21]:
                    predicted = 220 + np.random.uniform(0, 100)
                elif hour in [8, 9]:
                    predicted = 150 + np.random.uniform(0, 50)
                else:
                    predicted = 100 + np.random.uniform(0, 60)

            results.append({
                "hour": hour,
                "predicted_earnings_per_hour": round(predicted, 2),
                "label": f"{hour:02d}:00",
            })

        results.sort(key=lambda x: x["predicted_earnings_per_hour"], reverse=True)
        return results


if __name__ == "__main__":
    optimizer = EarningsOptimizer()

    sample_zones = [
        {"zone_name": "Koramangala", "latitude": 12.935, "longitude": 77.624,
         "demand_score": 85, "active_workers": 40, "surge_multiplier": 1.5},
        {"zone_name": "Indiranagar", "latitude": 12.978, "longitude": 77.640,
         "demand_score": 70, "active_workers": 25, "surge_multiplier": 1.2},
        {"zone_name": "HSR Layout", "latitude": 12.912, "longitude": 77.638,
         "demand_score": 60, "active_workers": 35, "surge_multiplier": 1.0},
    ]

    print("Zone Recommendations (Friday 8 PM):")
    recs = optimizer.recommend_zones(sample_zones, hour=20, day_of_week=4)
    for r in recs:
        print(f"  #{r['recommendation_rank']} {r['zone_name']}: ₹{r['predicted_earnings_per_hour']}/hr")

    print("\nBest Hours (Koramangala, Monday):")
    hours = optimizer.best_hours(12.935, 77.624, day_of_week=0)
    for h in hours[:5]:
        print(f"  {h['label']} → ₹{h['predicted_earnings_per_hour']}/hr")
