"""GigScore Random Forest model — training pipeline."""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Add parent paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from models.gigscore.features import engineer_features, FEATURE_NAMES


def compute_target_score(features: dict) -> float:
    """
    Compute target GigScore (0–900) from features using a heuristic formula.

    This generates training labels from the feature vector. In a real system,
    the labels would come from historical loan performance or manual review.
    """
    score = 0.0

    # Income consistency (0-270 points, 30%)
    cv = features.get("income_cv", 1.0)
    income_score = max(0, 100 - cv * 100)
    score += income_score * 2.7

    # Trip completion (0-225 points, 25%)
    trips = features.get("total_trips", 0)
    trip_score = min(100, trips / 5)  # 500 trips = max
    score += trip_score * 2.25

    # Rating (0-180 points, 20%)
    rating = features.get("avg_rating", 3.0)
    rating_score = (rating - 1) / 4 * 100  # 1-5 -> 0-100
    score += rating_score * 1.8

    # Work pattern (0-135 points, 15%)
    active_ratio = features.get("active_day_ratio", 0)
    pattern_score = active_ratio * 100
    score += pattern_score * 1.35

    # Platform diversity (0-90 points, 10%)
    n_platforms = features.get("num_platforms", 1)
    diversity_score = min(100, n_platforms * 25)
    score += diversity_score * 0.9

    # Add noise to prevent perfect fit
    noise = np.random.normal(0, 20)
    score = np.clip(score + noise, 0, 900)

    return round(score, 1)


def prepare_training_data(data_dir: str) -> tuple:
    """Load synthetic data and create feature matrix + target."""
    workers_df = pd.read_csv(os.path.join(data_dir, "workers.csv"))
    income_df = pd.read_csv(os.path.join(data_dir, "income_history.csv"))

    X_rows = []
    y_rows = []

    for _, worker in workers_df.iterrows():
        worker_income = income_df[income_df["worker_id"] == worker["worker_id"]]

        features = engineer_features(worker, worker_income)
        target = compute_target_score(features)

        X_rows.append(features)
        y_rows.append(target)

    X = pd.DataFrame(X_rows)[FEATURE_NAMES]
    y = np.array(y_rows)

    return X, y


def train_model(data_dir: str, output_dir: str = None):
    """Train the GigScore Random Forest model."""
    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    print("Loading and preparing training data...")
    X, y = prepare_training_data(data_dir)
    print(f"  Dataset: {X.shape[0]} workers, {X.shape[1]} features")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train Random Forest
    print("Training Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"  MAE: {mae:.2f} (out of 900)")
    print(f"  R²:  {r2:.4f}")

    # Feature importance
    importance = dict(zip(FEATURE_NAMES, model.feature_importances_))
    sorted_importance = dict(
        sorted(importance.items(), key=lambda x: x[1], reverse=True)
    )
    print("\n  Feature Importance:")
    for feat, imp in sorted_importance.items():
        print(f"    {feat}: {imp:.4f}")

    # Save model
    model_path = os.path.join(output_dir, "gigscore_rf_model.joblib")
    joblib.dump(model, model_path)
    print(f"\n  Model saved to: {model_path}")

    # Save metadata
    metadata = {
        "model_type": "RandomForestRegressor",
        "version": "rf_v1",
        "features": FEATURE_NAMES,
        "n_estimators": 200,
        "mae": mae,
        "r2": r2,
        "feature_importance": sorted_importance,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }
    joblib.dump(metadata, os.path.join(output_dir, "gigscore_metadata.joblib"))

    return model, metadata


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic")
    train_model(data_dir)
