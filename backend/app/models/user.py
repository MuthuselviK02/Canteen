from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # ADMIN | STUDENT | FACULTY | KITCHEN | etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships temporarily commented out to avoid circular imports
    # behavior_patterns = relationship(
    #     "CustomerBehaviorPattern",
    #     back_populates="user"
    # )
    # churn_predictions = relationship(
    #     "ChurnPrediction",
    #     back_populates="user"
    # )
    # invoices = relationship(
    #     "Invoice",
    #     back_populates="customer"
    # )  # Temporarily commented out
