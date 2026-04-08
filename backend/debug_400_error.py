"""
Debug the 400 Bad Request error in invoice creation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def debug_400_error():
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
            
            print("🔍 Debugging 400 Bad Request Error:")
            
            # Test different scenarios that might cause 400 errors
            test_cases = [
                {
                    "name": "Valid Invoice",
                    "data": {
                        "customer_id": 1,
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
                },
                {
                    "name": "Missing Customer Email",
                    "data": {
                        "customer_id": 1,
                        "customer_name": "Test User",
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
                },
                {
                    "name": "Empty Customer Name",
                    "data": {
                        "customer_id": 1,
                        "customer_name": "",
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
                },
                {
                    "name": "Zero Price Item",
                    "data": {
                        "customer_id": 1,
                        "customer_name": "Test User",
                        "customer_email": "test@example.com",
                        "customer_phone": "+91 9876543210",
                        "items": [
                            {
                                "name": "Test Item",
                                "price": 0.00,
                                "quantity": 1,
                                "description": "Test description"
                            }
                        ],
                        "notes": "Test invoice",
                        "payment_method": "cash"
                    }
                },
                {
                    "name": "Empty Item Name",
                    "data": {
                        "customer_id": 1,
                        "customer_name": "Test User",
                        "customer_email": "test@example.com",
                        "customer_phone": "+91 9876543210",
                        "items": [
                            {
                                "name": "",
                                "price": 100.00,
                                "quantity": 1,
                                "description": "Test description"
                            }
                        ],
                        "notes": "Test invoice",
                        "payment_method": "cash"
                    }
                }
            ]
            
            for test_case in test_cases:
                print(f"\n🧪 Testing: {test_case['name']}")
                print(f"  Data: {json.dumps(test_case['data'], indent=2)}")
                
                response = requests.post(
                    'http://localhost:8000/api/billing/invoices',
                    json=test_case['data'],
                    headers=headers
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ Success")
                else:
                    print(f"  ❌ Error")
                    try:
                        error_data = response.json()
                        print(f"  Error Details: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"  Raw Response: {response.text}")
            
            # Check the backend schema requirements
            print(f"\n📋 Checking Backend Schema:")
            
            # Get the billing router schema
            schema_response = requests.get('http://localhost:8000/api/billing/invoices', headers=headers)
            print(f"  Get Invoices Status: {schema_response.status_code}")
            
            # Test with minimal required fields based on typical invoice schema
            print(f"\n🔧 Testing Minimal Required Fields:")
            
            minimal_data = {
                "customer_id": 1,
                "items": [
                    {
                        "name": "Test",
                        "price": 100,
                        "quantity": 1
                    }
                ]
            }
            
            minimal_response = requests.post(
                'http://localhost:8000/api/billing/invoices',
                json=minimal_data,
                headers=headers
            )
            
            print(f"  Minimal Data Status: {minimal_response.status_code}")
            if minimal_response.status_code != 200:
                try:
                    error_data = minimal_response.json()
                    print(f"  Minimal Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"  Minimal Raw: {minimal_response.text}")
            
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_400_error()
