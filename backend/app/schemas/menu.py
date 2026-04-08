from pydantic import BaseModel, Field
from typing import Optional

class MenuCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str = "main_course"  # Default to canonical key
    image_url: Optional[str] = None
    base_prep_time: int = Field(..., gt=0)
    calories: int = Field(0, ge=0)
    is_vegetarian: bool = True
    is_spicy: bool = False
    is_available: bool = True
    present_stocks: int = Field(0, ge=0)

class MenuResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: str  # This will be the category_key
    category_label: Optional[str] = None  # Display label
    image_url: Optional[str] = None
    base_prep_time: int
    calories: int
    is_vegetarian: bool
    is_spicy: bool
    is_available: bool
    present_stocks: int

    @classmethod
    def from_db_item(cls, menu_item):
        """Create response from database item with category label"""
        try:
            from app.core.categories import get_category_label
            category_label = get_category_label(menu_item.category)
        except:
            category_label = menu_item.category.replace("_", " ").title()
        
        return cls(
            id=menu_item.id,
            name=menu_item.name,
            description=menu_item.description,
            price=menu_item.price,
            category=menu_item.category,
            category_label=category_label,
            image_url=menu_item.image_url,
            base_prep_time=menu_item.base_prep_time,
            calories=menu_item.calories,
            is_vegetarian=menu_item.is_vegetarian,
            is_spicy=menu_item.is_spicy,
            is_available=menu_item.is_available,
            present_stocks=menu_item.present_stocks
        )

    class Config:
        from_attributes = True
