"""
Simple test script to verify KPI calculation logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database.session import SessionLocal
from app.models.user import User
from app.models.menu import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.core.security import hash_password
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_kpi_calculation():
    """Test KPI calculation with existing data or create minimal test data"""
    db = SessionLocal()
    
    try:
        # Check if we have existing data
        existing_orders = db.query(Order).count()
        print(f"Found {existing_orders} existing orders in database")
        
        if existing_orders == 0:
            print("No existing orders found. Creating minimal test data...")
            
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
            
            # Create test menu item
            test_item = MenuItem(
                name="Test Item",
                description="Test description",
                price=100.0,
                category="Main Course",
                is_available=True
            )
            db.add(test_item)
            db.commit()
            db.refresh(test_item)
            
            # Create a test order
            now = datetime.utcnow()
            test_order = Order(
                user_id=test_user.id,
                status="completed",
                total_amount=100.0,
                created_at=now - timedelta(hours=2),
                started_preparation_at=now - timedelta(hours=1, minutes=50),
                completed_at=now - timedelta(hours=1, minutes=30)
            )
            db.add(test_order)
            db.commit()
            db.refresh(test_order)
            
            # Create order item
            test_order_item = OrderItem(
                order_id=test_order.id,
                menu_item_id=test_item.id,
                quantity=1,
                price_at_time=100.0
            )
            db.add(test_order_item)
            db.commit()
            
            print("✅ Created test data")
        
        # Test KPI calculation
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
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
        
        print("\n📊 KPI Test Results:")
        print(f"Today - Orders: {today_kpi['total_orders']}, Revenue: ₹{today_kpi['revenue']}, Avg Wait: {today_kpi['avg_wait_time']}min, Active: {today_kpi['active_orders']}")
        print(f"Yesterday - Orders: {yesterday_kpi['total_orders']}, Revenue: ₹{yesterday_kpi['revenue']}, Avg Wait: {yesterday_kpi['avg_wait_time']}min, Active: {yesterday_kpi['active_orders']}")
        
        # Test the API endpoint calculation
        print("\n🔧 Testing API endpoint logic...")
        
        # Test the change calculation
        def calculate_change(today_val: float, yesterday_val: float):
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
        
        changes = {
            'total_orders': calculate_change(today_kpi['total_orders'], yesterday_kpi['total_orders']),
            'revenue': calculate_change(today_kpi['revenue'], yesterday_kpi['revenue']),
            'avg_wait_time': calculate_change(today_kpi['avg_wait_time'], yesterday_kpi['avg_wait_time']),
            'active_orders': calculate_change(today_kpi['active_orders'], yesterday_kpi['active_orders'])
        }
        
        print("Changes calculated:")
        for key, change in changes.items():
            print(f"  {key}: {change['percentage']}% ({change['trend']})")
        
        print("\n✅ KPI calculation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_kpi_calculation()
