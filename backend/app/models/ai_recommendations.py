from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from datetime import datetime
from app.database.base import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preference_type = Column(String(50), nullable=False)  # 'category', 'spice_level', 'dietary'
    preference_value = Column(String(100), nullable=False)
    weight = Column(Float, default=1.0)  # Importance weight (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # 'view', 'order', 'favorite', 'rating'
    interaction_value = Column(Float)  # Rating score, order count, etc.
    context_data = Column(JSON)  # Time, weather, mood context
    created_at = Column(DateTime, default=datetime.utcnow)

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    recommendation_type = Column(String(50), nullable=False)  # 'preference', 'time_based', 'combo'
    confidence_score = Column(Float, nullable=False)  # 0-1 confidence
    reasoning = Column(Text)  # AI reasoning explanation
    context = Column(JSON)  # Context data used for recommendation
    is_accepted = Column(Boolean, default=None)  # User accepted/rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When recommendation expires
