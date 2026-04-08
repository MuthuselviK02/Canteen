"""
Test the fixed invoice creation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_fixed_invoice():
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
            
            print("🔧 Testing Fixed Invoice Creation:")
            
            # Test the exact payload that frontend would send
            test_cases = [
                {
                    "name": "Valid Customer ID",
                    "customer_id": "1",
                    "customer_name": "Test User",
                    "items": [{"name": "Test Item", "price": 100, "quantity": 1}]
                },
                {
                    "name": "Invalid Customer ID (empty)",
                    "customer_id": "",
                    "customer_name": "Test User",
                    "items": [{"name": "Test Item", "price": 100, "quantity": 1}]
                },
                {
                    "name": "Invalid Customer ID (zero)",
                    "customer_id": "0",
                    "customer_name": "Test User",
                    "items": [{"name": "Test Item", "price": 100, "quantity": 1}]
                },
                {
                    "name": "Invalid Customer ID (text)",
                    "customer_id": "abc",
                    "customer_name": "Test User",
                    "items": [{"name": "Test Item", "price": 100, "quantity": 1}]
                }
            ]
            
            for test_case in test_cases:
                print(f"\n🧪 Testing: {test_case['name']}")
                
                # Simulate frontend payload construction
                customer_id = int(test_case['customer_id']) if test_case['customer_id'].isdigit() else 0
                subtotal = sum(item['price'] * item['quantity'] for item in test_case['items'])
                tax_rate = 18
                tax_amount = subtotal * (tax_rate / 100)
                total_amount = subtotal + tax_amount
                
                invoice_payload = {
                    "customer_id": customer_id,
                    "customer_name": test_case['customer_name'] or '',
                    "customer_email": '',
                    "customer_phone": '',
                    "items": test_case['items'],
                    "subtotal": subtotal,
                    "tax_amount": tax_amount,
                    "total_amount": total_amount,
                    "notes": '',
                    "payment_method": 'cash'
                }
                
                print(f"  Payload customer_id: {invoice_payload['customer_id']}")
                print(f"  Valid customer_id: {invoice_payload['customer_id'] > 0}")
                
                response = requests.post(
                    'http://localhost:8000/api/billing/invoices',
                    json=invoice_payload,
                    headers=headers
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ Success")
                else:
                    print(f"  ❌ Error")
                    try:
                        error_data = response.json()
                        print(f"  Error: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"  Raw: {response.text}")
            
            print(f"\n💡 Expected Behavior:")
            print(f"✅ Valid Customer ID (1): Should create invoice")
            print(f"❌ Invalid IDs: Should show validation error in frontend")
            print(f"🔧 Frontend now validates before sending to backend")
            
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_invoice()
