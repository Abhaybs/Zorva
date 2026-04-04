"""Fatigue Detector — Gradient Boosting model to detect overwork patterns."""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib


def prepare_features(fatigue_df: pd.DataFrame) -> tuple:
    """Prepare feature matrix and labels from fatigue data."""
    feature_cols = [
        "hours_worked",
        "consecutive_work_days",
        "total_distance_km",
        "avg_speed_kmh",
        "break_minutes",
        "late_night_hours",
    ]

    X = fatigue_df[feature_cols].fillna(0)
    y = fatigue_df["is_fatigued"].astype(int)

    return X, y, feature_cols


def train_model(data_dir: str, output_dir: str = None):
    """Train the fatigue detection model."""
    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    print("Loading fatigue data...")
    fatigue_df = pd.read_csv(os.path.join(data_dir, "fatigue_data.csv"))
    print(f"  Records: {len(fatigue_df)}")

    X, y, feature_cols = prepare_features(fatigue_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Gradient Boosting classifier...")
    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        min_samples_split=5,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"  Accuracy: {accuracy:.4f}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Not Fatigued", "Fatigued"]))

    # Save
    model_path = os.path.join(output_dir, "fatigue_model.joblib")
    joblib.dump(model, model_path)

    metadata = {
        "model_type": "GradientBoostingClassifier",
        "version": "gb_v1",
        "features": feature_cols,
        "accuracy": accuracy,
    }
    joblib.dump(metadata, os.path.join(output_dir, "fatigue_metadata.joblib"))
    print(f"\n  Model saved to: {model_path}")

    return model, metadata


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic")
    train_model(data_dir)
