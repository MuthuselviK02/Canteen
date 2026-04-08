"""
Test order placement to verify the fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_order_placement():
    try:
        # Step 1: Login as a regular user
        login_data = {
            'email': 'siva@gmail.com',  # Use existing admin user for testing
            'password': 'admin123'
        }
        
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['access_token']
            print(f"✅ Login successful")
            
            # Step 2: Get menu items
            menu_response = requests.get('http://localhost:8000/api/menu/')
            
            if menu_response.status_code == 200:
                menu_items = menu_response.json()
                if menu_items:
                    first_item = menu_items[0]
                    print(f"✅ Found menu item: {first_item['name']} (ID: {first_item['id']})")
                    
                    # Step 3: Place an order
                    order_data = {
                        'items': [
                            {
                                'menu_item_id': first_item['id'],
                                'quantity': 2
                            }
                        ],
                        'available_time': 15  # Available in 15 minutes
                    }
                    
                    headers = {
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                    
                    order_response = requests.post('http://localhost:8000/api/orders/', json=order_data, headers=headers)
                    
                    if order_response.status_code == 200:
                        order_result = order_response.json()
                        print("✅ Order placed successfully!")
                        print(f"Order ID: {order_result['id']}")
                        print(f"Status: {order_result['status']}")
                        print(f"Total: ₹{order_result.get('total_amount', 'N/A')}")
                        
                        # Step 4: Verify order appears in user's orders
                        user_orders_response = requests.get('http://localhost:8000/api/orders/', headers=headers)
                        
                        if user_orders_response.status_code == 200:
                            user_orders = user_orders_response.json()
                            print(f"✅ User has {len(user_orders)} orders")
                            
                            # Find our new order
                            new_order = next((o for o in user_orders if o['id'] == order_result['id']), None)
                            if new_order:
                                print("✅ New order appears in user's order list!")
                                print(f"Order details: {json.dumps(new_order, indent=2)}")
                                return True
                            else:
                                print("❌ New order not found in user's order list")
                                return False
                        else:
                            print(f"❌ Failed to fetch user orders: {user_orders_response.status_code}")
                            return False
                    else:
                        print(f"❌ Failed to place order: {order_response.status_code}")
                        print(order_response.text)
                        return False
                else:
                    print("❌ No menu items found")
                    return False
            else:
                print(f"❌ Failed to fetch menu: {menu_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_order_placement()
    if success:
        print("\n🎉 Order placement test completed successfully!")
        print("Orders should now appear on the Orders page!")
    else:
        print("\n💥 Order placement test failed!")
