from pydantic import BaseModel
from typing import Optional, Literal


class InventoryCreate(BaseModel):
    menu_item_id: int
    stock_quantity: int


class InventoryUpdate(BaseModel):
    stock_quantity: int


class InventoryResponse(BaseModel):
    id: int
    menu_item_id: int
    stock_quantity: int

    class Config:
        from_attributes = True


class InventoryDashboardItem(BaseModel):
    item_id: int
    item_name: str
    category: str
    opening_stock: int
    completed_orders_today: int
    remaining_stock: int
    predicted_future_demand: int | None
    projected_stock: int | None
    suggested_stock_to_add: int
    days_of_supply: float | None
    inventory_status: Literal["Out of Stock", "Needs Restocking", "Well Stocked", "No Forecast"]
    risk_level: Literal["Low", "Medium", "High", "Unknown"]


class InventoryDashboardKPIs(BaseModel):
    total_items: int
    well_stocked: int
    needs_restocking: int
    out_of_stock: int
    no_forecast: int
    avg_days_of_supply: float | None
    stock_health_score: int | None


class InventoryDashboardResponse(BaseModel):
    inventory_kpis: InventoryDashboardKPIs
    inventory_items: list[InventoryDashboardItem]


class ManualStockUpdateRequest(BaseModel):
    menu_item_id: int
    quantity_delta: int | None = None
    set_stock_quantity: int | None = None
    reason: Literal["restock", "correction", "wastage"]
    confirmed: bool


class ManualStockUpdateResponse(BaseModel):
    menu_item_id: int
    item_name: str
    previous_stock: int
    new_stock: int
    quantity_delta: int
    reason: str
    updated_at: str
