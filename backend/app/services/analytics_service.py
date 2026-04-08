from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, extract

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.models.user import User


class AnalyticsService:
    """Service for generating comprehensive analytics data"""
    
    @staticmethod
    def get_comprehensive_analytics(db: Session) -> Dict[str, Any]:
        """
        Get comprehensive analytics data for the dashboard with real-time calculations
        """
        try:
            # Get current IST time by adding 5.5 hours to UTC
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            
            # Calculate IST date boundaries
            ist_today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            ist_yesterday = ist_today - timedelta(days=1)
            ist_week_start = ist_today - timedelta(days=ist_today.weekday())
            ist_last_week_start = ist_week_start - timedelta(days=7)
            ist_month_start = ist_today.replace(day=1)
            ist_last_month_start = (ist_month_start - timedelta(days=1)).replace(day=1)
            
            # Convert IST boundaries back to UTC for database queries
            today_utc = ist_today - ist_offset
            yesterday_utc = ist_yesterday - ist_offset
            week_start_utc = ist_week_start - ist_offset
            last_week_start_utc = ist_last_week_start - ist_offset
            month_start_utc = ist_month_start - ist_offset
            last_month_start_utc = ist_last_month_start - ist_offset
            now_utc = now
            
            # Get overview metrics
            overview = AnalyticsService.get_overview_metrics(db)
            
            # Get detailed analytics with time periods
            today_data = AnalyticsService.get_period_analytics(db, today_utc, now_utc)
            yesterday_data = AnalyticsService.get_period_analytics(db, yesterday_utc, today_utc)
            this_week_data = AnalyticsService.get_period_analytics(db, week_start_utc, now_utc)
            last_week_data = AnalyticsService.get_period_analytics(db, last_week_start_utc, week_start_utc)
            this_month_data = AnalyticsService.get_period_analytics(db, month_start_utc, now_utc)
            last_month_data = AnalyticsService.get_period_analytics(db, last_month_start_utc, month_start_utc)
            
            # Get specialized analytics
            revenue = AnalyticsService.get_revenue_analytics(db, 30)
            menu = AnalyticsService.get_menu_analytics(db, 30)
            users = AnalyticsService.get_user_analytics(db, 30)
            orders = AnalyticsService.get_order_analytics(db, 30)
            kitchen = AnalyticsService.get_kitchen_analytics(db)
            
            # Calculate growth metrics
            growth = AnalyticsService.calculate_growth_metrics(
                today_data, yesterday_data, this_week_data, last_week_data,
                this_month_data, last_month_data
            )
            
            # Get peak hour analysis
            peak_hour = AnalyticsService.get_peak_hour_analysis(db, today_utc, now_utc)
            
            # Get status breakdown
            status_breakdown = AnalyticsService.get_status_breakdown(db)
            
            # Combine all data
            analytics_data = {
                **overview,
                "today": today_data,
                "yesterday": yesterday_data,
                "this_week": this_week_data,
                "last_week": last_week_data,
                "this_month": this_month_data,
                "last_month": last_month_data,
                "growth": growth,
                "revenue": revenue,
                "menu": menu,
                "users": users,
                "orders": orders,
                "kitchen": kitchen,
                "peak_hour": peak_hour,
                "status_breakdown": status_breakdown,
                "generated_at": now.isoformat()
            }
            
            return analytics_data
            
        except Exception as e:
            print(f"Error in comprehensive analytics: {e}")
            return AnalyticsService.get_fallback_analytics()
    
    @staticmethod
    def get_period_analytics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get analytics for a specific time period
        """
        # Get orders in period
        orders = db.query(Order).filter(
            and_(Order.created_at >= start_date, Order.created_at < end_date)
        ).all()
        
        completed_orders = [o for o in orders if o.status == 'completed']
        
        # Calculate total revenue (from order items)
        order_ids = [o.id for o in orders]
        order_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all() if order_ids else []
        
        total_revenue = sum(
            db.query(MenuItem.price).filter(MenuItem.id == item.menu_item_id).scalar() or 0 * item.quantity
            for item in order_items
        )
        
        # Get new users in period
        new_users = db.query(User).filter(
            and_(User.created_at >= start_date, User.created_at < end_date)
        ).count()
        
        # Calculate average order value
        avg_order_value = total_revenue / len(completed_orders) if completed_orders else 0
        
        return {
            "orders": len(orders),
            "completed_orders": len(completed_orders),
            "revenue": total_revenue,
            "new_users": new_users,
            "avg_order_value": avg_order_value
        }
    
    @staticmethod
    def calculate_growth_metrics(
        today_data, yesterday_data, this_week_data, last_week_data,
        this_month_data, last_month_data
    ) -> Dict[str, Any]:
        """
        Calculate growth metrics between periods
        """
        def calculate_growth(current, previous) -> float:
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100
        
        return {
            "daily": {
                "orders_growth_percent": calculate_growth(today_data["orders"], yesterday_data["orders"]),
                "revenue_growth_percent": calculate_growth(today_data["revenue"], yesterday_data["revenue"]),
                "users_growth_percent": calculate_growth(today_data["new_users"], yesterday_data["new_users"])
            },
            "weekly": {
                "orders_growth_percent": calculate_growth(this_week_data["orders"], last_week_data["orders"]),
                "revenue_growth_percent": calculate_growth(this_week_data["revenue"], last_week_data["revenue"])
            },
            "monthly": {
                "orders_growth_percent": calculate_growth(this_month_data["orders"], last_month_data["orders"]),
                "revenue_growth_percent": calculate_growth(this_month_data["revenue"], last_month_data["revenue"])
            }
        }
    
    @staticmethod
    def get_peak_hour_analysis(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Find peak hour for orders
        """
        # Get hourly order counts
        hourly_orders = db.query(
            extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('orders')
        ).filter(
            and_(Order.created_at >= start_date, Order.created_at < end_date)
        ).group_by(extract('hour', Order.created_at)).all()
        
        if not hourly_orders:
            return {"hour": 12, "orders": 0}
        
        # Find peak hour
        peak_hour_data = max(hourly_orders, key=lambda x: x[1])
        
        return {
            "hour": int(peak_hour_data[0]),
            "orders": peak_hour_data[1]
        }
    
    @staticmethod
    def get_status_breakdown(db: Session) -> Dict[str, int]:
        """
        Get breakdown of orders by status
        """
        status_counts = db.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        return {status: count for status, count in status_counts}
    
    @staticmethod
    def get_overview_metrics(db: Session) -> Dict[str, Any]:
        """
        Get overview metrics with day-over-day comparisons
        """
        try:
            # Get current IST time by adding 5.5 hours to UTC
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            
            # Calculate IST date boundaries
            ist_today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            ist_yesterday = ist_today - timedelta(days=1)
            ist_week_start = ist_today - timedelta(days=ist_today.weekday())
            ist_last_week_start = ist_week_start - timedelta(weeks=1)
            
            # Convert IST boundaries back to UTC for database queries
            today_start = ist_today - ist_offset
            yesterday_start = ist_yesterday - ist_offset
            week_start = ist_week_start - ist_offset
            last_week_start = ist_last_week_start - ist_offset
            month_start = now.replace(day=1)
            last_month_start = (month_start - timedelta(days=1)).replace(day=1)
            
            # Helper function to get period stats
            def get_period_stats(start_date: datetime, end_date: Optional[datetime] = None):
                query = db.query(Order).filter(Order.created_at >= start_date)
                if end_date:
                    query = query.filter(Order.created_at < end_date)
                
                orders = query.all()
                completed_orders = [o for o in orders if o.status == 'completed']
                
                # Calculate revenue from completed orders
                total_revenue = 0
                for order in completed_orders:
                    for item in order.items:
                        total_revenue += item.quantity * item.menu_item.price
                
                return {
                    'orders': len(orders),
                    'completed_orders': len(completed_orders),
                    'revenue': total_revenue,
                    'new_users': 0  # Will be calculated separately
                }
            
            # Today's stats
            today_stats = get_period_stats(today_start)
            
            # Yesterday's stats
            yesterday_stats = get_period_stats(yesterday_start, today_start)
            
            # This week's stats
            this_week_stats = get_period_stats(week_start)
            
            # Last week's stats
            last_week_stats = get_period_stats(last_week_start, week_start)
            
            # This month's stats
            this_month_stats = get_period_stats(month_start)
            
            # Last month's stats
            last_month_stats = get_period_stats(last_month_start, month_start)
            
            # Calculate growth percentages
            def calculate_growth(current: float, previous: float) -> float:
                if previous == 0:
                    return 100.0 if current > 0 else 0.0
                return ((current - previous) / previous) * 100
            
            # Get total users
            total_users = db.query(User).count()
            
            # Calculate food industry metrics
            food_metrics = AnalyticsService._calculate_food_industry_metrics(db, today_start)
            
            # Get status breakdown
            status_breakdown = {}
            all_orders = db.query(Order).filter(Order.created_at >= today_start).all()
            for order in all_orders:
                status_breakdown[order.status] = status_breakdown.get(order.status, 0) + 1
            
            # Find peak hour
            peak_hour = AnalyticsService._find_peak_hour(db, today_start)
            
            return {
                'overview': {
                    'total_orders': len(all_orders),
                    'total_revenue': today_stats['revenue'],
                    'total_users': total_users,
                    'avg_order_value': today_stats['revenue'] / today_stats['completed_orders'] if today_stats['completed_orders'] > 0 else 0,
                    'avg_preparation_time_minutes': food_metrics['avg_prep_time'],
                    'table_turnover_rate': food_metrics['table_turnover_rate'],
                    'customer_retention_rate': food_metrics['customer_retention_rate'],
                    'revenue_per_customer': food_metrics['revenue_per_customer'],
                    'gross_profit_margin': food_metrics['gross_profit_margin'],
                },
                'today': {
                    'orders': today_stats['orders'],
                    'completed_orders': today_stats['completed_orders'],
                    'revenue': today_stats['revenue'],
                    'new_users': 0,  # TODO: Implement user registration tracking
                    'avg_order_value': today_stats['revenue'] / today_stats['completed_orders'] if today_stats['completed_orders'] > 0 else 0,
                },
                'yesterday': {
                    'orders': yesterday_stats['orders'],
                    'completed_orders': yesterday_stats['completed_orders'],
                    'revenue': yesterday_stats['revenue'],
                    'new_users': 0,
                    'avg_order_value': yesterday_stats['revenue'] / yesterday_stats['completed_orders'] if yesterday_stats['completed_orders'] else 0,
                },
                'this_week': {
                    'orders': this_week_stats['orders'],
                    'revenue': this_week_stats['revenue'],
                    'avg_order_value': this_week_stats['revenue'] / this_week_stats['completed_orders'] if this_week_stats['completed_orders'] else 0,
                },
                'last_week': {
                    'orders': last_week_stats['orders'],
                    'revenue': last_week_stats['revenue'],
                    'avg_order_value': last_week_stats['revenue'] / last_week_stats['completed_orders'] if last_week_stats['completed_orders'] else 0,
                },
                'this_month': {
                    'orders': this_month_stats['orders'],
                    'revenue': this_month_stats['revenue'],
                    'avg_order_value': this_month_stats['revenue'] / this_month_stats['completed_orders'] if this_month_stats['completed_orders'] else 0,
                },
                'last_month': {
                    'orders': last_month_stats['orders'],
                    'revenue': last_month_stats['revenue'],
                    'avg_order_value': last_month_stats['revenue'] / last_month_stats['completed_orders'] if last_month_stats['completed_orders'] else 0,
                },
                'growth': {
                    'daily': {
                        'orders_growth_percent': calculate_growth(today_stats['orders'], yesterday_stats['orders']),
                        'revenue_growth_percent': calculate_growth(today_stats['revenue'], yesterday_stats['revenue']),
                        'users_growth_percent': 0.0,  # TODO: Implement user growth tracking
                    },
                    'weekly': {
                        'orders_growth_percent': calculate_growth(this_week_stats['orders'], last_week_stats['orders']),
                        'revenue_growth_percent': calculate_growth(this_week_stats['revenue'], last_week_stats['revenue']),
                    },
                    'monthly': {
                        'orders_growth_percent': calculate_growth(this_month_stats['orders'], last_month_stats['orders']),
                        'revenue_growth_percent': calculate_growth(this_month_stats['revenue'], last_month_stats['revenue']),
                    },
                },
                'food_industry_metrics': food_metrics,
                'status_breakdown': status_breakdown,
                'peak_hour': peak_hour,
            }
            
        except Exception as e:
            print(f"Error in overview metrics: {e}")
            return AnalyticsService.get_fallback_overview()
    
    @staticmethod
    def _calculate_food_industry_metrics(db: Session, today_start: datetime) -> Dict[str, Any]:
        """
        Calculate food industry specific metrics
        """
        try:
            # Average preparation time
            completed_orders = db.query(Order).filter(
                and_(
                    Order.created_at >= today_start,
                    Order.status == 'completed',
                    Order.started_preparation_at.isnot(None),
                    Order.completed_at.isnot(None)
                )
            ).all()
            
            prep_times = []
            for order in completed_orders:
                prep_time = (order.completed_at - order.started_preparation_at).total_seconds() / 60
                prep_times.append(prep_time)
            
            avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else 15.0
            
            # Table turnover rate (orders per hour during peak times 12-2 PM)
            peak_orders = db.query(Order).filter(
                and_(
                    Order.created_at >= today_start,
                    func.extract('hour', Order.created_at).between(12, 14)
                )
            ).count()
            
            peak_hours = 3  # 12-2 PM is 3 hours
            table_turnover_rate = peak_orders / peak_hours if peak_hours > 0 else 0
            
            # Customer retention rate (simplified - customers who ordered more than once)
            customer_orders = {}
            for order in completed_orders:
                if order.user_id not in customer_orders:
                    customer_orders[order.user_id] = 0
                customer_orders[order.user_id] += 1
            
            returning_customers = len([count for count in customer_orders.values() if count > 1])
            total_customers = len(customer_orders)
            customer_retention_rate = (returning_customers / total_customers * 100) if total_customers > 0 else 0
            
            # Revenue per customer
            total_revenue = 0
            for order in completed_orders:
                for item in order.items:
                    total_revenue += item.quantity * item.menu_item.price
            
            revenue_per_customer = total_revenue / total_customers if total_customers > 0 else 0
            
            # Gross profit margin (assuming 30% food cost)
            food_cost_percentage = 30
            gross_profit_margin = 100 - food_cost_percentage
            
            # Top selling items
            top_items_query = db.query(
                MenuItem.name,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.quantity * MenuItem.price).label('total_revenue')
            ).select_from(
                MenuItem
            ).join(
                OrderItem, MenuItem.id == OrderItem.menu_item_id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                and_(
                    Order.created_at >= today_start,
                    Order.status == 'completed'
                )
            ).group_by(MenuItem.id, MenuItem.name).order_by(
                desc(func.sum(OrderItem.quantity))
            ).limit(10).all()
            
            top_items = [
                {
                    'name': item.name,
                    'quantity': int(item.total_quantity),
                    'revenue': float(item.total_revenue)
                }
                for item in top_items_query
            ]
            
            # Calculate food cost and profit
            estimated_food_cost = total_revenue * (food_cost_percentage / 100)
            gross_profit = total_revenue - estimated_food_cost
            
            return {
                'top_items': top_items,
                'food_cost_percentage': food_cost_percentage,
                'estimated_food_cost': estimated_food_cost,
                'gross_profit': gross_profit,
                'gross_profit_margin': gross_profit_margin,
                'table_turnover_rate': table_turnover_rate,
                'customer_retention_rate': customer_retention_rate,
                'revenue_per_customer': revenue_per_customer,
                'avg_prep_time': avg_prep_time,
            }
            
        except Exception as e:
            print(f"Error calculating food industry metrics: {e}")
            return AnalyticsService.get_fallback_food_metrics()
    
    @staticmethod
    def _find_peak_hour(db: Session, today_start: datetime) -> Dict[str, Any]:
        """
        Find the peak hour for orders
        """
        try:
            peak_hour_query = db.query(
                func.extract('hour', Order.created_at).label('hour'),
                func.count(Order.id).label('order_count')
            ).filter(
                Order.created_at >= today_start
            ).group_by(
                func.extract('hour', Order.created_at)
            ).order_by(
                desc(func.count(Order.id))
            ).first()
            
            if peak_hour_query:
                return {
                    'hour': int(peak_hour_query.hour),
                    'orders': int(peak_hour_query.order_count)
                }
            else:
                return {'hour': 12, 'orders': 0}
                
        except Exception as e:
            print(f"Error finding peak hour: {e}")
            return {'hour': 12, 'orders': 0}
    
    @staticmethod
    def get_revenue_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed revenue analytics
        """
        try:
            # Get current IST time by adding 5.5 hours to UTC
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            
            # Calculate IST date boundaries
            ist_today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_utc = ist_today - ist_offset
            
            start_date = today_utc - timedelta(days=days)
            
            # Daily revenue - use IST date conversion
            daily_revenue = db.query(
                func.date(Order.created_at + ist_offset).label('date'),
                func.count(Order.id).label('orders'),
                func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
            ).select_from(
                Order
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                MenuItem, MenuItem.id == OrderItem.menu_item_id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).group_by(
                func.date(Order.created_at + ist_offset)
            ).order_by(
                func.date(Order.created_at + ist_offset)
            ).all()
            
            # Calculate average order value for each day
            daily_data = []
            for day in daily_revenue:
                avg_order_value = day.revenue / day.orders if day.orders > 0 else 0
                # Handle both date objects and strings
                if hasattr(day.date, 'strftime'):
                    date_str = day.date.strftime('%Y-%m-%d')
                else:
                    date_str = str(day.date)
                daily_data.append({
                    'date': date_str,
                    'orders': int(day.orders),
                    'revenue': float(day.revenue),
                    'avg_order_value': float(avg_order_value)
                })
            
            # Hourly revenue (today only) - use IST time
            hourly_revenue = db.query(
                func.extract('hour', Order.created_at + ist_offset).label('hour'),
                func.count(Order.id).label('orders'),
                func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
            ).select_from(
                Order
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                MenuItem, MenuItem.id == OrderItem.menu_item_id
            ).filter(
                and_(
                    Order.created_at >= today_utc,
                    Order.status == 'completed'
                )
            ).group_by(
                func.extract('hour', Order.created_at + ist_offset)
            ).order_by(
                func.extract('hour', Order.created_at + ist_offset)
            ).all()
            
            hourly_data = []
            for hour in hourly_revenue:
                hourly_data.append({
                    'hour': int(hour.hour),
                    'orders': int(hour.orders),
                    'revenue': float(hour.revenue)
                })
            
            # Day of week revenue
            dow_revenue = db.query(
                func.extract('dow', Order.created_at).label('day_of_week'),
                func.count(Order.id).label('orders'),
                func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
            ).select_from(
                Order
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                MenuItem, MenuItem.id == OrderItem.menu_item_id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).group_by(
                func.extract('dow', Order.created_at)
            ).order_by(
                func.extract('dow', Order.created_at)
            ).all()
            
            dow_data = []
            for dow in dow_revenue:
                dow_data.append({
                    'day_of_week': int(dow.day_of_week),
                    'orders': int(dow.orders),
                    'revenue': float(dow.revenue)
                })
            
            return {
                'daily_revenue': daily_data,
                'hourly_revenue': hourly_data,
                'dow_revenue': dow_data
            }
            
        except Exception as e:
            print(f"Error in revenue analytics: {e}")
            return {
                'daily_revenue': [],
                'hourly_revenue': [],
                'dow_revenue': []
            }
    
    @staticmethod
    def get_menu_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed menu analytics with performance metrics
        """
        try:
            now = datetime.utcnow()
            start_date = now - timedelta(days=days)
            
            # Top selling items
            top_items = db.query(
                MenuItem.name,
                MenuItem.category,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.quantity * MenuItem.price).label('total_revenue'),
                func.count(func.distinct(OrderItem.order_id)).label('order_count')
            ).select_from(
                MenuItem
            ).join(
                OrderItem, MenuItem.id == OrderItem.menu_item_id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).group_by(MenuItem.id, MenuItem.name, MenuItem.category).order_by(
                desc(func.sum(OrderItem.quantity))
            ).limit(20).all()
            
            # Category performance
            category_performance = db.query(
                MenuItem.category,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.quantity * MenuItem.price).label('total_revenue'),
                func.count(func.distinct(OrderItem.order_id)).label('order_count')
            ).join(
                OrderItem, MenuItem.id == OrderItem.menu_item_id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).group_by(MenuItem.category).all()
            
            return {
                'top_items': [
                    {
                        'name': item.name,
                        'category': item.category,
                        'orders': int(item.order_count),
                        'revenue': float(item.total_revenue)
                    } for item in top_items
                ],
                'category_performance': {
                    cat.category: {
                        'orders': int(cat.order_count),
                        'revenue': float(cat.total_revenue)
                    } for cat in category_performance
                }
            }
            
        except Exception as e:
            print(f"Error in menu analytics: {e}")
            return {
                'top_items': [],
                'category_performance': {}
            }
    
    @staticmethod
    def get_user_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get user behavior analytics
        """
        try:
            now = datetime.utcnow()
            start_date = now - timedelta(days=days)
            
            # User statistics
            total_users = db.query(User).count()
            active_users = db.query(
                func.count(func.distinct(Order.user_id))
            ).join(
                Order, User.id == Order.user_id
            ).filter(
                Order.created_at >= start_date
            ).scalar() or 0
            
            # Average orders per user
            total_orders = db.query(Order).filter(
                Order.created_at >= start_date
            ).count()
            
            avg_orders_per_user = total_orders / active_users if active_users > 0 else 0
            
            # Average revenue per user
            total_revenue = db.query(
                func.sum(OrderItem.quantity * MenuItem.price)
            ).select_from(
                Order
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                MenuItem, MenuItem.id == OrderItem.menu_item_id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).scalar() or 0
            
            avg_revenue_per_user = total_revenue / active_users if active_users > 0 else 0
            
            # Customer lifetime value (simplified)
            avg_customer_lifetime_value = avg_revenue_per_user * 3  # Assume 3 orders average
            
            # Top customers
            top_customers = db.query(
                User.fullname,
                User.email,
                func.count(Order.id).label('order_count'),
                func.sum(OrderItem.quantity * MenuItem.price).label('total_spent')
            ).select_from(
                User
            ).join(
                Order, User.id == Order.user_id
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                MenuItem, MenuItem.id == OrderItem.menu_item_id
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).group_by(User.id, User.name, User.email).order_by(
                desc(func.sum(OrderItem.quantity * MenuItem.price))
            ).limit(10).all()
            
            # User roles distribution
            user_roles = db.query(
                User.role,
                func.count(User.id).label('count')
            ).group_by(User.role).all()
            
            return {
                'user_statistics': {
                    'avg_orders_per_user': round(avg_orders_per_user, 2),
                    'avg_revenue_per_user': round(avg_revenue_per_user, 2),
                    'total_active_users': active_users,
                    'avg_customer_lifetime_value': round(avg_customer_lifetime_value, 2),
                },
                'top_customers': [
                    {
                        'name': customer.name,
                        'email': customer.email,
                        'order_count': int(customer.order_count),
                        'total_spent': float(customer.total_spent),
                        'avg_order_value': float(customer.total_spent / customer.order_count) if customer.order_count > 0 else 0
                    }
                    for customer in top_customers
                ],
                'user_roles': {role.role: int(role.count) for role in user_roles}
            }
            
        except Exception as e:
            print(f"Error in user analytics: {e}")
            return {
                'user_statistics': {
                    'avg_orders_per_user': 0,
                    'avg_revenue_per_user': 0,
                    'total_active_users': 0,
                    'avg_customer_lifetime_value': 0,
                },
                'top_customers': [],
                'user_roles': {}
            }
    
    @staticmethod
    def get_order_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed order analytics
        """
        try:
            now = datetime.utcnow()
            start_date = now - timedelta(days=days)
            
            # Performance metrics
            total_orders = db.query(Order).filter(Order.created_at >= start_date).count()
            completed_orders = db.query(Order).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed'
                )
            ).count()
            
            completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            
            # Average preparation time
            prep_times = []
            completed_with_times = db.query(Order).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status == 'completed',
                    Order.started_preparation_at.isnot(None),
                    Order.completed_at.isnot(None)
                )
            ).all()
            
            for order in completed_with_times:
                prep_time = (order.completed_at - order.started_preparation_at).total_seconds() / 60
                prep_times.append(prep_time)
            
            avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else 0
            
            return {
                'performance_metrics': {
                    'avg_preparation_time_minutes': round(avg_prep_time, 2),
                    'completion_rate_percent': round(completion_rate, 2),
                    'total_orders': total_orders,
                    'completed_orders': completed_orders,
                }
            }
            
        except Exception as e:
            print(f"Error in order analytics: {e}")
            return {
                'performance_metrics': {
                    'avg_preparation_time_minutes': 0,
                    'completion_rate_percent': 0,
                    'total_orders': 0,
                    'completed_orders': 0,
                }
            }
    
    @staticmethod
    def get_kitchen_analytics(db: Session) -> Dict[str, Any]:
        """
        Get enhanced kitchen-specific analytics for operational efficiency
        """
        try:
            # Get current IST time by adding 5.5 hours to UTC
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            
            # Calculate IST date boundaries
            ist_today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Convert IST boundaries back to UTC for database queries
            today_start = ist_today - ist_offset
            
            # Get today's orders
            today_orders = db.query(Order).filter(Order.created_at >= today_start).all()
            
            # Completed orders today
            completed_orders = [o for o in today_orders if o.status == 'completed']
            
            # Calculate preparation times
            prep_times = []
            for order in completed_orders:
                if order.started_preparation_at and order.completed_at:
                    prep_time = (order.completed_at - order.started_preparation_at).total_seconds() / 60
                    prep_times.append(prep_time)
            
            avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else 0
            fastest_prep = min(prep_times) if prep_times else 0
            slowest_prep = max(prep_times) if prep_times else 0
            
            # Current queue status
            pending_count = len([o for o in today_orders if o.status == 'pending'])
            preparing_count = len([o for o in today_orders if o.status == 'preparing'])
            ready_count = len([o for o in today_orders if o.status == 'ready'])
            
            # Efficiency metrics
            completion_rate = (len(completed_orders) / len(today_orders) * 100) if today_orders else 0
            
            # Calculate orders per hour
            hours_elapsed = max(1, (now - today_start).total_seconds() / 3600)
            avg_orders_per_hour = len(completed_orders) / hours_elapsed
            
            # Peak hour performance (12-2 PM)
            peak_hour_orders = [o for o in completed_orders if 12 <= o.created_at.hour <= 14]
            peak_hour_performance = len(peak_hour_orders)
            
            # Efficiency score (0-100)
            efficiency_score = min(100, round(
                (completion_rate * 0.4) + 
                (40 if avg_orders_per_hour > 10 else avg_orders_per_hour * 4) + 
                (20 if avg_prep_time < 15 else max(0, 20 - avg_prep_time))
            ))
            
            # Alerts
            long_waiting_orders = 0
            overdue_orders = 0
            
            for order in today_orders:
                if order.status in ['pending', 'preparing']:
                    wait_time = (now - order.created_at).total_seconds() / 60
                    if wait_time > 30:
                        long_waiting_orders += 1
                    
                    if order.predicted_wait_time and wait_time > order.predicted_wait_time + 10:
                        overdue_orders += 1
            
            high_volume_alert = pending_count > 10 or preparing_count > 5
            
            # Hourly performance for today
            hourly_performance = []
            for hour in range(now.hour + 1):
                hour_start = today_start.replace(hour=hour)
                hour_end = hour_start + timedelta(hours=1)
                
                hour_orders = [o for o in completed_orders if hour_start <= o.created_at < hour_end]
                hour_prep_times = []
                
                for order in hour_orders:
                    if order.started_preparation_at and order.completed_at:
                        prep_time = (order.completed_at - order.started_preparation_at).total_seconds() / 60
                        hour_prep_times.append(prep_time)
                
                hour_avg_time = sum(hour_prep_times) / len(hour_prep_times) if hour_prep_times else 0
                
                hourly_performance.append({
                    "hour": hour,
                    "completed": len(hour_orders),
                    "avg_time": round(hour_avg_time, 1)
                })
            
            return {
                "today_stats": {
                    "total_orders": len(today_orders),
                    "completed_orders": len(completed_orders),
                    "avg_prep_time": round(avg_prep_time, 1),
                    "fastest_prep_time": round(fastest_prep, 1),
                    "slowest_prep_time": round(slowest_prep, 1),
                },
                "current_queue": {
                    "pending_count": pending_count,
                    "preparing_count": preparing_count,
                    "ready_count": ready_count,
                    "total_active_orders": pending_count + preparing_count + ready_count,
                },
                "efficiency": {
                    "completion_rate": round(completion_rate, 1),
                    "avg_orders_per_hour": round(avg_orders_per_hour, 1),
                    "peak_hour_performance": peak_hour_performance,
                    "efficiency_score": efficiency_score,
                },
                "alerts": {
                    "long_waiting_orders": long_waiting_orders,
                    "overdue_orders": overdue_orders,
                    "high_volume_alert": high_volume_alert,
                },
                "hourly_performance": hourly_performance,
                "kitchen_status": {
                    "status": "busy" if (pending_count + preparing_count) > 5 else "normal",
                    "estimated_clear_time": max(0, (pending_count + preparing_count) * max(15, avg_prep_time)),
                    "staff_efficiency": efficiency_score >= 70
                }
            }
            
        except Exception as e:
            print(f"Error in kitchen analytics: {e}")
            return {
                "today_stats": {
                    "total_orders": 0,
                    "completed_orders": 0,
                    "avg_prep_time": 0,
                    "fastest_prep_time": 0,
                    "slowest_prep_time": 0,
                },
                "current_queue": {
                    "pending_count": 0,
                    "preparing_count": 0,
                    "ready_count": 0,
                    "total_active_orders": 0,
                },
                "efficiency": {
                    "completion_rate": 0,
                    "avg_orders_per_hour": 0,
                    "peak_hour_performance": 0,
                    "efficiency_score": 0,
                },
                "alerts": {
                    "long_waiting_orders": 0,
                    "overdue_orders": 0,
                    "high_volume_alert": False,
                },
                "hourly_performance": [],
                "kitchen_status": {
                    "status": "normal",
                    "estimated_clear_time": 0,
                    "staff_efficiency": True
                }
            }
    
    @staticmethod
    def get_fallback_analytics() -> Dict[str, Any]:
        """Return fallback analytics data when errors occur"""
        return {
            **AnalyticsService.get_fallback_overview(),
            'revenue': {'daily_revenue': [], 'hourly_revenue': [], 'dow_revenue': []},
            'menu': {'top_items': [], 'category_performance': {}},
            'users': {'user_statistics': {}, 'top_customers': [], 'user_roles': {}},
            'orders': {'performance_metrics': {}},
            'generated_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_fallback_overview() -> Dict[str, Any]:
        """Return fallback overview data"""
        return {
            'overview': {
                'total_orders': 0,
                'total_revenue': 0,
                'total_users': 0,
                'avg_order_value': 0,
                'avg_preparation_time_minutes': 0,
                'table_turnover_rate': 0,
                'customer_retention_rate': 0,
                'revenue_per_customer': 0,
                'gross_profit_margin': 70,
            },
            'today': {'orders': 0, 'completed_orders': 0, 'revenue': 0, 'new_users': 0, 'avg_order_value': 0},
            'yesterday': {'orders': 0, 'completed_orders': 0, 'revenue': 0, 'new_users': 0, 'avg_order_value': 0},
            'this_week': {'orders': 0, 'revenue': 0, 'avg_order_value': 0},
            'last_week': {'orders': 0, 'revenue': 0, 'avg_order_value': 0},
            'this_month': {'orders': 0, 'revenue': 0, 'avg_order_value': 0},
            'last_month': {'orders': 0, 'revenue': 0, 'avg_order_value': 0},
            'growth': {
                'daily': {'orders_growth_percent': 0, 'revenue_growth_percent': 0, 'users_growth_percent': 0},
                'weekly': {'orders_growth_percent': 0, 'revenue_growth_percent': 0},
                'monthly': {'orders_growth_percent': 0, 'revenue_growth_percent': 0},
            },
            'food_industry_metrics': AnalyticsService.get_fallback_food_metrics(),
            'status_breakdown': {'pending': 0, 'preparing': 0, 'ready': 0, 'completed': 0},
            'peak_hour': {'hour': 12, 'orders': 0},
        }
    
    @staticmethod
    def get_fallback_food_metrics() -> Dict[str, Any]:
        """Return fallback food industry metrics"""
        return {
            'top_items': [],
            'food_cost_percentage': 30,
            'estimated_food_cost': 0,
            'gross_profit': 0,
            'gross_profit_margin': 70,
            'table_turnover_rate': 0,
            'customer_retention_rate': 0,
            'avg_prep_time': 15,
        }
    
    @staticmethod
    def get_fallback_kitchen_analytics() -> Dict[str, Any]:
        """Return fallback kitchen analytics data"""
        return {
            'today_stats': {
                'total_orders': 0,
                'completed_orders': 0,
                'avg_prep_time': 15,
                'fastest_prep_time': 10,
                'slowest_prep_time': 20,
            },
            'current_queue': {
                'pending_count': 0,
                'preparing_count': 0,
                'ready_count': 0,
                'total_active_orders': 0,
            },
            'efficiency': {
                'completion_rate': 0,
                'avg_orders_per_hour': 0,
                'peak_hour_performance': 0,
                'efficiency_score': 50,
            },
            'alerts': {
                'long_waiting_orders': 0,
                'overdue_orders': 0,
                'high_volume_alert': False,
            },
            'hourly_performance': [],
            'generated_at': datetime.utcnow().isoformat()
        }
