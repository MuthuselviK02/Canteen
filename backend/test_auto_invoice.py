"""
Test automatic invoice creation when order is completed
"""
import requests
import json
import time

def test_auto_invoice_creation():
    try:
        # Login as admin
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        print("1. 🔐 Logging in as admin...")
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Login successful")
        
        # Place an order
        print("\n2. 🛒 Placing an order...")
        order_data = {
            "items": [
                {"menu_item_id": 1, "quantity": 2},
                {"menu_item_id": 2, "quantity": 1}
            ]
        }
        
        order_response = requests.post('http://localhost:8000/api/orders/', json=order_data, headers=headers)
        
        if order_response.status_code != 200:
            print(f"❌ Order placement failed: {order_response.status_code}")
            print(f"Response: {order_response.text}")
            return
        
        order = order_response.json()
        order_id = order['id']
        print(f"✅ Order placed successfully: Order ID {order_id}")
        print(f"   Status: {order.get('status')}")
        print(f"   Invoice ID: {order.get('invoice_id', 'Not created yet')}")
        
        # Update order status to preparing
        print("\n3. 👨‍🍳 Updating order status to 'preparing'...")
        status_response = requests.put(f'http://localhost:8000/api/orders/{order_id}/status', 
                                     json={'status': 'preparing'}, headers=headers)
        
        if status_response.status_code == 200:
            print("✅ Order status updated to 'preparing'")
        else:
            print(f"❌ Status update failed: {status_response.status_code}")
        
        # Update order status to ready
        print("\n4. 🍽️ Updating order status to 'ready'...")
        status_response = requests.put(f'http://localhost:8000/api/orders/{order_id}/status', 
                                     json={'status': 'ready'}, headers=headers)
        
        if status_response.status_code == 200:
            print("✅ Order status updated to 'ready'")
        else:
            print(f"❌ Status update failed: {status_response.status_code}")
        
        # Update order status to completed (this should trigger invoice creation)
        print("\n5. ✅ Updating order status to 'completed' (should auto-create invoice)...")
        status_response = requests.put(f'http://localhost:8000/api/orders/{order_id}/status', 
                                     json={'status': 'completed'}, headers=headers)
        
        if status_response.status_code == 200:
            updated_order = status_response.json()
            print("✅ Order status updated to 'completed'")
            print(f"   Invoice ID: {updated_order.get('invoice_id', 'Not created')}")
            
            if updated_order.get('invoice_id'):
                print(f"🎉 SUCCESS: Auto-created invoice {updated_order['invoice_id']}")
                
                # Check if invoice appears in billing dashboard
                print("\n6. 📊 Checking billing dashboard...")
                billing_response = requests.get('http://localhost:8002/api/billing/invoices', headers=headers)
                
                if billing_response.status_code == 200:
                    invoices = billing_response.json()
                    auto_invoice = next((inv for inv in invoices if inv['id'] == updated_order['invoice_id']), None)
                    
                    if auto_invoice:
                        print("✅ Auto-created invoice found in billing dashboard")
                        print(f"   Invoice Number: {auto_invoice.get('invoice_number')}")
                        print(f"   Status: {auto_invoice.get('status')}")
                        print(f"   Total Amount: ₹{auto_invoice.get('total_amount', 0):.2f}")
                    else:
                        print("❌ Auto-created invoice not found in billing dashboard")
                else:
                    print(f"❌ Failed to fetch billing invoices: {billing_response.status_code}")
            else:
                print("❌ No invoice was auto-created")
        else:
            print(f"❌ Status update failed: {status_response.status_code}")
            print(f"Response: {status_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Automatic Invoice Creation")
    print("=" * 50)
    test_auto_invoice_creation()
