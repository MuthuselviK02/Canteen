from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from app.database.base import Base

class QueueSnapshot(Base):
    __tablename__ = "queue_snapshot"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    queue_length = Column(Integer)
    hour = Column(Integer)
    day_of_week = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
