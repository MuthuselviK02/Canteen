from sqlalchemy import Column, Integer, ForeignKey, Float
from app.database.base import Base

class MenuItemIngredient(Base):
    """
    Placeholder for future ingredient/recipe mapping.
    Uncomment and use when you want to enable ingredient-level forecasts.
    """
    __tablename__ = "menu_item_ingredients"

    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    ingredient_name = Column(String, nullable=False)  # e.g., "Rice", "Tomato", "Chicken"
    quantity_per_unit = Column(Float, nullable=False)  # e.g., 100g per portion
    unit = Column(String, nullable=False)  # e.g., "g", "ml", "pcs"
    # Add relationships/imports when you enable this model
