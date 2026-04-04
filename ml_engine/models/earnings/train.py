"""Earnings Zone Optimizer — trains a model to predict high-demand zones/times."""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


def prepare_features(zone_df: pd.DataFrame) -> tuple:
    """Prepare features from zone data."""
    feature_cols = [
        "latitude", "longitude", "hour", "day_of_week",
        "demand_score", "active_workers", "surge_multiplier",
    ]

    X = zone_df[feature_cols].fillna(0)
    y = zone_df["avg_earnings_per_hour"]

    return X, y, feature_cols


def train_model(data_dir: str, output_dir: str = None):
    """Train the earnings zone optimizer."""
    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    print("Loading zone data...")
    zone_df = pd.read_csv(os.path.join(data_dir, "zone_data.csv"))
    print(f"  Records: {len(zone_df)}")

    X, y, feature_cols = prepare_features(zone_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training Gradient Boosting regressor for earnings prediction...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        min_samples_split=5,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"  MAE: ₹{mae:.2f}/hr")
    print(f"  R²:  {r2:.4f}")

    model_path = os.path.join(output_dir, "earnings_model.joblib")
    joblib.dump(model, model_path)

    metadata = {
        "model_type": "GradientBoostingRegressor",
        "version": "gb_v1",
        "features": feature_cols,
        "mae": mae,
        "r2": r2,
    }
    joblib.dump(metadata, os.path.join(output_dir, "earnings_metadata.joblib"))
    print(f"\n  Model saved to: {model_path}")

    return model, metadata


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic")
    train_model(data_dir)
