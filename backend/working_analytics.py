"""
Create a new analytics endpoint without caching
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.models.user import User

router = APIRouter()

@router.get("/api/analytics-working")
async def get_analytics_working(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """New analytics endpoint without caching - working version"""
    try:
        # Get today's date range (IST)
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        
        # Calculate IST date boundaries
        ist_today_start = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
        ist_today_end = ist_now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Convert to UTC for database queries
        utc_start = ist_today_start - ist_offset
        utc_end = ist_today_end - ist_offset
        
        print(f"Working analytics: Querying from {utc_start} to {utc_end}")
        
        # Get today's orders
        today_orders = db.query(Order).filter(
            Order.created_at >= utc_start,
            Order.created_at <= utc_end
        ).all()
        
        # Calculate basic metrics
        total_revenue = sum(order.total_amount or 0 for order in today_orders)
        total_orders = len(today_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        unique_customers = len(set(order.user_id for order in today_orders))
        
        # Get yesterday's comparison
        yesterday_start = utc_start - timedelta(days=1)
        yesterday_end = utc_end - timedelta(days=1)
        
        yesterday_orders = db.query(Order).filter(
            Order.created_at >= yesterday_start,
            Order.created_at <= yesterday_end
        ).all()
        
        yesterday_revenue = sum(order.total_amount or 0 for order in yesterday_orders)
        yesterday_orders_count = len(yesterday_orders)
        
        # Calculate growth rates
        revenue_growth = ((total_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 100 if total_revenue > 0 else 0
        orders_growth = ((total_orders - yesterday_orders_count) / yesterday_orders_count * 100) if yesterday_orders_count > 0 else 100 if total_orders > 0 else 0
        
        # Get time slot analysis
        time_slots = {
            "Breakfast": {"revenue": 0, "orders": 0},
            "Lunch": {"revenue": 0, "orders": 0},
            "Snacks": {"revenue": 0, "orders": 0},
            "Dinner": {"revenue": 0, "orders": 0},
            "Late Night": {"revenue": 0, "orders": 0}
        }
        
        for order in today_orders:
            order_time = order.created_at + ist_offset  # Convert to IST
            hour = order_time.hour
            
            if 6 <= hour < 11:
                slot = "Breakfast"
            elif 11 <= hour < 15:
                slot = "Lunch"
            elif 15 <= hour < 18:
                slot = "Snacks"
            elif 18 <= hour < 22:
                slot = "Dinner"
            else:
                slot = "Late Night"
            
            time_slots[slot]["revenue"] += order.total_amount or 0
            time_slots[slot]["orders"] += 1
        
        # Get top selling items
        item_sales = db.query(
            MenuItem.name,
            MenuItem.category,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue'),
            func.count(OrderItem.id).label('order_count')
        ).join(
            OrderItem, MenuItem.id == OrderItem.menu_item_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.created_at >= utc_start,
            Order.created_at <= utc_end
        ).group_by(
            MenuItem.id, MenuItem.name, MenuItem.category
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        # Format item data
        top_items = []
        for item in item_sales:
            top_items.append({
                "name": item.name,
                "category": item.category,
                "orders": item.order_count,
                "quantity": item.total_quantity,
                "revenue": float(item.total_revenue)
            })
        
        return {
            "kpis": {
                "revenue": total_revenue,
                "orders": total_orders,
                "avg_order_value": avg_order_value,
                "customers": unique_customers,
                "revenue_growth": revenue_growth,
                "orders_growth": orders_growth
            },
            "trends": {
                "revenue_growth": revenue_growth,
                "order_growth": orders_growth
            },
            "time_slot_analysis": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "slots": time_slots
            },
            "item_performance": {
                "top_selling": top_items,
                "low_selling": top_items[-5:] if len(top_items) > 5 else []
            },
            "revenue_trends": [
                {
                    "date": ist_now.strftime('%Y-%m-%d'),
                    "revenue": total_revenue,
                    "orders": total_orders
                }
            ],
            "order_trends": [
                {
                    "date": ist_now.strftime('%Y-%m-%d'),
                    "orders": total_orders
                }
            ],
            "customer_trends": [
                {
                    "date": ist_now.strftime('%Y-%m-%d'),
                    "customers": unique_customers
                }
            ],
            "avg_order_value_trends": [
                {
                    "date": ist_now.strftime('%Y-%m-%d'),
                    "avg_order_value": avg_order_value
                }
            ]
        }
        
    except Exception as e:
        print(f"Error in working analytics: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error getting working analytics: {str(e)}")
