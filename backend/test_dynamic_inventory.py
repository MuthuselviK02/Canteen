#!/usr/bin/env python3
"""
Test Dynamic Inventory Updates

This script tests the complete flow of:
1. Creating orders
2. Completing orders
3. Verifying inventory updates
4. Testing the sync endpoint
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
API_URL = "http://localhost:8000"
ADMIN_TOKEN = None
USER_TOKEN = None

def login_admin():
    """Login as admin and get token"""
    global ADMIN_TOKEN
    response = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "admin@canteen.com",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        ADMIN_TOKEN = data["access_token"]
        print("✅ Admin login successful")
        return True
    else:
        print(f"❌ Admin login failed: {response.text}")
        return False

def login_user():
    """Login as regular user and get token"""
    global USER_TOKEN
    response = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "user@canteen.com", 
        "password": "user123"
    })
    
    if response.status_code == 200:
        data = response.json()
        USER_TOKEN = data["access_token"]
        print("✅ User login successful")
        return True
    else:
        print(f"❌ User login failed: {response.text}")
        return False

def get_menu_items():
    """Get available menu items"""
    response = requests.get(f"{API_URL}/api/menu/")
    
    if response.status_code == 200:
        items = response.json()
        print(f"✅ Found {len(items)} menu items")
        return items
    else:
        print(f"❌ Failed to get menu items: {response.text}")
        return []

def get_current_inventory():
    """Get current inventory status"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    
    # Get today's date range
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    response = requests.get(
        f"{API_URL}/api/inventory/dashboard",
        headers=headers,
        params={
            "start_date": today.isoformat(),
            "end_date": tomorrow.isoformat(),
            "category": "all"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Current inventory: {data['inventory_kpis']}")
        return data
    else:
        print(f"❌ Failed to get inventory: {response.text}")
        return None

def create_test_order(menu_items):
    """Create a test order"""
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    
    # Select first 2 items for the order
    order_items = []
    for item in menu_items[:2]:
        order_items.append({
            "menu_item_id": item["id"],
            "quantity": 2
        })
    
    order_data = {
        "items": order_items
    }
    
    response = requests.post(f"{API_URL}/api/orders/", json=order_data, headers=headers)
    
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Order created: ID {order['id']}")
        return order
    else:
        print(f"❌ Failed to create order: {response.text}")
        return None

def update_order_status(order_id, status):
    """Update order status"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    
    response = requests.put(
        f"{API_URL}/api/orders/{order_id}/status",
        json={"status": status},
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Order {order_id} status updated to {status}")
        return True
    else:
        print(f"❌ Failed to update order status: {response.text}")
        return False

def sync_inventory():
    """Test the inventory sync endpoint"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    
    response = requests.post(f"{API_URL}/api/inventory/sync-inventory", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Inventory sync successful: {data}")
        return True
    else:
        print(f"❌ Inventory sync failed: {response.text}")
        return False

def test_inventory_flow():
    """Test the complete inventory update flow"""
    print("\n🧪 Testing Dynamic Inventory Updates")
    print("=" * 50)
    
    # Step 1: Login
    if not login_admin() or not login_user():
        return False
    
    # Step 2: Get menu items
    menu_items = get_menu_items()
    if not menu_items:
        return False
    
    # Step 3: Get initial inventory
    print("\n📦 Initial Inventory Status:")
    initial_inventory = get_current_inventory()
    if not initial_inventory:
        return False
    
    # Step 4: Create test order
    print("\n🛒 Creating Test Order:")
    order = create_test_order(menu_items)
    if not order:
        return False
    
    # Step 5: Update order through completion flow
    print("\n📋 Updating Order Status:")
    update_order_status(order["id"], "preparing")
    time.sleep(1)
    
    update_order_status(order["id"], "ready")
    time.sleep(1)
    
    # This should trigger inventory update
    update_order_status(order["id"], "completed")
    time.sleep(2)  # Allow time for inventory update
    
    # Step 6: Check updated inventory
    print("\n📊 Updated Inventory Status:")
    updated_inventory = get_current_inventory()
    if not updated_inventory:
        return False
    
    # Step 7: Test manual sync
    print("\n🔄 Testing Manual Sync:")
    sync_inventory()
    
    # Step 8: Final inventory check
    print("\n📈 Final Inventory Status:")
    final_inventory = get_current_inventory()
    
    # Step 9: Compare results
    print("\n📋 Inventory Comparison:")
    print(f"Initial items: {len(initial_inventory['inventory_items'])}")
    print(f"Updated items: {len(updated_inventory['inventory_items'])}")
    print(f"Final items: {len(final_inventory['inventory_items'])}")
    
    # Check if stock levels changed
    for item in initial_inventory['inventory_items']:
        item_id = item['item_id']
        initial_stock = item['remaining_stock']
        
        # Find corresponding item in final inventory
        final_item = next((i for i in final_inventory['inventory_items'] if i['item_id'] == item_id), None)
        if final_item:
            final_stock = final_item['remaining_stock']
            if initial_stock != final_stock:
                print(f"📉 Item {item_id} ({item['item_name']}): {initial_stock} → {final_stock}")
    
    print("\n✅ Dynamic inventory test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_inventory_flow()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
