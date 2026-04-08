#!/usr/bin/env python3
"""
Model validation script to compare RandomForest vs XGBoost performance
Run this before and after migration to ensure performance improvement
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import time

# Model paths
XGBOOST_MODEL_PATH = Path(__file__).parent / "wait_time_model.pkl"
RF_MODEL_PATH = Path(__file__).parent / "wait_time_model_rf_backup.pkl"
TRAINING_DATA_PATH = Path(__file__).parent.parent.parent / "training_data.csv"


def load_data(csv_path: str):
    """Load and prepare training data"""
    if not Path(csv_path).exists():
        print(f"Training data not found at {csv_path}")
        print("Please ensure training_data.csv exists with the required columns:")
        print("queue_position, total_items, total_quantity, hour_of_day, day_of_week, actual_wait_time")
        return None, None
    
    df = pd.read_csv(csv_path)
    
    X = df[
        [
            "queue_position",
            "total_items", 
            "total_quantity",
            "hour_of_day",
            "day_of_week",
        ]
    ]
    
    y = df["actual_wait_time"]
    
    return X, y


def train_random_forest(X_train, y_train):
    """Train RandomForest model for comparison"""
    print("Training RandomForest model...")
    start_time = time.time()
    
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    )
    
    rf_model.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    # Save backup
    joblib.dump(rf_model, RF_MODEL_PATH)
    
    return rf_model, training_time


def train_xgboost(X_train, y_train):
    """Train XGBoost model"""
    print("Training XGBoost model...")
    start_time = time.time()
    
    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        reg_alpha=0.1,
        reg_lambda=1.0,
    )
    
    xgb_model.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    return xgb_model, training_time


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model performance"""
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring='neg_mean_absolute_error')
    cv_mae = -cv_scores.mean()
    
    return {
        'model': model_name,
        'mae': mae,
        'mse': mse,
        'r2': r2,
        'cv_mae': cv_mae,
        'cv_std': cv_scores.std()
    }


def compare_models():
    """Compare RandomForest vs XGBoost performance"""
    print("Model Comparison: RandomForest vs XGBoost")
    print("=" * 50)
    
    # Load data
    X, y = load_data(TRAINING_DATA_PATH)
    if X is None:
        return
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
    print(f"Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    print()
    
    # Train models
    rf_model, rf_time = train_random_forest(X_train, y_train)
    xgb_model, xgb_time = train_xgboost(X_train, y_train)
    
    # Evaluate models
    rf_metrics = evaluate_model(rf_model, X_test, y_test, "RandomForest")
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
    
    # Print comparison
    print("\nPerformance Comparison:")
    print("-" * 60)
    print(f"{'Metric':<15} {'RandomForest':<15} {'XGBoost':<15} {'Improvement':<15}")
    print("-" * 60)
    
    metrics_to_compare = ['mae', 'mse', 'r2', 'cv_mae']
    for metric in metrics_to_compare:
        rf_val = rf_metrics[metric]
        xgb_val = xgb_metrics[metric]
        
        if metric == 'r2':
            improvement = ((xgb_val - rf_val) / rf_val) * 100
            improvement_str = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
        else:
            improvement = ((rf_val - xgb_val) / rf_val) * 100
            improvement_str = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
        
        print(f"{metric.upper():<15} {rf_val:<15.3f} {xgb_val:<15.3f} {improvement_str:<15}")
    
    print(f"\nTraining Time:")
    print(f"   RandomForest: {rf_time:.2f}s")
    print(f"   XGBoost: {xgb_time:.2f}s")
    print(f"   Speed Improvement: {((rf_time - xgb_time) / rf_time) * 100:.1f}%")
    
    # Feature importance comparison
    print(f"\nFeature Importance:")
    print("-" * 40)
    
    feature_names = X.columns
    
    print("RandomForest:")
    for name, importance in zip(feature_names, rf_model.feature_importances_):
        print(f"   {name}: {importance:.3f}")
    
    print("\nXGBoost:")
    for name, importance in zip(feature_names, xgb_model.feature_importances_):
        print(f"   {name}: {importance:.3f}")
    
    # Recommendation
    print(f"\nRecommendation:")
    if xgb_metrics['mae'] < rf_metrics['mae']:
        print("XGBoost shows better performance - proceed with migration!")
    else:
        print("RandomForest performs better - consider tuning XGBoost parameters")
    
    if xgb_time < rf_time:
        print("XGBoost trains faster - better for production!")
    
    return rf_metrics, xgb_metrics


def test_current_model():
    """Test the currently deployed model"""
    print("Testing Current Deployed Model")
    print("=" * 40)
    
    if not XGBOOST_MODEL_PATH.exists():
        print("No model found. Please train the model first.")
        return
    
    # Load model
    model = joblib.load(XGBOOST_MODEL_PATH)
    
    # Load test data
    X, y = load_data(TRAINING_DATA_PATH)
    if X is None:
        return
    
    # Test with sample predictions
    sample_features = [
        [1, 2, 3, 12, 1],  # queue_position=1, total_items=2, total_quantity=3, hour=12, day=1
        [5, 4, 8, 13, 2],  # queue_position=5, total_items=4, total_quantity=8, hour=13, day=2
        [10, 1, 2, 19, 4], # queue_position=10, total_items=1, total_quantity=2, hour=19, day=4
    ]
    
    print("Sample Predictions:")
    for i, features in enumerate(sample_features, 1):
        prediction = model.predict([features])[0]
        print(f"   Sample {i}: {prediction:.1f} minutes")
    
    print("Model is working correctly!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_current_model()
    else:
        compare_models()
