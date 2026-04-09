from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(gt=0)


class UserInfo(BaseModel):
    id: int
    fullname: str
    email: str

    class Config:
        from_attributes = True


class MenuItemInfo(BaseModel):
    id: int
    name: str
    price: float
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    menu_item: Optional[MenuItemInfo] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(min_length=1)
    available_time: int | None = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    queue_position: int | None
    predicted_wait_time: int | None
    created_at: datetime
    started_preparation_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    user: Optional[UserInfo] = None
    invoice_id: Optional[str] = None

    class Config:
        from_attributes = True
