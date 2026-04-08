"""
Check what happened to the pending order
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def check_order_status_change():
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
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Get all recent orders to see status changes
            kitchen_response = requests.get('http://localhost:8000/api/kitchen/orders', headers=headers)
            
            if kitchen_response.status_code == 200:
                kitchen_orders = kitchen_response.json()
                
                # Sort by creation time to see recent orders
                recent_orders = sorted(kitchen_orders, key=lambda x: x['created_at'], reverse=True)[:10]
                
                print("📋 Recent Orders (last 10):")
                for i, order in enumerate(recent_orders, 1):
                    user_name = order['user']['fullname'] if order.get('user') else 'Unknown'
                    items = [item['menu_item']['name'] for item in order['items']]
                    created_time = order['created_at'].split('T')[1].split('.')[0]  # Extract time part
                    
                    print(f"{i}. Order #{order['id']}: {order['status'].upper()}")
                    print(f"   User: {user_name}")
                    print(f"   Items: {items}")
                    print(f"   Time: {created_time}")
                    print()
                
                # Specifically look for orders from "vishnu" that were mentioned in your screenshot
                vishnu_orders = [o for o in kitchen_orders if o.get('user') and o['user']['fullname'].lower() == 'vishnu']
                
                print("🔍 Vishnu's Orders:")
                for order in vishnu_orders:
                    items = [item['menu_item']['name'] for item in order['items']]
                    created_time = order['created_at'].split('T')[1].split('.')[0]
                    
                    print(f"Order #{order['id']}: {order['status'].upper()}")
                    print(f"   Items: {items}")
                    print(f"   Created: {created_time}")
                    print(f"   Queue Position: {order.get('queue_position', 'N/A')}")
                    print()
                    
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_order_status_change()
