from datetime import datetime


def extract_features(
    *,
    queue_position: int,
    total_items: int,
    total_quantity: int,
    created_at: datetime,
):
    """
    Convert runtime order data into ML feature vector.
    Keep this SIMPLE for v1.
    """

    hour_of_day = created_at.hour
    day_of_week = created_at.weekday()

    return [
        queue_position,
        total_items,
        total_quantity,
        hour_of_day,
        day_of_week,
    ]
