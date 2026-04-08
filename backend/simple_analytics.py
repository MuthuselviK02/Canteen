"""
Create a simple analytics endpoint that returns basic metrics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.order import Order
from app.models.user import User

router = APIRouter(prefix="/api/simple-analytics", tags=["Simple Analytics"])

@router.get("/dashboard-summary")
async def get_simple_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get simple dashboard summary without complex analytics"""
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
        
        print(f"Querying orders from {utc_start} to {utc_end}")
        
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
        revenue_growth = ((total_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
        orders_growth = ((total_orders - yesterday_orders_count) / yesterday_orders_count * 100) if yesterday_orders_count > 0 else 0
        
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
            "period": {
                "start_date": utc_start.isoformat(),
                "end_date": utc_end.isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error in simple analytics: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error getting simple dashboard summary: {str(e)}")
