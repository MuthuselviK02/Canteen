"""
Debug create invoice dialog issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def debug_create_invoice_issue():
    try:
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
            
            print("🔍 Debugging Create Invoice Issue:")
            
            # Test 1: Check if we can get users for customer ID
            print(f"\n👥 Checking Available Users:")
            users_response = requests.get('http://localhost:8000/api/admin/users', headers=headers)
            
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"  Available users: {len(users)}")
                for user in users[:3]:  # Show first 3
                    print(f"    ID: {user['id']}, Name: {user['fullname']}, Email: {user['email']}")
            else:
                print(f"  Could not fetch users: {users_response.status_code}")
            
            # Test 2: Try creating invoice with minimal valid data
            print(f"\n🧪 Testing Minimal Invoice Creation:")
            
            minimal_invoice = {
                "customer_id": 1,  # Use first user
                "customer_name": "Test User",
                "customer_email": "test@example.com",
                "customer_phone": "+91 9876543210",
                "items": [
                    {
                        "name": "Test Item",
                        "price": 100.00,
                        "quantity": 1,
                        "description": "Test description"
                    }
                ],
                "notes": "Test invoice",
                "payment_method": "cash"
            }
            
            print(f"  Sending invoice data:")
            print(f"    Customer ID: {minimal_invoice['customer_id']}")
            print(f"    Customer Name: {minimal_invoice['customer_name']}")
            print(f"    Items: {len(minimal_invoice['items'])}")
            print(f"    Total: ₹{sum(item['price'] * item['quantity'] for item in minimal_invoice['items'])}")
            
            create_response = requests.post(
                'http://localhost:8000/api/billing/invoices',
                json=minimal_invoice,
                headers=headers
            )
            
            print(f"  Response Status: {create_response.status_code}")
            
            if create_response.status_code == 200:
                invoice = create_response.json()
                print(f"  ✅ Success! Invoice created:")
                print(f"    Invoice Number: {invoice.get('invoice_number', 'N/A')}")
                print(f"    ID: {invoice.get('id', 'N/A')[:8]}...")
                print(f"    Status: {invoice.get('status', 'N/A')}")
                print(f"    Total: ₹{invoice.get('total_amount', 0)}")
            else:
                print(f"  ❌ Failed to create invoice")
                try:
                    error_data = create_response.json()
                    print(f"    Error: {error_data}")
                except:
                    print(f"    Raw Response: {create_response.text}")
            
            # Test 3: Check what happens with invalid data
            print(f"\n🚫 Testing Invalid Data:")
            
            invalid_invoice = {
                "customer_id": "",  # Invalid
                "customer_name": "",  # Invalid
                "items": [],  # Invalid
                "payment_method": "cash"
            }
            
            invalid_response = requests.post(
                'http://localhost:8000/api/billing/invoices',
                json=invalid_invoice,
                headers=headers
            )
            
            print(f"  Invalid Data Response: {invalid_response.status_code}")
            if invalid_response.status_code != 200:
                try:
                    error_data = invalid_response.json()
                    print(f"    Expected Error: {error_data}")
                except:
                    print(f"    Raw Error: {invalid_response.text}")
            
            print(f"\n💡 Troubleshooting Tips:")
            print(f"1. Check browser console for JavaScript errors")
            print(f"2. Verify Customer ID exists in the system")
            print(f"3. Ensure at least one item has a name and price > 0")
            print(f"4. Check network tab in browser dev tools")
            print(f"5. Verify authentication token is valid")
            
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_create_invoice_issue()
