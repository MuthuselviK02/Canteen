from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database.session import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.core.dependencies import admin_only

router = APIRouter(prefix="/api/admin", tags=["Admin KPI"])


@router.get("/kpi/daily")
def get_daily_kpi(
    db: Session = Depends(get_db),
    current_user = Depends(admin_only)
):
    """
    Get daily KPI metrics for admin dashboard
    Returns today's metrics and yesterday's comparison
    All timestamps are calculated in UTC and converted to IST for display
    """
    try:
        now = datetime.utcnow()
        
        # Calculate IST time by adding 5.5 hours
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        
        # Calculate today's date range in IST
        today_start = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) - ist_offset
        today_end = ist_now.replace(hour=23, minute=59, second=59, microsecond=999999) - ist_offset
        
        # Calculate yesterday's date range in IST
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start - timedelta(microseconds=1)
        
        def calculate_kpi(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
            """Calculate KPI metrics for a given date range"""
            
            # Get orders in the date range (same as kitchen orders)
            orders = db.query(Order).filter(
                and_(Order.created_at >= start_date, Order.created_at < end_date)
            ).all()

            if orders:
                order_ids = [order.id for order in orders]
                valid_order_ids = {
                    row[0]
                    for row in db.query(OrderItem.order_id)
                    .filter(OrderItem.order_id.in_(order_ids))
                    .distinct()
                    .all()
                }
                orders = [order for order in orders if order.id in valid_order_ids]
            
            # Total Orders
            total_orders = len(orders)
            
            # Active Orders (pending + preparing)
            active_orders = len([o for o in orders if o.status in ['pending', 'preparing']])
            
            # Completed orders for revenue calculation
            completed_orders = [o for o in orders if o.status == 'completed']
            
            # Calculate Revenue from completed orders
            total_revenue = 0
            if completed_orders:
                order_ids = [o.id for o in completed_orders]
                order_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all()
                
                for item in order_items:
                    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                    if menu_item:
                        total_revenue += item.quantity * menu_item.price
            
            # Calculate Average Wait Time (in minutes)
            # Wait time = time from order creation to completion
            wait_times = []
            for order in completed_orders:
                if order.completed_at:
                    wait_time = (order.completed_at - order.created_at).total_seconds() / 60
                    wait_times.append(wait_time)
            
            avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
            
            return {
                'total_orders': total_orders,
                'revenue': total_revenue,
                'avg_wait_time': round(avg_wait_time, 2),
                'active_orders': active_orders
            }
        
        # Calculate today's KPIs
        today_kpi = calculate_kpi(today_start, today_end)
        
        # Calculate yesterday's KPIs
        yesterday_kpi = calculate_kpi(yesterday_start, yesterday_end)
        
        # Calculate percentage changes
        def calculate_change(today_val: float, yesterday_val: float) -> Dict[str, Any]:
            if yesterday_val == 0:
                return {
                    'value': today_val - yesterday_val,
                    'percentage': 100.0 if today_val > 0 else 0.0,
                    'trend': 'up' if today_val > 0 else 'neutral'
                }
            
            change = today_val - yesterday_val
            percentage = (change / yesterday_val) * 100
            
            return {
                'value': change,
                'percentage': round(percentage, 2),
                'trend': 'up' if percentage > 0 else 'down' if percentage < 0 else 'neutral'
            }
        
        # Calculate changes for each metric
        kpi_data = {
            'today': today_kpi,
            'yesterday': yesterday_kpi,
            'changes': {
                'total_orders': calculate_change(today_kpi['total_orders'], yesterday_kpi['total_orders']),
                'revenue': calculate_change(today_kpi['revenue'], yesterday_kpi['revenue']),
                'avg_wait_time': calculate_change(today_kpi['avg_wait_time'], yesterday_kpi['avg_wait_time']),
                'active_orders': calculate_change(today_kpi['active_orders'], yesterday_kpi['active_orders'])
            },
            'generated_at': now.isoformat(),
            'timezone': 'UTC (calculated), IST (for display)'
        }
        
        return kpi_data
        
    except Exception as e:
        print(f"Error calculating daily KPI: {e}")
        # Return fallback data
        return {
            'today': {
                'total_orders': 0,
                'revenue': 0,
                'avg_wait_time': 0,
                'active_orders': 0
            },
            'yesterday': {
                'total_orders': 0,
                'revenue': 0,
                'avg_wait_time': 0,
                'active_orders': 0
            },
            'changes': {
                'total_orders': {'value': 0, 'percentage': 0, 'trend': 'neutral'},
                'revenue': {'value': 0, 'percentage': 0, 'trend': 'neutral'},
                'avg_wait_time': {'value': 0, 'percentage': 0, 'trend': 'neutral'},
                'active_orders': {'value': 0, 'percentage': 0, 'trend': 'neutral'}
            },
            'generated_at': datetime.utcnow().isoformat(),
            'timezone': 'UTC (calculated), IST (for display)',
            'error': str(e)
        }
