"""
Test invoice creation with user credentials
"""
import requests
from datetime import datetime, timedelta

def test_invoice_creation():
    try:
        # Login with user credentials
        login_data = {
            'email': 'sharan@gmail.com',
            'password': 'sharan@1230'
        }
        
        print("🔐 Logging in with user credentials...")
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            print(f'Response: {login_response.text}')
            return
        
        token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Login successful")
        
        # Test creating an invoice
        print("\n🧾 Testing invoice creation...")
        
        invoice_data = {
            "customer_id": 2,  # User ID from console logs
            "items": [
                {
                    "name": "Test Item",
                    "price": 100.0,
                    "quantity": 1,
                    "description": "Test invoice item"
                }
            ],
            "notes": "Test invoice from order",
            "payment_method": "cash"
        }
        
        response = requests.post('http://localhost:8002/api/billing/invoices', json=invoice_data, headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            invoice = response.json()
            print(f'✅ Invoice created successfully: {invoice.get("invoice_number")}')
        else:
            print(f'❌ Invoice creation failed: {response.status_code}')
            print(f'Error details: {response.text}')
            
            # Try to get more detailed error info
            try:
                error_data = response.json()
                print(f'Error details: {error_data}')
            except:
                print('Could not parse error response')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Invoice Creation")
    print("=" * 40)
    test_invoice_creation()
