from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
import time
from datetime import datetime, timedelta

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.services.historical_analytics_service import HistoricalAnalyticsService
from app.models.order import Order

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Test endpoint
@router.get("/test")
async def test_analytics_endpoint():
    """
    Test endpoint to verify analytics router is working
    """
    return {"message": "Analytics router is working!", "status": "success"}

# Cache for analytics data (simple in-memory cache)
analytics_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cache_key(endpoint: str, params: dict = None) -> str:
    """Generate cache key for analytics endpoints"""
    param_str = str(sorted(params.items())) if params else ""
    return f"{endpoint}_{param_str}"

def get_cached_data(cache_key: str) -> Optional[dict]:
    """Get cached analytics data if available and not expired"""
    if cache_key in analytics_cache:
        data, timestamp = analytics_cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    return None

def set_cached_data(cache_key: str, data: dict, expire_seconds: int = None):
    """Cache analytics data with timestamp"""
    analytics_cache[cache_key] = (data, time.time())
    # expire_seconds parameter is accepted but not used in this simple cache implementation

@router.get("/clear-all-cache")
async def clear_all_analytics_cache(
    user=Depends(get_current_user)
):
    """
    Clear all analytics cache (for testing/debugging)
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    global analytics_cache
    analytics_cache.clear()
    return {"message": "All analytics cache cleared successfully"}

@router.get("/clear-cache")
async def clear_analytics_cache(
    user=Depends(get_current_user)
):
    """
    Clear analytics cache (for testing/debugging)
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    global analytics_cache
    analytics_cache.clear()
    return {"message": "Analytics cache cleared successfully"}

@router.get("/overview")
def get_overview_analytics(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get comprehensive overview analytics for SuperAdmin dashboard
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    cache_key = get_cache_key("overview")
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        analytics_data = AnalyticsService.get_overview_metrics(db)
        set_cached_data(cache_key, analytics_data)
        return analytics_data
    except Exception as e:
        print(f"Error in overview analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate overview analytics")

@router.get("/revenue")
def get_revenue_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days for analytics"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get detailed revenue analytics
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    cache_key = get_cache_key("revenue", {"days": days})
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        analytics_data = AnalyticsService.get_revenue_analytics(db, days)
        set_cached_data(cache_key, analytics_data)
        return analytics_data
    except Exception as e:
        print(f"Error in revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate revenue analytics")

@router.get("/menu")
def get_menu_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days for analytics"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get menu performance analytics
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    cache_key = get_cache_key("menu", {"days": days})
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        analytics_data = AnalyticsService.get_menu_analytics(db, days)
        set_cached_data(cache_key, analytics_data)
        return analytics_data
    except Exception as e:
        print(f"Error in menu analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate menu analytics")

@router.get("/users")
def get_user_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days for analytics"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get user behavior analytics
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    cache_key = get_cache_key("users", {"days": days})
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        analytics_data = AnalyticsService.get_user_analytics(db, days)
        set_cached_data(cache_key, analytics_data)
        return analytics_data
    except Exception as e:
        print(f"Error in user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate user analytics")

@router.get("/orders-by-date")
async def get_orders_by_date(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    status: Optional[str] = Query(None, description="Order status filter"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders for a specific date (for analytics dashboard)
    Only accessible by ADMIN and SUPER_ADMIN roles
    """
    try:
        # Check if user has admin privileges
        if current_user.role not in ['ADMIN', 'SUPER_ADMIN']:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Parse date and set time boundaries in IST
        target_dt = datetime.strptime(date, "%Y-%m-%d")
        
        # Set day boundaries in IST
        day_start = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Convert IST boundaries back to UTC for database query
        day_start_utc = day_start - timedelta(hours=5, minutes=30)
        day_end_utc = day_end - timedelta(hours=5, minutes=30)
        
        print(f"🕐 Analytics Orders Query - Date: {date}, IST Start: {day_start}, IST End: {day_end}")
        print(f"🕐 Analytics Orders Query - UTC Start: {day_start_utc}, UTC End: {day_end_utc}")
        
        # Get all orders for the date range
        orders_query = db.query(Order).filter(
            and_(
                Order.created_at >= day_start_utc,
                Order.created_at < day_end_utc
            )
        )
        
        # Filter by status if provided
        if status:
            orders_query = orders_query.filter(Order.status == status.lower())
        
        orders = orders_query.all()
        
        print(f"📊 Analytics Orders Query - Found {len(orders)} orders")
        
        # Convert to response format
        orders_response = []
        for order in orders:
            # Convert UTC time to IST for display
            ist_time = order.created_at + timedelta(hours=5, minutes=30)
            
            orders_response.append({
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "created_at": order.created_at.isoformat(),
                "created_at_ist": f"{ist_time.isoformat()}+05:30",
                "queue_position": order.queue_position,
                "predicted_wait_time": order.predicted_wait_time
            })
        
        return {
            "date": date,
            "total_orders": len(orders_response),
            "orders": orders_response
        }
        
    except Exception as e:
        print(f"Error in orders by date: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")


@router.get("/orders")
def get_order_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days for analytics"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get detailed order analytics
    Only accessible by SUPER_ADMIN and ADMIN roles
    """
    if user.role not in ['SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
    
    cache_key = get_cache_key("orders", {"days": days})
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        analytics_data = AnalyticsService.get_order_analytics(db, days)
        set_cached_data(cache_key, analytics_data)
        return analytics_data
    except Exception as e:
        print(f"Error in order analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate order analytics")

@router.get("/dashboard")
async def get_analytics_dashboard(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical and real-time business analytics dashboard
    Only uses completed/paid orders data
    """
    try:
        # Parse date parameters (handle IST timezone)
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                # Parse date in IST and convert to UTC for database query
                ist_start_date = datetime.strptime(start_date, "%Y-%m-%d")
                ist_offset = timedelta(hours=5, minutes=30)
                parsed_start_date = ist_start_date - ist_offset
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}. Use YYYY-MM-DD format")
        
        if end_date:
            try:
                # Parse date in IST and convert to UTC for database query
                ist_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                ist_offset = timedelta(hours=5, minutes=30)
                parsed_end_date = ist_end_date.replace(hour=23, minute=59, second=59, microsecond=999999) - ist_offset
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format")
        
        # Validate date range
        if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        # Check cache first
        cache_key = get_cache_key("dashboard_v2", {"start_date": start_date, "end_date": end_date})
        cached_data = get_cached_data(cache_key)
        if cached_data:
            try:
                daily = (cached_data.get("revenue_trends") or {}).get("daily")
                if isinstance(daily, dict) and isinstance(daily.get("data"), list):
                    return cached_data
            except Exception:
                pass
            
        analytics_data = HistoricalAnalyticsService.get_comprehensive_historical_analytics(
            db, parsed_start_date, parsed_end_date
        )

        try:
            daily = (analytics_data.get("revenue_trends") or {}).get("daily")
            if isinstance(daily, dict) and isinstance(daily.get("data"), list):
                set_cached_data(cache_key, analytics_data)
        except Exception:
            pass
        return analytics_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@router.get("/kpi-metrics")
async def get_kpi_metrics(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get KPI metrics with time scope comparisons
    """
    try:
        # Parse date parameters
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}. Use YYYY-MM-DD format")
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Set end date to end of day
                parsed_end_date = parsed_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format")
        
        # Validate date range
        if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        
        cache_key = get_cache_key("kpi_metrics", {"start_date": start_date, "end_date": end_date})
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
            
        data = HistoricalAnalyticsService.get_kpi_metrics(db, parsed_start_date, parsed_end_date)
        set_cached_data(cache_key, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching KPI metrics: {str(e)}")

@router.get("/revenue-by-time-slot")
async def get_revenue_by_time_slot(
    target_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue analysis by time slots for a specific date
    """
    try:
        cache_key = get_cache_key("revenue_time_slot", {"date": target_date})
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
            
        data = HistoricalAnalyticsService.get_revenue_by_time_slot(db, target_date)
        set_cached_data(cache_key, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching revenue by time slot: {str(e)}")

@router.get("/item-performance")
async def get_item_performance(
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get top-selling and low-selling items analysis
    """
    try:
        cache_key = get_cache_key("item_performance", {"days": days})
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
            
        data = HistoricalAnalyticsService.get_item_performance_analysis(db, days)
        set_cached_data(cache_key, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item performance: {str(e)}")

@router.get("/revenue-trends")
async def get_revenue_trends(
    view_type: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue trends with different view types
    """
    try:
        cache_key = get_cache_key("revenue_trends", {"view_type": view_type, "days": days})
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
            
        data = HistoricalAnalyticsService.get_revenue_trends(db, view_type, days)
        set_cached_data(cache_key, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching revenue trends: {str(e)}")

@router.get("/kitchen")
async def get_kitchen_analytics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get kitchen-specific analytics for operational efficiency
    Accessible by KITCHEN, STAFF, SUPER_ADMIN, and ADMIN roles
    """
    # DEBUG: Log user info
    print(f"DEBUG: User {current_user.email} with role '{current_user.role}' accessing kitchen analytics")
    
    if current_user.role not in ['KITCHEN', 'STAFF', 'SUPER_ADMIN', 'ADMIN']:
        raise HTTPException(status_code=403, detail="Access denied. Kitchen privileges required.")
    
    try:
        # Check cache first
        cache_key = get_cache_key("kitchen")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data

        # Get kitchen analytics
        analytics_data = AnalyticsService.get_kitchen_analytics(db)
        
        # Cache the result (shorter cache for real-time operations)
        set_cached_data(cache_key, analytics_data)
        
        return analytics_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching kitchen analytics: {str(e)}")

@router.get("/debug/user")
async def debug_user_info(
    current_user = Depends(get_current_user)
):
    """
    Debug endpoint to check current user info
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "fullname": current_user.fullname,
        "is_active": current_user.is_active
    }

@router.delete("/cache")
def clear_analytics_cache(
    user=Depends(get_current_user)
):
    """
    Clear analytics cache (useful for debugging or force refresh)
    Only accessible by SUPER_ADMIN role
    """
    if user.role != 'SUPER_ADMIN':
        raise HTTPException(status_code=403, detail="Access denied. Super Admin privileges required.")
    
    global analytics_cache
    analytics_cache.clear()
    
    return {
        "message": "Analytics cache cleared successfully",
        "cleared_at": datetime.utcnow().isoformat()
    }

@router.get("/health")
def analytics_health_check():
    """
    Health check endpoint for analytics service
    """
    return {
        "status": "healthy",
        "cache_size": len(analytics_cache),
        "cache_duration": CACHE_DURATION,
        "timestamp": datetime.utcnow().isoformat()
    }
