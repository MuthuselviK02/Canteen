"""
Test formatISTDate function for payment dates
"""
import requests
from datetime import datetime, timedelta

def test_format_ist_date():
    try:
        # Login with user credentials
        login_data = {
            'email': 'sharan@gmail.com',
            'password': 'sharan@1230'
        }
        
        print("🔐 Logging in...")
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            return
        
        token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Get payments for today
        response = requests.get(
            'http://localhost:8002/api/billing/payments?start_date=2026-02-05&end_date=2026-02-05', 
            headers=headers
        )
        
        if response.status_code == 200:
            payments = response.json()
            print(f'✅ Found {len(payments)} payments')
            
            for payment in payments[:3]:  # Show first 3
                created_at = payment.get('created_at', '')
                amount = payment.get('amount', 0)
                
                # Simulate formatISTDate function
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                ist_offset = timedelta(hours=5, minutes=30)
                ist_date = date + ist_offset
                
                # Format like formatISTDate should
                formatted_date = ist_date.strftime('%d/%m/%Y')
                
                print(f"  - ₹{amount}")
                print(f"    UTC: {created_at}")
                print(f"    IST: {ist_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Formatted: {formatted_date}")
                print()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing formatISTDate for Payments")
    print("=" * 40)
    test_format_ist_date()
