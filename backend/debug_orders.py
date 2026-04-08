"""
Debug active orders discrepancy between kitchen and admin pages
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

def debug_active_orders():
    try:
        # Login as admin
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['access_token']
            print(f"✅ Login successful")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 1. Get KPI data from admin endpoint
            print("\n📊 Admin KPI Data:")
            kpi_response = requests.get('http://localhost:8000/api/admin/kpi/daily', headers=headers)
            
            if kpi_response.status_code == 200:
                kpi_data = kpi_response.json()
                print(f"Today's Active Orders: {kpi_data['today']['active_orders']}")
                print(f"Today's Total Orders: {kpi_data['today']['total_orders']}")
            else:
                print(f"❌ Failed to get KPI: {kpi_response.status_code}")
            
            # 2. Get all orders from kitchen endpoint
            print("\n🍳 Kitchen Orders Data:")
            kitchen_response = requests.get('http://localhost:8000/api/kitchen/orders', headers=headers)
            
            if kitchen_response.status_code == 200:
                kitchen_orders = kitchen_response.json()
                print(f"Total orders in kitchen: {len(kitchen_orders)}")
                
                # Count by status
                pending_count = len([o for o in kitchen_orders if o['status'].lower() == 'pending'])
                preparing_count = len([o for o in kitchen_orders if o['status'].lower() == 'preparing'])
                ready_count = len([o for o in kitchen_orders if o['status'].lower() == 'ready'])
                completed_count = len([o for o in kitchen_orders if o['status'].lower() == 'completed'])
                
                print(f"Pending: {pending_count}")
                print(f"Preparing: {preparing_count}")
                print(f"Ready: {ready_count}")
                print(f"Completed: {completed_count}")
                print(f"Active (Pending + Preparing): {pending_count + preparing_count}")
                
                # Show details of active orders
                print("\n📋 Active Orders Details:")
                active_orders = [o for o in kitchen_orders if o['status'].lower() in ['pending', 'preparing']]
                for order in active_orders:
                    print(f"Order #{order['id']}: {order['status']} - User: {order['user']['fullname'] if order.get('user') else 'Unknown'}")
                    print(f"  Created: {order['created_at']}")
                    print(f"  Items: {[item['menu_item']['name'] for item in order['items']]}")
                    print()
                
            else:
                print(f"❌ Failed to get kitchen orders: {kitchen_response.status_code}")
            
            # 3. Get user's personal orders
            print("\n👤 User Orders Data:")
            user_orders_response = requests.get('http://localhost:8000/api/orders/', headers=headers)
            
            if user_orders_response.status_code == 200:
                user_orders = user_orders_response.json()
                print(f"Total user orders: {len(user_orders)}")
                
                user_active = len([o for o in user_orders if o['status'].lower() in ['pending', 'preparing']])
                print(f"User active orders: {user_active}")
                
            else:
                print(f"❌ Failed to get user orders: {user_orders_response.status_code}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_active_orders()
