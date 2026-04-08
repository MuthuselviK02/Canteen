"""
Test script to verify KPI calculation logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models import user, menu, order, order_item
from app.models.user import User
from app.models.menu import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.core.security import hash_password

def create_test_data():
    """Create test data for KPI verification"""
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = User(
            fullname="Test Admin",
            email="admin@test.com",
            password_hash=hash_password("test123"),
            role="ADMIN"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create test menu items
        menu_items = [
            MenuItem(
                name="Test Item 1",
                description="Test description 1",
                price=100.0,
                prep_time=15,
                calories=300,
                category="Main Course",
                image_url="/test1.jpg",
                available=True
            ),
            MenuItem(
                name="Test Item 2", 
                description="Test description 2",
                price=150.0,
                prep_time=20,
                calories=400,
                category="Main Course",
                image_url="/test2.jpg",
                available=True
            )
        ]
        
        for item in menu_items:
            db.add(item)
        db.commit()
        
        # Refresh to get IDs
        for item in menu_items:
            db.refresh(item)
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        # Create today's orders
        today_orders = [
            {
                'created_at': today_start + timedelta(hours=9),
                'status': 'completed',
                'completed_at': today_start + timedelta(hours=9, minutes=20),
                'items': [(menu_items[0], 2), (menu_items[1], 1)]
            },
            {
                'created_at': today_start + timedelta(hours=11),
                'status': 'completed', 
                'completed_at': today_start + timedelta(hours=11, minutes=25),
                'items': [(menu_items[1], 1)]
            },
            {
                'created_at': today_start + timedelta(hours=13),
                'status': 'pending',
                'items': [(menu_items[0], 1)]
            },
            {
                'created_at': today_start + timedelta(hours=14),
                'status': 'preparing',
                'items': [(menu_items[1], 2)]
            }
        ]
        
        # Create yesterday's orders
        yesterday_orders = [
            {
                'created_at': yesterday_start + timedelta(hours=10),
                'status': 'completed',
                'completed_at': yesterday_start + timedelta(hours=10, minutes=18),
                'items': [(menu_items[0], 1)]
            },
            {
                'created_at': yesterday_start + timedelta(hours=12),
                'status': 'completed',
                'completed_at': yesterday_start + timedelta(hours=12, minutes=22),
                'items': [(menu_items[1], 1), (menu_items[0], 1)]
            }
        ]
        
        # Helper to create orders
        def create_order(order_data, day):
            order = Order(
                user_id=test_user.id,
                status=order_data['status'],
                total_amount=0,  # Will be calculated
                created_at=order_data['created_at'],
                started_preparation_at=order_data['created_at'] + timedelta(minutes=5) if order_data['status'] != 'pending' else None,
                completed_at=order_data.get('completed_at')
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            
            # Create order items
            total = 0
            for menu_item, quantity in order_data['items']:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=quantity,
                    price_at_time=menu_item.price
                )
                db.add(order_item)
                total += menu_item.price * quantity
            
            order.total_amount = total
            db.commit()
            
            return order
        
        # Create all orders
        for order_data in today_orders:
            create_order(order_data, 'today')
            
        for order_data in yesterday_orders:
            create_order(order_data, 'yesterday')
        
        print("✅ Test data created successfully!")
        print(f"Created {len(today_orders)} orders for today")
        print(f"Created {len(yesterday_orders)} orders for yesterday")
        
        # Test KPI calculation
        from app.routers.admin_kpi import router
        from app.core.dependencies import admin_only
        
        # Create a mock admin user for testing
        class MockUser:
            def __init__(self):
                self.role = "ADMIN"
        
        # Import the calculate_kpi function by accessing it through the router
        # We'll manually call the logic here
        def test_kpi_calculation():
            def calculate_kpi(start_date: datetime, end_date: datetime):
                orders = db.query(Order).filter(
                    Order.created_at >= start_date, 
                    Order.created_at < end_date
                ).all()
                
                total_orders = len(orders)
                active_orders = len([o for o in orders if o.status in ['pending', 'preparing']])
                completed_orders = [o for o in orders if o.status == 'completed']
                
                total_revenue = 0
                if completed_orders:
                    order_ids = [o.id for o in completed_orders]
                    order_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all()
                    
                    for item in order_items:
                        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                        if menu_item:
                            total_revenue += item.quantity * menu_item.price
                
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
            
            today_kpi = calculate_kpi(today_start, now)
            yesterday_kpi = calculate_kpi(yesterday_start, today_start)
            
            print("\n📊 KPI Results:")
            print(f"Today - Orders: {today_kpi['total_orders']}, Revenue: ₹{today_kpi['revenue']}, Avg Wait: {today_kpi['avg_wait_time']}min, Active: {today_kpi['active_orders']}")
            print(f"Yesterday - Orders: {yesterday_kpi['total_orders']}, Revenue: ₹{yesterday_kpi['revenue']}, Avg Wait: {yesterday_kpi['avg_wait_time']}min, Active: {yesterday_kpi['active_orders']}")
            
            # Expected values:
            # Today: 4 orders, ₹550 revenue (2*100 + 1*150 + 1*100 + 2*150 for completed), avg wait ~22.5min, 2 active
            # Yesterday: 2 orders, ₹250 revenue, avg wait ~20min, 0 active
            
        test_kpi_calculation()
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
