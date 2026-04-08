from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, extract, case

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.models.user import User


class HistoricalAnalyticsService:
    """Service for generating historical and real-time business analytics from completed/paid orders"""

    ANALYTICS_ORDER_STATUSES = ["preparing", "ready", "completed", "paid"]
    
    @staticmethod
    def get_time_slot(hour: int) -> str:
        """Categorize hour into time slots"""
        if 6 <= hour < 11:
            return "Breakfast"
        elif 11 <= hour < 15:
            return "Lunch"
        elif 15 <= hour < 18:
            return "Snacks"
        elif 18 <= hour < 23:
            return "Dinner"
        else:
            return "LateNight"
    
    @staticmethod
    def get_kpi_metrics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get KPI metrics with time scope comparisons
        Only uses completed/paid orders
        """
        try:
            # Get current IST time by adding 5.5 hours to UTC
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            ist_today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            ist_yesterday = ist_today - timedelta(days=1)
            
            # Use provided date range or default to today (IST)
            if start_date and end_date:
                current_start = start_date
                current_end = end_date
                # Calculate previous period of same duration
                duration = current_end - current_start
                prev_start = current_start - duration
                prev_end = current_start
            else:
                # Use IST time for default date range
                current_start = ist_today - ist_offset  # Today start in UTC
                current_end = ist_now - ist_offset      # Current time in UTC
                prev_start = ist_yesterday - ist_offset # Yesterday start in UTC
                prev_end = ist_today - ist_offset      # Yesterday end in UTC
            
            def get_period_metrics(start: datetime, end: datetime) -> Dict[str, float]:
                """Get metrics for a specific period"""
                # Get order items with menu prices in a single query for completed/paid orders
                order_items_query = db.query(OrderItem, MenuItem, Order).join(
                    MenuItem, OrderItem.menu_item_id == MenuItem.id
                ).join(
                    Order, OrderItem.order_id == Order.id
                ).filter(
                    and_(
                        Order.created_at >= start,
                        Order.created_at < end,
                        func.lower(Order.status).in_(HistoricalAnalyticsService.ANALYTICS_ORDER_STATUSES)
                    )
                ).all()
                
                # Calculate metrics from the joined data
                total_revenue = 0
                total_orders_set = set()
                unique_customers_set = set()
                
                for order_item, menu_item, order in order_items_query:
                    item_price = menu_item.price or 0
                    total_revenue += item_price * order_item.quantity
                    total_orders_set.add(order.id)
                    unique_customers_set.add(order.user_id)
                
                total_orders = len(total_orders_set)
                avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
                unique_customers = len(unique_customers_set)
                
                return {
                    "revenue": total_revenue,
                    "orders": total_orders,
                    "avg_order_value": avg_order_value,
                    "unique_customers": unique_customers
                }
            
            # Get metrics for current and previous periods
            current_metrics = get_period_metrics(current_start, current_end)
            previous_metrics = get_period_metrics(prev_start, prev_end)
            
            def calculate_growth(current: float, previous: float) -> float:
                """Calculate percentage growth with 0-safe logic"""
                if previous == 0:
                    return 100.0 if current > 0 else 0.0
                return round(((current - previous) / previous) * 100, 1)
            
            return {
                "current_period": {
                    **current_metrics,
                    "revenue_growth": calculate_growth(current_metrics["revenue"], previous_metrics["revenue"]),
                    "orders_growth": calculate_growth(current_metrics["orders"], previous_metrics["orders"]),
                    "avg_order_growth": calculate_growth(current_metrics["avg_order_value"], previous_metrics["avg_order_value"]),
                    "customers_growth": calculate_growth(current_metrics["unique_customers"], previous_metrics["unique_customers"]),
                    "period_start": current_start.isoformat(),
                    "period_end": current_end.isoformat()
                },
                "previous_period": {
                    **previous_metrics,
                    "period_start": prev_start.isoformat(),
                    "period_end": prev_end.isoformat()
                }
            }
            
        except Exception as e:
            print(f"Error in get_kpi_metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_revenue_by_time_slot(db: Session, target_date: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get revenue analysis by time slots for a specific date or date range
        """
        try:
            # If date range is provided, use it; otherwise use target date
            if start_date and end_date:
                # Use the provided date range
                day_start_utc = start_date
                day_end_utc = end_date
                display_date = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            else:
                # Parse target date or use today (in IST)
                if target_date:
                    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
                else:
                    # Convert current UTC time to IST for date calculation
                    ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
                    target_dt = ist_now
                
                # Set day boundaries in IST
                day_start = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                # Convert IST boundaries back to UTC for database query
                day_start_utc = day_start - timedelta(hours=5, minutes=30)
                day_end_utc = day_end - timedelta(hours=5, minutes=30)
                display_date = target_date or target_dt.strftime("%Y-%m-%d")
            
            # Get order items with menu and order details in a single query for completed/paid orders
            order_items_query = db.query(OrderItem, MenuItem, Order).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    Order.created_at >= day_start_utc,
                    Order.created_at < day_end_utc,
                    func.lower(Order.status).in_(HistoricalAnalyticsService.ANALYTICS_ORDER_STATUSES)
                )
            ).all()
            
            # Group by time slots
            time_slots = {
                "Breakfast": {"revenue": 0, "orders": 0, "items": []},
                "Lunch": {"revenue": 0, "orders": 0, "items": []},
                "Snacks": {"revenue": 0, "orders": 0, "items": []},
                "Dinner": {"revenue": 0, "orders": 0, "items": []},
                "LateNight": {"revenue": 0, "orders": 0, "items": []}
            }
            
            total_revenue = 0
            processed_orders = set()  # Track unique orders
            
            for order_item, menu_item, order in order_items_query:
                # Convert UTC time to IST (UTC+5:30) before categorizing
                ist_time = order.created_at + timedelta(hours=5, minutes=30)
                hour = ist_time.hour
                time_slot = HistoricalAnalyticsService.get_time_slot(hour)
                
                item_revenue = (menu_item.price or 0) * order_item.quantity
                time_slots[time_slot]["revenue"] += item_revenue
                time_slots[time_slot]["items"].append({
                    "name": menu_item.name,
                    "quantity": order_item.quantity,
                    "revenue": item_revenue
                })
                total_revenue += item_revenue
                
                # Count unique orders per time slot
                if order.id not in processed_orders:
                    time_slots[time_slot]["orders"] += 1
                    processed_orders.add(order.id)
            
            # Calculate percentages and sort items within each slot
            for slot_name, slot_data in time_slots.items():
                slot_data["percentage"] = (slot_data["revenue"] / total_revenue * 100) if total_revenue > 0 else 0
                slot_data["items"] = sorted(slot_data["items"], key=lambda x: x["revenue"], reverse=True)[:5]  # Top 5 items
            
            return {
                "date": display_date,
                "total_revenue": total_revenue,
                "total_orders": len(processed_orders),
                "time_slots": time_slots
            }
            
        except Exception as e:
            print(f"Error in get_revenue_by_time_slot: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_item_performance_analysis(db: Session, days: int = 30, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get top-selling and low-selling items analysis
        """
        try:
            # Use provided date range or default to last N days
            if start_date and end_date:
                query_start_date = start_date
                query_end_date = end_date
                period_description = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            else:
                query_end_date = datetime.utcnow()
                query_start_date = query_end_date - timedelta(days=days)
                period_description = f"Last {days} days"
            
            # Get order items with menu and order details in a single query for completed/paid orders
            order_items_query = db.query(OrderItem, MenuItem, Order).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    Order.created_at >= query_start_date,
                    Order.created_at < query_end_date,
                    func.lower(Order.status).in_(HistoricalAnalyticsService.ANALYTICS_ORDER_STATUSES)
                )
            ).all()
            
            # Aggregate item performance
            item_stats = {}
            for order_item, menu_item, order in order_items_query:
                item_id = menu_item.id
                if item_id not in item_stats:
                    item_stats[item_id] = {
                        "name": menu_item.name,
                        "category": menu_item.category,
                        "price": menu_item.price or 0,
                        "total_quantity": 0,
                        "total_orders": set(),
                        "total_revenue": 0
                    }
                
                item_stats[item_id]["total_quantity"] += order_item.quantity
                item_stats[item_id]["total_orders"].add(order_item.order_id)
                item_stats[item_id]["total_revenue"] += (menu_item.price or 0) * order_item.quantity
            
            # Convert sets to counts and calculate additional metrics
            for item_id, stats in item_stats.items():
                stats["total_orders"] = len(stats["total_orders"])
                stats["avg_quantity_per_order"] = stats["total_quantity"] / stats["total_orders"] if stats["total_orders"] > 0 else 0
            
            # Sort by revenue for top-selling
            top_selling = sorted(item_stats.values(), key=lambda x: x["total_revenue"], reverse=True)[:10]
            
            # Sort by revenue for low-selling (minimum 1 order to be considered)
            low_selling_candidates = [stats for stats in item_stats.values() if stats["total_orders"] >= 1]
            low_selling = sorted(low_selling_candidates, key=lambda x: x["total_revenue"])[:10]
            
            # Add actionable suggestions
            for item in top_selling:
                if item["total_revenue"] > 1000:  # High revenue threshold
                    item["suggestion"] = "promote"
                    item["action"] = "Feature prominently, consider combo offers"
                elif item["avg_quantity_per_order"] > 2:
                    item["suggestion"] = "maintain"
                    item["action"] = "Keep current positioning, monitor demand"
                else:
                    item["suggestion"] = "optimize"
                    item["action"] = "Consider upselling strategies"
            
            for item in low_selling:
                if item["total_revenue"] < 50:  # Very low revenue threshold
                    item["suggestion"] = "remove"
                    item["action"] = "Consider removing from menu or revamping"
                elif item["total_revenue"] < 100:  # Low revenue threshold
                    item["suggestion"] = "improve"
                    item["action"] = "Review recipe, pricing, or presentation"
                else:
                    item["suggestion"] = "promote"
                    item["action"] = "Increase visibility, offer promotions"
            
            return {
                "period": period_description,
                "total_items": len(item_stats),
                "top_selling": top_selling,
                "low_selling": low_selling
            }
            
        except Exception as e:
            print(f"Error in get_item_performance_analysis: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_revenue_trends(
        db: Session, 
        view_type: str = "daily", 
        days: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get revenue trends with different view types (daily/weekly/monthly)
        """
        try:
            # Use provided date range or default to last N days (in IST)
            if start_date and end_date:
                # Use the provided date range but ensure full day coverage
                # start_date and end_date are already converted to UTC by the router
                query_start_date = start_date
                query_end_date = end_date
                print(f"DEBUG Revenue Trends: Using provided date range {query_start_date} to {query_end_date}")
                print(f"DEBUG Revenue Trends: Start date IST: {query_start_date + timedelta(hours=5, minutes=30)}")
                print(f"DEBUG Revenue Trends: End date IST: {query_end_date + timedelta(hours=5, minutes=30)}")
                # Determine grouping strategy based on date range
                # ≤ 2 days → Hourly, > 2 days → Daily
                date_range_days = (query_end_date - query_start_date).days + 1
                if date_range_days <= 2:
                    effective_view_type = "hourly"
                    print(f"DEBUG Revenue Trends: Using HOURLY grouping for {date_range_days} day(s) range")
                else:
                    effective_view_type = "daily"
                    print(f"DEBUG Revenue Trends: Using DAILY grouping for {date_range_days} day(s) range")
            else:
                # Default to last N days in IST
                now = datetime.utcnow()
                ist_offset = timedelta(hours=5, minutes=30)
                ist_now = now + ist_offset
                query_end_date = ist_now - ist_offset  # Current time in UTC
                query_start_date = query_end_date - timedelta(days=days)  # N days ago in UTC
                effective_view_type = view_type  # Use provided view_type for default ranges
                print(f"DEBUG Revenue Trends: Using default range {query_start_date} to {query_end_date}")
                print(f"DEBUG Revenue Trends: Start date IST: {query_start_date + timedelta(hours=5, minutes=30)}")
                print(f"DEBUG Revenue Trends: End date IST: {query_end_date + timedelta(hours=5, minutes=30)}")
                print(f"DEBUG Revenue Trends: View type: {effective_view_type}")
            
            print(f"DEBUG Revenue Trends: Querying orders between {query_start_date} and {query_end_date}")
            
            # Get order items with menu and order details in a single query for completed/paid orders
            order_items_query = db.query(OrderItem, MenuItem, Order).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    Order.created_at >= query_start_date,
                    Order.created_at <= query_end_date,  # Changed from < to <= for inclusive end date
                    func.lower(Order.status).in_(HistoricalAnalyticsService.ANALYTICS_ORDER_STATUSES)
                )
            ).all()
            
            # Group by time period
            trends = {}
            debug_count = 0
            
            for order_item, menu_item, order in order_items_query:
                revenue = (menu_item.price or 0) * order_item.quantity
                
                # Convert order time to IST for consistent grouping
                ist_offset = timedelta(hours=5, minutes=30)
                order_time_ist = order.created_at + ist_offset
                
                if effective_view_type == "hourly":
                    # Group by hour - format: "YYYY-MM-DD HH:00"
                    period_key = order_time_ist.strftime("%Y-%m-%d %H:00")
                elif effective_view_type == "daily":
                    period_key = order_time_ist.strftime("%Y-%m-%d")
                elif effective_view_type == "weekly":
                    # Get week start date in IST
                    week_start = order_time_ist - timedelta(days=order_time_ist.weekday())
                    period_key = week_start.strftime("%Y-%m-%d")
                elif effective_view_type == "monthly":
                    period_key = order_time_ist.strftime("%Y-%m")
                else:
                    period_key = order_time_ist.strftime("%Y-%m-%d")
                
                # Debug first few orders to see grouping
                if debug_count < 5:
                    print(f"DEBUG Grouping: Order UTC time: {order.created_at}, IST time: {order_time_ist}, Period key: {period_key}")
                    debug_count += 1
                
                if period_key not in trends:
                    trends[period_key] = {
                        "revenue": 0,
                        "orders": set(),
                        "customers": set(),
                        "revenue_growth": 0,
                        "orders_growth": 0,
                        "customers_growth": 0
                    }
                
                trends[period_key]["revenue"] += revenue
                trends[period_key]["orders"].add(order.id)
                trends[period_key]["customers"].add(order.user_id)
            
            # Convert sets to counts and calculate additional metrics
            trend_data = []
            for period_key, data in sorted(trends.items()):
                order_count = len(data["orders"])
                customer_count = len(data["customers"])
                avg_order_value = data["revenue"] / order_count if order_count > 0 else 0
                
                trend_data.append({
                    "period": period_key,
                    "date": period_key,
                    "revenue": data["revenue"],
                    "orders": order_count,
                    "customers": customer_count,
                    "avg_order_value": avg_order_value
                })
            
            # ZERO-FILL: Generate complete date series for the selected range
            if start_date and end_date:
                # Build expected bucket list based on view type
                expected_buckets = []
                if effective_view_type == "hourly":
                    # Generate hourly buckets for each day in range
                    current_date = query_start_date
                    while current_date <= query_end_date:
                        # Convert to IST for bucket key
                        current_ist = current_date + timedelta(hours=5, minutes=30)
                        # Generate 24 hourly buckets for this day
                        for hour in range(24):
                            bucket_key = current_ist.strftime("%Y-%m-%d") + f" {hour:02d}:00"
                            expected_buckets.append(bucket_key)
                        current_date += timedelta(days=1)
                else:
                    # Generate daily buckets
                    current_date = query_start_date
                    while current_date <= query_end_date:
                        # Convert to IST for bucket key
                        current_ist = current_date + timedelta(hours=5, minutes=30)
                        bucket_key = current_ist.strftime("%Y-%m-%d")
                        expected_buckets.append(bucket_key)
                        current_date += timedelta(days=1)
                
                # Create lookup from existing data
                data_lookup = {item["date"]: item for item in trend_data}
                
                # Build complete series with zero-fill
                complete_trend_data = []
                for bucket in expected_buckets:
                    if bucket in data_lookup:
                        complete_trend_data.append(data_lookup[bucket])
                    else:
                        # Zero-fill missing bucket
                        complete_trend_data.append({
                            "period": bucket,
                            "date": bucket,
                            "revenue": 0,
                            "orders": 0,
                            "customers": 0,
                            "avg_order_value": 0
                        })
                
                trend_data = complete_trend_data
                print(f"DEBUG Zero-fill: Generated {len(trend_data)} buckets (expected {len(expected_buckets)})")
            
            # Calculate growth percentages using robust logic
            for i in range(1, len(trend_data)):
                prev = trend_data[i-1]
                curr = trend_data[i]
                
                # Use standard growth formula with 0-handling
                if prev["revenue"] == 0:
                    curr["revenue_growth"] = 100.0 if curr["revenue"] > 0 else 0.0
                else:
                    curr["revenue_growth"] = ((curr["revenue"] - prev["revenue"]) / prev["revenue"] * 100)
                
                if prev["orders"] == 0:
                    curr["orders_growth"] = 100.0 if curr["orders"] > 0 else 0.0
                else:
                    curr["orders_growth"] = ((curr["orders"] - prev["orders"]) / prev["orders"] * 100)
                
                if prev["customers"] == 0:
                    curr["customers_growth"] = 100.0 if curr["customers"] > 0 else 0.0
                else:
                    curr["customers_growth"] = ((curr["customers"] - prev["customers"]) / prev["customers"] * 100)
                
                if prev["avg_order_value"] == 0:
                    curr["avg_order_growth"] = 100.0 if curr["avg_order_value"] > 0 else 0.0
                else:
                    curr["avg_order_growth"] = ((curr["avg_order_value"] - prev["avg_order_value"]) / prev["avg_order_value"] * 100)
            else:
                if trend_data:
                    trend_data[0]["revenue_growth"] = 0
                    trend_data[0]["orders_growth"] = 0
                    trend_data[0]["customers_growth"] = 0
                    trend_data[0]["avg_order_growth"] = 0
            
            # Calculate targets (simple growth target of 10% over previous period average)
            if len(trend_data) > 1:
                avg_revenue = sum(t["revenue"] for t in trend_data[:-1]) / (len(trend_data) - 1)
                target_growth = 1.1  # 10% growth target
                
                for t in trend_data:
                    t["target_revenue"] = avg_revenue * target_growth
                    t["target_achieved"] = (t["revenue"] / t["target_revenue"] * 100) if t["target_revenue"] > 0 else 0
            else:
                for t in trend_data:
                    t["target_revenue"] = t["revenue"]
                    t["target_achieved"] = 100
            
            # Build period description
            if start_date and end_date:
                date_range_days = (end_date - start_date).days + 1
                if effective_view_type == "hourly":
                    period_desc = f"Hourly view for {date_range_days} day(s)"
                else:
                    period_desc = f"Daily view for {date_range_days} day(s)"
            else:
                period_desc = f"Last {days} days"
            
            return {
                "view_type": effective_view_type,
                "period": period_desc,
                "data": trend_data,
                "summary": {
                    "total_revenue": sum(t["revenue"] for t in trend_data),
                    "total_orders": sum(t["orders"] for t in trend_data),
                    "avg_revenue_per_period": sum(t["revenue"] for t in trend_data) / len(trend_data) if trend_data else 0,
                    "growth_rate": next((t["revenue_growth"] for t in reversed(trend_data) if t["revenue"] > 0), 0)
                }
            }
            
        except Exception as e:
            print(f"Error in get_revenue_trends: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_comprehensive_historical_analytics(
        db: Session, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get complete historical analytics dashboard
        """
        try:
            # Calculate days for different views based on date range
            if start_date and end_date:
                days = (end_date - start_date).days + 1
                daily_days = min(days, 90)  # Limit to 90 days for daily view
                weekly_days = max(days // 7, 12)  # At least 12 weeks
                monthly_days = max(days // 30, 12)  # At least 12 months
            else:
                daily_days = 30
                weekly_days = 90
                monthly_days = 365
            
            return {
                "kpi_metrics": HistoricalAnalyticsService.get_kpi_metrics(db, start_date, end_date),
                "revenue_by_time_slot": HistoricalAnalyticsService.get_revenue_by_time_slot(db, None, start_date, end_date),
                "item_performance": HistoricalAnalyticsService.get_item_performance_analysis(db, 30, start_date, end_date),
                "revenue_trends": {
                    "daily": HistoricalAnalyticsService.get_revenue_trends(db, "daily", daily_days, start_date, end_date),
                    "weekly": HistoricalAnalyticsService.get_revenue_trends(db, "weekly", weekly_days, start_date, end_date),
                    "monthly": HistoricalAnalyticsService.get_revenue_trends(db, "monthly", monthly_days, start_date, end_date)
                },
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error in get_comprehensive_historical_analytics: {e}")
            return {"error": str(e)}
