import requests
import json

# Debug order status updates and invoice creation
BASE_URL = "http://localhost:8000"

def debug_order_to_invoice():
    """Debug why orders aren't creating invoices"""
    login_data = {
        "email": "superadmin@admin.com",
        "password": "admin@1230"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print("❌ Login failed")
            return
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("❌ No token received")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user's orders
        orders_response = requests.get(f"{BASE_URL}/api/orders/", headers=headers)
        
        if orders_response.status_code != 200:
            print(f"❌ Failed to get orders: {orders_response.status_code}")
            return
            
        orders = orders_response.json()
        print(f"📋 Found {len(orders)} orders for user")
        
        # Check for completed orders without invoices
        completed_without_invoice = 0
        for order in orders:
            if order.get('status') == 'completed' and not order.get('invoice_id'):
                completed_without_invoice += 1
                print(f"❌ Order {order.get('id')} completed but no invoice_id: {order.get('invoice_id')}")
        
        if completed_without_invoice > 0:
            print(f"\n🚨 ISSUE: {completed_without_invoice} completed orders missing invoice_id")
            
            # Try to manually trigger invoice creation for one completed order
            test_order = None
            for order in orders:
                if order.get('status') == 'completed' and not order.get('invoice_id'):
                    test_order = order
                    break
            
            if test_order:
                print(f"\n🔧 Testing manual status update for order {test_order.get('id')}...")
                
                # Update to completed status (should trigger invoice creation)
                update_response = requests.put(
                    f"{BASE_URL}/api/orders/{test_order.get('id')}/status", 
                    json={'status': 'completed'}, 
                    headers=headers
                )
                
                if update_response.status_code == 200:
                    print(f"✅ Status updated successfully")
                    
                    # Check if invoice was created
                    time.sleep(2)  # Wait for async processing
                    
                    # Check order again
                    check_response = requests.get(f"{BASE_URL}/api/orders/{test_order.get('id')}", headers=headers)
                    if check_response.status_code == 200:
                        updated_order = check_response.json()
                        print(f"📄 Updated order: invoice_id = {updated_order.get('invoice_id')}")
                        
                        if updated_order.get('invoice_id'):
                            print(f"✅ SUCCESS: Invoice created for order {test_order.get('id')}")
                        else:
                            print(f"❌ FAILED: No invoice created for order {test_order.get('id')}")
                    else:
                        print(f"❌ Failed to check updated order: {check_response.status_code}")
                else:
                    print(f"❌ Status update failed: {update_response.status_code}")
        else:
            print("✅ All completed orders have invoice_id")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_order_to_invoice()
