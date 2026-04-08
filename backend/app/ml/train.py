import joblib
import pandas as pd
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

MODEL_PATH = Path(__file__).parent / "wait_time_model.pkl"


def train_model(csv_path: str):
    """
    CSV must contain:
    queue_position, total_items, total_quantity,
    hour_of_day, day_of_week, actual_wait_time
    """

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

    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # XGBoost model with optimized parameters
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        reg_alpha=0.1,  # L1 regularization
        reg_lambda=1.0,  # L2 regularization
    )

    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"📊 Model Performance Metrics:")
    print(f"   MAE: {mae:.2f} minutes")
    print(f"   MSE: {mse:.2f}")
    print(f"   R²: {r2:.3f}")

    # Feature importance
    feature_importance = model.feature_importances_
    feature_names = X.columns
    print(f"\n🔍 Feature Importance:")
    for name, importance in zip(feature_names, feature_importance):
        print(f"   {name}: {importance:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"\n✅ XGBoost wait time model trained and saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_model("training_data.csv")
