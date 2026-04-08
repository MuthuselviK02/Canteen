"""
Test payments endpoint with user credentials
"""
import requests
from datetime import datetime, timedelta

def test_payments_endpoint():
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
        
        # Test payments endpoint for today
        print("\n💳 Testing payments endpoint...")
        
        # Get today's date range
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        today_str = ist_now.strftime('%Y-%m-%d')
        
        response = requests.get(
            f'http://localhost:8002/api/billing/payments?start_date={today_str}&end_date={today_str}', 
            headers=headers
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            payments = response.json()
            print(f'✅ Payments data received: {len(payments)} payments')
            
            for payment in payments[:5]:  # Show first 5 payments
                print(f"  - {payment.get('invoice_number')}: ₹{payment.get('amount', 0):.2f} ({payment.get('status')})")
        else:
            print(f'❌ Payments endpoint failed: {response.status_code}')
            print(f'Error details: {response.text}')
        
        # Also test without date filters
        print("\n💳 Testing payments endpoint without date filters...")
        response = requests.get('http://localhost:8002/api/billing/payments', headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            payments = response.json()
            print(f'✅ All payments: {len(payments)} payments')
            
            for payment in payments[:5]:  # Show first 5 payments
                print(f"  - {payment.get('invoice_number')}: ₹{payment.get('amount', 0):.2f} ({payment.get('status')})")
        else:
            print(f'❌ All payments endpoint failed: {response.status_code}')
            print(f'Error details: {response.text}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Payments Endpoint")
    print("=" * 40)
    test_payments_endpoint()
