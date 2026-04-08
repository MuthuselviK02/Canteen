import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "wait_time_model.pkl"


class WaitTimeModel:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
                self.model = None
        else:
            self.model = None

    def predict(self, features: list[int]) -> int | None:
        if self.model is None:
            return None
        try:
            return int(round(self.model.predict([features])[0]))
        except Exception as e:
            print(f"Warning: Prediction failed: {e}")
            return None


# singleton instance
wait_time_model = WaitTimeModel()


def predict_wait_time(features: list[int]) -> int | None:
    return wait_time_model.predict(features)
