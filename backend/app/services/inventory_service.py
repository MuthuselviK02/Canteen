from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.inventory import Inventory, InventoryLog, InventoryStockUpdate
from app.models.menu import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from fastapi import HTTPException
from datetime import datetime


def _normalize_order_status(value: str | None) -> str:
    return (value or "").strip().lower()


def _is_completed_status(value: str | None) -> bool:
    # Inventory consumption MUST only include COMPLETED orders.
    # The codebase uses lowercase statuses in several places.
    return _normalize_order_status(value) == "completed"


def _sum_completed_order_quantity(
    db: Session,
    menu_item_id: int,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    qty = (
        db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            OrderItem.menu_item_id == menu_item_id,
            Order.completed_at.isnot(None),
            Order.completed_at >= start_dt,
            Order.completed_at <= end_dt,
            func.lower(func.trim(Order.status)) == "completed",
        )
        .scalar()
        or 0
    )
    return int(qty)


def _get_inventory_status(remaining_stock: int, projected_stock: int | None) -> str:
    if remaining_stock <= 0:
        return "Out of Stock"
    if remaining_stock < 6:  # Items with less than 6 units need restocking
        return "Needs Restocking"
    if projected_stock is None:
        return "No Forecast"
    if projected_stock <= 0:
        return "Needs Restocking"
    return "Well Stocked"


def _get_risk_level(status: str, projected_stock: int | None) -> str:
    if status == "Out of Stock":
        return "High"
    if status == "No Forecast":
        return "Unknown"
    if status == "Needs Restocking":
        return "High" if projected_stock is not None and projected_stock < -5 else "Medium"
    return "Low"


def _suggest_stock_to_add(projected_stock: int | None) -> int:
    if projected_stock is None or projected_stock >= 0:
        return 0
    return abs(projected_stock)


def check_stock(db: Session, menu_item_id: int, quantity: int):
    inventory = db.query(Inventory).filter(
        Inventory.menu_item_id == menu_item_id
    ).first()

    if not inventory or inventory.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    return inventory


def deduct_stock(db: Session, menu_item_id: int, quantity: int):
    inventory = check_stock(db, menu_item_id, quantity)
    inventory.stock_quantity -= quantity

    log = InventoryLog(
        menu_item_id=menu_item_id,
        quantity_used=quantity
    )

    db.add(log)
    db.commit()

def create_inventory(db: Session, menu_item_id: int, stock_quantity: int):
    existing = db.query(Inventory).filter(
        Inventory.menu_item_id == menu_item_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Inventory already exists for this item"
        )

    inventory = Inventory(
        menu_item_id=menu_item_id,
        stock_quantity=stock_quantity
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


def update_inventory_stock(db: Session, menu_item_id: int, stock_quantity: int):
    inventory = db.query(Inventory).filter(
        Inventory.menu_item_id == menu_item_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found"
        )

    inventory.stock_quantity = stock_quantity
    db.commit()
    db.refresh(inventory)
    return inventory


def get_all_inventory(db: Session):
    return db.query(Inventory).all()


def get_inventory_dashboard(
    db: Session,
    start_dt: datetime,
    end_dt: datetime,
    category: str | None = None,
    predicted_demand_by_item_id: dict[int, int] | None = None,
):
    """
    Database-driven inventory computation.

    - Items: fetched from menu_items (Menu management table)
    - Consumption: reduced ONLY by orders with status == COMPLETED
    - Predictions: automatically fetched from demand forecasts if not provided
    """

    # If no predictions provided, automatically fetch today's demand forecasts
    if predicted_demand_by_item_id is None:
        try:
            from app.models.predictive_analytics import DemandForecast
            from sqlalchemy import func
            today = datetime.now().date()
            
            today_forecasts = db.query(DemandForecast).filter(
                func.date(DemandForecast.forecast_date) == today,
                DemandForecast.forecast_period == 'daily'
            ).all()
            
            predicted_demand_by_item_id = {
                forecast.menu_item_id: forecast.predicted_quantity 
                for forecast in today_forecasts
            }
            
            print(f"[DEBUG] Auto-fetched {len(predicted_demand_by_item_id)} demand forecasts for {today}")
        except Exception as e:
            print(f"[ERROR] Failed to fetch forecasts: {e}")
            predicted_demand_by_item_id = {}

    q = db.query(MenuItem)
    if category and category != "all":
        q = q.filter(MenuItem.category == category)
    menu_items = q.all()

    predicted_demand_by_item_id = predicted_demand_by_item_id or {}

    items = []
    for mi in menu_items:
        opening_stock = int(getattr(mi, "present_stocks", 0) or 0)
        completed_qty = _sum_completed_order_quantity(db, mi.id, start_dt, end_dt)
        
        # Use real-time stock from MenuItem.present_stocks (updated by real-time service)
        # This ensures inventory reflects actual database state including all completed orders
        remaining_stock = int(getattr(mi, "present_stocks", 0) or 0)

        # Handle predictions: null if no prediction data exists
        predicted_future_demand = predicted_demand_by_item_id.get(mi.id)
        if predicted_future_demand is None:
            # No forecast available for this item
            predicted_future_demand = None
            projected_stock = None
        else:
            # Convert to int and calculate projected stock
            predicted_future_demand = int(predicted_future_demand)
            projected_stock = remaining_stock - predicted_future_demand

        status = _get_inventory_status(max(0, remaining_stock), projected_stock)
        risk = _get_risk_level(status, projected_stock)

        # Calculate days of supply only if we have valid predictions
        days_of_supply = None
        if predicted_future_demand is not None and predicted_future_demand > 0:
            days_of_supply = remaining_stock / predicted_future_demand

        items.append(
            {
                "item_id": mi.id,
                "item_name": mi.name,
                "category": mi.category,
                "opening_stock": opening_stock,
                "completed_orders_today": completed_qty,
                "remaining_stock": max(0, remaining_stock),
                "predicted_future_demand": predicted_future_demand,
                "projected_stock": projected_stock,
                "suggested_stock_to_add": _suggest_stock_to_add(projected_stock),
                "days_of_supply": days_of_supply,
                "inventory_status": status,
                "recommended_action": "",
                "risk_level": risk,
            }
        )

    # Sort items by status priority, then by stock level ascending
    status_priority = {"Out of Stock": 0, "Needs Restocking": 1, "Well Stocked": 2, "No Forecast": 3}
    items.sort(key=lambda x: (status_priority.get(x["inventory_status"], 4), x["remaining_stock"]))

    total = len(items)
    well = len([i for i in items if i["inventory_status"] == "Well Stocked"])
    needs = len([i for i in items if i["inventory_status"] == "Needs Restocking"])
    out = len([i for i in items if i["inventory_status"] == "Out of Stock"])
    no_forecast = len([i for i in items if i["inventory_status"] == "No Forecast"])

    # Calculate average days of supply only from items with valid values
    items_with_valid_days = [i for i in items if i["days_of_supply"] is not None]
    avg_days = None
    if items_with_valid_days:
        avg_days = sum(i["days_of_supply"] for i in items_with_valid_days) / len(items_with_valid_days)

    # Calculate stock health score only from items with valid status (exclude No Forecast)
    items_with_valid_status = total - no_forecast
    stock_health_score = None
    if items_with_valid_status > 0:
        well_percentage = (well / items_with_valid_status) * 100
        days_score = avg_days * 10 if avg_days is not None else 0
        health_score_float = (well_percentage * 0.7) + (days_score * 0.3)
        stock_health_score = int(round(health_score_float))  # Convert to integer

    kpis = {
        "total_items": total,
        "well_stocked": well,
        "needs_restocking": needs,
        "out_of_stock": out,
        "no_forecast": no_forecast,
        "avg_days_of_supply": avg_days,
        "stock_health_score": stock_health_score,
    }

    return kpis, items


def manual_stock_update_with_confirmation(
    db: Session,
    menu_item_id: int,
    quantity_delta: int | None,
    set_stock_quantity: int | None,
    reason: str,
    confirmed: bool,
):
    """
    Manual stock update. MUST be confirmed by the user.

    This updates the MenuItem.present_stocks as the latest snapshot and
    writes an audit row to inventory_logs.
    """

    if not confirmed:
        raise HTTPException(status_code=400, detail="Confirmation required")
    if set_stock_quantity is None and (quantity_delta is None or quantity_delta == 0):
        raise HTTPException(status_code=400, detail="Update value is required")
    if reason not in ["restock", "correction", "wastage"]:
        raise HTTPException(status_code=400, detail="Invalid reason")

    mi = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not mi:
        raise HTTPException(status_code=404, detail="Menu item not found")

    previous = int(getattr(mi, "present_stocks", 0) or 0)

    if set_stock_quantity is not None:
        new_value = int(set_stock_quantity)
        computed_delta = new_value - previous
    else:
        new_value = previous + int(quantity_delta or 0)
        computed_delta = int(quantity_delta or 0)

    if new_value < 0:
        raise HTTPException(status_code=400, detail="Resulting stock cannot be negative")

    # Update snapshot
    mi.present_stocks = new_value

    # Audit logs
    # InventoryLog is a legacy table; keep it as best-effort.
    db.add(InventoryLog(menu_item_id=menu_item_id, quantity_used=abs(int(computed_delta))))

    # New snapshot/audit table to preserve historical data.
    db.add(
        InventoryStockUpdate(
            menu_item_id=menu_item_id,
            previous_stock=previous,
            quantity_delta=int(computed_delta),
            new_stock=new_value,
            reason=reason,
        )
    )

    db.commit()
    db.refresh(mi)

    return {
        "menu_item_id": mi.id,
        "item_name": mi.name,
        "previous_stock": previous,
        "new_stock": new_value,
        "quantity_delta": int(computed_delta),
        "reason": reason,
        "updated_at": datetime.utcnow().isoformat(),
    }
