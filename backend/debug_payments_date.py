"""
Debug payments date filtering for today
"""
import requests
from datetime import datetime, timedelta

def debug_payments_today():
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
        
        # Get today's date range
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        today_str = ist_now.strftime('%Y-%m-%d')
        
        print(f"📅 Today (IST): {today_str}")
        print(f"📅 UTC now: {now}")
        print(f"📅 IST now: {ist_now}")
        
        # Test payments for today
        print(f"\n💳 Testing payments for today ({today_str})...")
        response = requests.get(
            f'http://localhost:8002/api/billing/payments?start_date={today_str}&end_date={today_str}', 
            headers=headers
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            payments = response.json()
            print(f'✅ Found {len(payments)} payments for today')
            
            for payment in payments:
                created_at = payment.get('created_at', 'Unknown')
                amount = payment.get('amount', 0)
                status = payment.get('status', 'Unknown')
                print(f"  - ₹{amount} ({status}) - {created_at}")
        else:
            print(f'❌ Failed: {response.text}')
        
        # Also check what payments actually exist
        print(f"\n💳 Checking all payments without date filter...")
        response = requests.get('http://localhost:8002/api/billing/payments', headers=headers)
        
        if response.status_code == 200:
            payments = response.json()
            print(f'✅ Total payments: {len(payments)}')
            
            # Group payments by date
            from collections import defaultdict
            payments_by_date = defaultdict(list)
            
            for payment in payments:
                created_at = payment.get('created_at', '')
                if created_at:
                    # Extract date part
                    date_part = created_at.split('T')[0]
                    payments_by_date[date_part].append(payment)
            
            print(f"\n📊 Payments by date:")
            for date, date_payments in sorted(payments_by_date.items()):
                print(f"  {date}: {len(date_payments)} payments")
                for payment in date_payments[:3]:  # Show first 3
                    amount = payment.get('amount', 0)
                    print(f"    - ₹{amount}")
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Debugging Payments Date Filtering")
    print("=" * 50)
    debug_payments_today()
