from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String, default="main_course")  # Store category_key
    image_url = Column(String)
    base_prep_time = Column(Integer)
    calories = Column(Integer)
    is_vegetarian = Column(Boolean, default=True)
    is_spicy = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    present_stocks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships - temporarily commented out to avoid import issues
    # prep_predictions = relationship(
    #     "PreparationTimePrediction",
    #     back_populates="menu_item"
    # )
    # demand_forecasts = relationship(
    #     "DemandForecast",
    #     back_populates="menu_item"
    # )

    def get_category_label(self) -> str:
        """Get display label for this category"""
        from app.core.categories import get_category_label
        return get_category_label(self.category)
    
    def set_category(self, category_input: str):
        """Set category using migration logic"""
        from app.core.categories import migrate_legacy_category
        self.category = migrate_legacy_category(category_input)
