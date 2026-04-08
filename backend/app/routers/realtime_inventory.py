"""
Inventory Management API Endpoints

These endpoints provide real-time inventory management capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.core.dependencies import admin_only
from app.services.realtime_inventory_service import RealTimeInventoryService
from app.services.inventory_service import get_inventory_dashboard

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])


@router.post("/sync-completed-orders")
def sync_inventory_with_completed_orders(
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Manually sync inventory with all completed orders.
    Use this if inventory gets out of sync with orders.
    """
    try:
        RealTimeInventoryService.bulk_update_inventory_for_completed_orders(db)
        
        return {
            "success": True,
            "message": "Inventory successfully synced with completed orders",
            "timestamp": "2026-02-06T15:10:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync inventory: {str(e)}")


@router.get("/real-time-status")
def get_real_time_inventory_status(
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Get current real-time inventory status for all menu items.
    This shows the actual present_stocks values from the database.
    """
    try:
        inventory_status = RealTimeInventoryService.get_current_inventory_status(db)
        
        return {
            "success": True,
            "data": inventory_status,
            "total_items": len(inventory_status),
            "timestamp": "2026-02-06T15:10:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inventory status: {str(e)}")


@router.post("/test-order-completion/{order_id}")
def test_order_completion_inventory_update(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Test inventory update for a specific completed order.
    This endpoint is for testing purposes only.
    """
    try:
        RealTimeInventoryService.update_inventory_on_order_completion(db, order_id)
        
        return {
            "success": True,
            "message": f"Inventory updated for order {order_id}",
            "order_id": order_id,
            "timestamp": "2026-02-06T15:10:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update inventory for order {order_id}: {str(e)}")


@router.get("/dashboard-with-real-time")
def get_inventory_dashboard_with_real_time(
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Get inventory dashboard with real-time stock levels.
    This combines the regular dashboard calculation with real-time inventory updates.
    """
    try:
        from datetime import datetime, timedelta
        
        # Get today's date range
        today = datetime.now().date()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        
        # Get regular dashboard data
        kpis, items = get_inventory_dashboard(db, start_dt, end_dt)
        
        # Get real-time inventory status
        real_time_status = RealTimeInventoryService.get_current_inventory_status(db)
        
        # Update items with real-time stock levels
        for item in items:
            if item['item_id'] in real_time_status:
                item['real_time_stock'] = real_time_status[item['item_id']]['present_stock']
                item['stock_difference'] = item['real_time_stock'] - item['remaining_stock']
            else:
                item['real_time_stock'] = item['remaining_stock']
                item['stock_difference'] = 0
        
        return {
            "success": True,
            "inventory_kpis": kpis,
            "inventory_items": items,
            "real_time_status": real_time_status,
            "timestamp": "2026-02-06T15:10:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inventory dashboard: {str(e)}")
