"""Feature engineering for GigScore Random Forest model."""

import pandas as pd
import numpy as np


def engineer_features(
    worker: pd.Series,
    income_df: pd.DataFrame,
) -> dict:
    """
    Extract features from a worker's income history for GigScore prediction.

    Returns a flat dict of features ready for the model.
    """
    features = {}

    # ── Income consistency ────────────────────────────────────
    if len(income_df) > 0:
        daily_totals = income_df.groupby("date")["amount"].sum()
        features["income_mean"] = daily_totals.mean()
        features["income_std"] = daily_totals.std()
        features["income_cv"] = (
            features["income_std"] / features["income_mean"]
            if features["income_mean"] > 0
            else 1.0
        )
        features["income_median"] = daily_totals.median()
        features["income_max"] = daily_totals.max()
        features["income_min"] = daily_totals.min()
    else:
        for f in ["income_mean", "income_std", "income_cv", "income_median",
                   "income_max", "income_min"]:
            features[f] = 0.0

    # ── Trip / task completion ────────────────────────────────
    if "trips_completed" in income_df.columns:
        features["total_trips"] = income_df["trips_completed"].sum()
        features["avg_trips_per_day"] = (
            income_df.groupby("date")["trips_completed"].sum().mean()
        )
    else:
        features["total_trips"] = len(income_df)
        features["avg_trips_per_day"] = 0.0

    # ── Work pattern regularity ───────────────────────────────
    if len(income_df) > 0 and "date" in income_df.columns:
        unique_dates = income_df["date"].nunique()
        date_range = pd.to_datetime(income_df["date"])
        total_span = (date_range.max() - date_range.min()).days + 1
        features["active_day_ratio"] = unique_dates / max(total_span, 1)
        features["total_active_days"] = unique_dates
        features["total_span_days"] = total_span
    else:
        features["active_day_ratio"] = 0.0
        features["total_active_days"] = 0
        features["total_span_days"] = 0

    # ── Platform diversity ────────────────────────────────────
    if "platform" in income_df.columns:
        features["num_platforms"] = income_df["platform"].nunique()
        platform_shares = income_df.groupby("platform")["amount"].sum()
        total = platform_shares.sum()
        if total > 0:
            shares = platform_shares / total
            features["platform_entropy"] = float(
                -np.sum(shares * np.log2(shares + 1e-10))
            )
        else:
            features["platform_entropy"] = 0.0
    else:
        features["num_platforms"] = worker.get("num_platforms", 1)
        features["platform_entropy"] = 0.0

    # ── Rating ────────────────────────────────────────────────
    features["avg_rating"] = worker.get("avg_rating", 4.0)

    # ── Account maturity ──────────────────────────────────────
    features["account_age_days"] = worker.get("account_age_days", 0)

    # ── Hours worked ──────────────────────────────────────────
    if "hours_worked" in income_df.columns:
        features["avg_hours_per_day"] = (
            income_df.groupby("date")["hours_worked"].sum().mean()
        )
    else:
        features["avg_hours_per_day"] = 0.0

    return features


def features_to_dataframe(features: dict) -> pd.DataFrame:
    """Convert feature dict to a single-row DataFrame for model prediction."""
    return pd.DataFrame([features])


FEATURE_NAMES = [
    "income_mean", "income_std", "income_cv", "income_median",
    "income_max", "income_min", "total_trips", "avg_trips_per_day",
    "active_day_ratio", "total_active_days", "total_span_days",
    "num_platforms", "platform_entropy", "avg_rating",
    "account_age_days", "avg_hours_per_day",
]
