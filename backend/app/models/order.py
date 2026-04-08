from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="Pending")
    queue_position = Column(Integer)
    predicted_wait_time = Column(Integer)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_preparation_at = Column(DateTime, nullable=True)
    ready_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    invoice_id = Column(String, nullable=True)  # Add invoice_id field

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    # invoice = relationship(
    #     "Invoice",
    #     back_populates="order"
    # )  # Temporarily commented out
