"""Synthetic gig worker data generator for model training and testing."""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_worker_profiles(n: int = 500) -> pd.DataFrame:
    """Generate synthetic gig worker profiles."""
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    ]
    platforms = ["swiggy", "zomato", "ola", "uber", "dunzo", "zepto", "rapido", "blinkit"]

    records = []
    for i in range(n):
        worker_platforms = random.sample(platforms, k=random.randint(1, 4))
        records.append({
            "worker_id": f"W{i:05d}",
            "city": random.choice(cities),
            "platforms": ",".join(worker_platforms),
            "num_platforms": len(worker_platforms),
            "avg_rating": round(random.uniform(3.0, 5.0), 2),
            "account_age_days": random.randint(30, 1500),
            "is_active": random.random() > 0.1,
        })
    return pd.DataFrame(records)


def generate_income_history(workers: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    """Generate synthetic daily income records for each worker."""
    records = []
    base_date = datetime.now() - timedelta(days=days)

    for _, worker in workers.iterrows():
        # Worker-specific parameters
        base_daily = random.uniform(200, 1500)  # Base daily earning capacity
        consistency = random.uniform(0.3, 0.95)  # How consistently they work
        platforms = worker["platforms"].split(",")

        for day_offset in range(days):
            # Randomly skip days based on consistency
            if random.random() > consistency:
                continue

            date = base_date + timedelta(days=day_offset)

            # Daily variation
            daily_total = base_daily * random.uniform(0.4, 1.8)

            # Split across platforms
            num_active_platforms = random.randint(1, len(platforms))
            active_platforms = random.sample(platforms, num_active_platforms)

            for platform in active_platforms:
                amount = daily_total / num_active_platforms * random.uniform(0.5, 1.5)
                trips = random.randint(1, 15)

                records.append({
                    "worker_id": worker["worker_id"],
                    "date": date.strftime("%Y-%m-%d"),
                    "platform": platform,
                    "amount": round(amount, 2),
                    "trips_completed": trips,
                    "hours_worked": round(random.uniform(2, 14), 1),
                    "source": random.choice(["screenshot_ocr", "sms_parse", "manual_entry"]),
                })

    return pd.DataFrame(records)


def generate_fatigue_data(workers: pd.DataFrame, days: int = 90) -> pd.DataFrame:
    """Generate synthetic fatigue-related data (GPS patterns, work hours, etc.)."""
    records = []
    base_date = datetime.now() - timedelta(days=days)

    for _, worker in workers.iterrows():
        for day_offset in range(days):
            if random.random() > 0.7:
                continue

            date = base_date + timedelta(days=day_offset)
            hours = round(random.uniform(2, 16), 1)
            consecutive_days = random.randint(1, 14)

            # Fatigue is more likely with high hours and many consecutive days
            fatigue_score = min(1.0, (hours / 16) * 0.5 + (consecutive_days / 14) * 0.5)
            is_fatigued = fatigue_score > 0.65

            records.append({
                "worker_id": worker["worker_id"],
                "date": date.strftime("%Y-%m-%d"),
                "hours_worked": hours,
                "consecutive_work_days": consecutive_days,
                "total_distance_km": round(random.uniform(10, 200), 1),
                "avg_speed_kmh": round(random.uniform(10, 50), 1),
                "break_minutes": random.randint(0, 120),
                "late_night_hours": round(random.uniform(0, hours * 0.4), 1),
                "fatigue_score": round(fatigue_score, 3),
                "is_fatigued": is_fatigued,
            })

    return pd.DataFrame(records)


def generate_zone_data(n_zones: int = 50, days: int = 90) -> pd.DataFrame:
    """Generate synthetic zone-level demand and earnings data."""
    # Major Indian city coordinates (approximate)
    city_coords = {
        "Mumbai": (19.076, 72.877),
        "Delhi": (28.613, 77.209),
        "Bangalore": (12.971, 77.594),
        "Hyderabad": (17.385, 78.486),
        "Chennai": (13.082, 80.270),
    }

    records = []
    base_date = datetime.now() - timedelta(days=days)

    for city, (base_lat, base_lng) in city_coords.items():
        for zone_idx in range(n_zones // len(city_coords)):
            zone_lat = base_lat + random.uniform(-0.15, 0.15)
            zone_lng = base_lng + random.uniform(-0.15, 0.15)
            zone_name = f"{city}_Z{zone_idx:03d}"

            for day_offset in range(days):
                date = base_date + timedelta(days=day_offset)
                day_of_week = date.weekday()

                for hour in [8, 12, 14, 18, 20, 22]:  # Key time slots
                    # Demand varies by time and day
                    base_demand = random.uniform(10, 100)
                    if hour in [12, 14, 20]:  # Meal times
                        base_demand *= 1.8
                    if day_of_week >= 5:  # Weekends
                        base_demand *= 1.3

                    records.append({
                        "zone_name": zone_name,
                        "city": city,
                        "latitude": round(zone_lat, 4),
                        "longitude": round(zone_lng, 4),
                        "date": date.strftime("%Y-%m-%d"),
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "demand_score": round(base_demand + random.gauss(0, 10), 1),
                        "avg_earnings_per_hour": round(random.uniform(80, 300), 2),
                        "active_workers": random.randint(5, 100),
                        "surge_multiplier": round(random.uniform(1.0, 2.5), 2),
                    })

    return pd.DataFrame(records)


def main():
    """Generate all synthetic datasets and save to CSV."""
    output_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(output_dir, exist_ok=True)

    print("Generating synthetic gig worker data...")

    # Workers
    workers = generate_worker_profiles(500)
    workers.to_csv(os.path.join(output_dir, "workers.csv"), index=False)
    print(f"  ✓ Workers: {len(workers)} profiles")

    # Income
    income = generate_income_history(workers, days=90)
    income.to_csv(os.path.join(output_dir, "income_history.csv"), index=False)
    print(f"  ✓ Income: {len(income)} records")

    # Fatigue
    fatigue = generate_fatigue_data(workers, days=90)
    fatigue.to_csv(os.path.join(output_dir, "fatigue_data.csv"), index=False)
    print(f"  ✓ Fatigue: {len(fatigue)} records")

    # Zones
    zones = generate_zone_data(50, days=90)
    zones.to_csv(os.path.join(output_dir, "zone_data.csv"), index=False)
    print(f"  ✓ Zones: {len(zones)} records")

    print("\nAll synthetic data generated successfully!")


if __name__ == "__main__":
    main()
