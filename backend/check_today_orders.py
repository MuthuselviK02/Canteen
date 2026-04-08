#!/usr/bin/env python3
"""
Script to check today's orders in the database
"""

import sqlite3
from datetime import datetime, timedelta
import sys

def check_today_orders():
    """Check orders in database for today"""
    
    # Database file path
    db_path = "canteen.db"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking today's orders in database...")
        print(f"📁 Database: {db_path}")
        
        # Get current time and calculate IST
        utc_now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = utc_now + ist_offset
        
        print(f"🕐 UTC Time: {utc_now}")
        print(f"🕐 IST Time: {ist_now}")
        print(f"📅 Today's Date (IST): {ist_now.date()}")
        
        # Query all orders
        cursor.execute("""
            SELECT id, user_id, status, total_amount, created_at, updated_at
            FROM orders 
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        orders = cursor.fetchall()
        
        print(f"\n📊 Total orders found: {len(orders)}")
        print("=" * 80)
        
        if not orders:
            print("❌ No orders found in database!")
            return
        
        # Process each order
        today_orders = []
        
        for order in orders:
            order_id, user_id, status, total_amount, created_at, updated_at = order
            
            # Parse created_at
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            # Convert to IST
            ist_created = created_dt + ist_offset
            
            print(f"\n📋 Order #{order_id}")
            print(f"   User ID: {user_id}")
            print(f"   Status: {status}")
            print(f"   Amount: ₹{total_amount}")
            print(f"   Created (UTC): {created_at}")
            print(f"   Created (IST): {ist_created}")
            print(f"   Date (IST): {ist_created.date()}")
            print(f"   Hour (IST): {ist_created.hour}:00")
            
            # Check if it's today
            if ist_created.date() == ist_now.date():
                today_orders.append(order)
                print("   ✅ TODAY'S ORDER!")
            else:
                print("   ❌ Not today")
        
        print("\n" + "=" * 80)
        print(f"📈 TODAY'S ORDERS SUMMARY")
        print(f"   Total today's orders: {len(today_orders)}")
        
        if today_orders:
            print("\n📋 Today's Orders Details:")
            for order in today_orders:
                order_id, user_id, status, total_amount, created_at, updated_at = order
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                ist_created = created_dt + ist_offset
                
                print(f"   Order #{order_id}: {ist_created.strftime('%I:%M %p')} - ₹{total_amount} ({status})")
                
                # Check hour
                hour = ist_created.hour
                if hour == 0:
                    print(f"      → 12:00 AM - 12:59 AM slot ⚠️")
                elif hour == 1:
                    print(f"      → 1:00 AM - 1:59 AM slot ⚠️ (CURRENT)")
                else:
                    print(f"      → {hour}:00 - {hour}:59 slot")
        else:
            print("   ❌ No orders found for today!")
        
        # Also check order items for today's orders
        if today_orders:
            print("\n🛒 ORDER ITEMS FOR TODAY'S ORDERS:")
            for order in today_orders:
                order_id, user_id, status, total_amount, created_at, updated_at = order
                
                cursor.execute("""
                    SELECT oi.id, oi.menu_item_id, oi.quantity, oi.price_at_time, mi.name
                    FROM order_items oi
                    LEFT JOIN menu_items mi ON oi.menu_item_id = mi.id
                    WHERE oi.order_id = ?
                """, (order_id,))
                
                items = cursor.fetchall()
                
                print(f"\n   Order #{order_id} items:")
                for item in items:
                    item_id, menu_item_id, quantity, price_at_time, name = item
                    print(f"      - {name or f'Item {menu_item_id}'} x{quantity} = ₹{price_at_time}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_today_orders()
