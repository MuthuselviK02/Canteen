from datetime import datetime


def current_hour() -> int:
    return datetime.utcnow().hour


def current_day_of_week() -> int:
    """
    Monday = 0, Sunday = 6
    """
    return datetime.utcnow().weekday()
