from sqlalchemy.orm import Session
from app.models.order import Order


def get_queue_length(db: Session):
    return db.query(Order).filter(
        Order.status.in_(["Pending", "Preparing"])
    ).count()


def assign_queue_position(db: Session):
    return get_queue_length(db) + 1


def normalize_queue(db: Session):
    orders = db.query(Order).filter(
        Order.status.in_(["Pending", "Preparing"])
    ).order_by(Order.created_at).all()

    for idx, order in enumerate(orders, start=1):
        order.queue_position = idx

    db.commit()
