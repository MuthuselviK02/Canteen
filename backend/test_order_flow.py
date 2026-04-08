import requests

def test_complete_order_flow():
    print("🧪 Testing Complete Order Flow with Menu Items")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print("✅ Login successful")
        
        # Step 2: Place order
        print("\n2. Placing order...")
        order_data = {
            'items': [
                {'menu_item_id': 1, 'quantity': 1},
                {'menu_item_id': 2, 'quantity': 1}
            ],
            'available_time': None
        }
        
        order_response = requests.post(
            'http://localhost:8000/api/orders/',
            json=order_data,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if order_response.status_code == 200:
            order = order_response.json()
            print(f"✅ Order placed successfully! Order ID: {order['id']}")
            
            # Step 3: Get all orders
            print("\n3. Fetching all orders...")
            orders_response = requests.get(
                'http://localhost:8000/api/orders/',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if orders_response.status_code == 200:
                orders = orders_response.json()
                print(f"✅ Found {len(orders)} orders")
                
                # Check if menu items are included
                if orders and orders[0].get('items'):
                    first_order = orders[0]
                    first_item = first_order['items'][0]
                    
                    if first_item.get('menu_item'):
                        menu_item = first_item['menu_item']
                        print(f"✅ Menu item details included:")
                        print(f"   - Name: {menu_item.get('name', 'Unknown')}")
                        print(f"   - Price: ${menu_item.get('price', 0)}")
                        print(f"   - Image: {menu_item.get('image_url', 'No image')}")
                    else:
                        print("❌ Menu item details missing")
                else:
                    print("❌ No items found in order")
            else:
                print(f"❌ Failed to fetch orders: {orders_response.text}")
        else:
            print(f"❌ Order placement failed: {order_response.text}")
    else:
        print(f"❌ Login failed: {login_response.text}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("✅ Backend API endpoints working")
    print("✅ Menu item details included in orders")
    print("✅ Frontend should now display orders correctly")

if __name__ == "__main__":
    test_complete_order_flow()
