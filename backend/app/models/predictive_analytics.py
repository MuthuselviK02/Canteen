from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class PreparationTimePrediction(Base):
    """AI-powered preparation time predictions"""
    __tablename__ = "preparation_time_predictions"
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    predicted_time = Column(Integer, nullable=False)  # in minutes
    confidence_score = Column(Float, nullable=False)  # 0-1
    factors = Column(JSON)  # {order_volume, complexity, ingredients, etc.}
    actual_time = Column(Integer)  # actual time taken (for learning)
    prediction_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships - temporarily commented out to avoid import issues
    # menu_item = relationship("MenuItem", back_populates="prep_predictions")

class QueueForecast(Base):
    """Queue length forecasting"""
    __tablename__ = "queue_forecasts"
    
    id = Column(Integer, primary_key=True)
    predicted_time = Column(DateTime, nullable=False)  # future timestamp
    predicted_queue_length = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False)
    factors = Column(JSON)  # {day_of_week, time, weather, events, etc.}
    actual_queue_length = Column(Integer)  # actual queue (for learning)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    actual_records = relationship("QueueActual", back_populates="forecast")

class QueueActual(Base):
    """Actual queue measurements for learning"""
    __tablename__ = "queue_actuals"
    
    id = Column(Integer, primary_key=True)
    queue_length = Column(Integer, nullable=False)
    wait_time = Column(Integer, nullable=False)  # in minutes
    timestamp = Column(DateTime, default=func.now())
    forecast_id = Column(Integer, ForeignKey("queue_forecasts.id"))
    factors = Column(JSON)  # actual conditions at time
    
    # Relationships
    forecast = relationship("QueueForecast", back_populates="actual_records")

class PeakHourPrediction(Base):
    """Peak hour prediction and resource allocation"""
    __tablename__ = "peak_hour_predictions"
    
    id = Column(Integer, primary_key=True)
    prediction_date = Column(DateTime, nullable=False)
    peak_start_time = Column(DateTime, nullable=False)
    peak_end_time = Column(DateTime, nullable=False)
    predicted_orders = Column(Integer, nullable=False)
    recommended_staff = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False)
    factors = Column(JSON)  # {day_type, weather, events, etc.}
    actual_orders = Column(Integer)  # for learning
    actual_staff_needed = Column(Integer)  # for learning
    created_at = Column(DateTime, default=func.now())

class DemandForecast(Base):
    """Demand forecasting for inventory management"""
    __tablename__ = "demand_forecasts"
    
    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    predicted_quantity = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False)
    forecast_period = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    factors = Column(JSON)  # {historical_data, trends, seasonality, etc.}
    actual_quantity = Column(Integer)  # for learning
    created_at = Column(DateTime, default=func.now())
    
    # Relationships - temporarily commented out to avoid import issues
    # menu_item = relationship("MenuItem", back_populates="demand_forecasts")

class CustomerBehaviorPattern(Base):
    """Customer behavior pattern analysis"""
    __tablename__ = "customer_behavior_patterns"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pattern_type = Column(String, nullable=False)  # 'ordering_time', 'preferences', 'frequency', etc.
    pattern_data = Column(JSON, nullable=False)  # pattern details
    confidence_score = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="behavior_patterns")  # Temporarily commented out

class ChurnPrediction(Base):
    """Churn prediction for user retention"""
    __tablename__ = "churn_predictions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    churn_probability = Column(Float, nullable=False)  # 0-1
    risk_level = Column(String, nullable=False)  # 'low', 'medium', 'high', 'critical'
    risk_factors = Column(JSON)  # {last_order, frequency, complaints, etc.}
    recommended_action = Column(Text)  # retention strategy
    confidence_score = Column(Float, nullable=False)
    prediction_date = Column(DateTime, default=func.now())
    actual_churn = Column(Boolean)  # for learning
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    # user = relationship("User", back_populates="churn_predictions")  # Temporarily commented out

class RevenueForecast(Base):
    """Revenue forecasting"""
    __tablename__ = "revenue_forecasts"
    
    id = Column(Integer, primary_key=True)
    forecast_date = Column(DateTime, nullable=False)
    forecast_period = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    predicted_revenue = Column(Float, nullable=False)
    predicted_orders = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False)
    factors = Column(JSON)  # {historical_data, trends, seasonality, events, etc.}
    actual_revenue = Column(Float)  # for learning
    actual_orders = Column(Integer)  # for learning
    created_at = Column(DateTime, default=func.now())

class PredictiveModel(Base):
    """ML model metadata and performance tracking"""
    __tablename__ = "predictive_models"
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)  # 'prep_time', 'queue', 'demand', etc.
    model_version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # 'linear_regression', 'random_forest', etc.
    accuracy_score = Column(Float)
    last_trained = Column(DateTime)
    training_data_size = Column(Integer)
    parameters = Column(JSON)  # model hyperparameters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
