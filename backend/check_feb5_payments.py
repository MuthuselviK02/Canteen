"""
Check what payments should show for Feb 5 IST
"""
import requests
from datetime import datetime, timedelta

def check_feb5_payments():
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
        
        # Define Feb 5 IST boundaries
        # Feb 5 IST = Feb 4 18:30 UTC to Feb 5 18:30 UTC
        feb5_ist_start_utc = datetime(2026, 2, 4, 18, 30, 0)  # Feb 5 00:00 IST = Feb 4 18:30 UTC
        feb5_ist_end_utc = datetime(2026, 2, 5, 18, 29, 59)   # Feb 5 23:59 IST = Feb 5 18:29 UTC
        
        print(f"📅 Feb 5 IST boundaries:")
        print(f"  Start: {feb5_ist_start_utc} UTC")
        print(f"  End: {feb5_ist_end_utc} UTC")
        
        # Check what payments exist in this range
        print(f"\n💳 Checking payments for Feb 5 IST range...")
        
        # Test with the exact date range the frontend uses
        today_str = "2026-02-05"
        response = requests.get(
            f'http://localhost:8002/api/billing/payments?start_date={today_str}&end_date={today_str}', 
            headers=headers
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            payments = response.json()
            print(f'✅ Found {len(payments)} payments')
            
            for payment in payments:
                created_at = payment.get('created_at', '')
                amount = payment.get('amount', 0)
                status = payment.get('status', '')
                
                # Convert to IST
                if created_at:
                    utc_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    ist_offset = timedelta(hours=5, minutes=30)
                    ist_time = utc_time + ist_offset
                    
                    print(f"  - ₹{amount} ({status})")
                    print(f"    UTC: {created_at}")
                    print(f"    IST: {ist_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Check if this is actually Feb 5 IST
                    ist_date = ist_time.strftime('%Y-%m-%d')
                    if ist_date == '2026-02-05':
                        print(f"    ✅ This IS Feb 5 IST")
                    else:
                        print(f"    ❌ This is NOT Feb 5 IST (it's {ist_date})")
                    print()
        else:
            print(f'❌ Failed: {response.text}')
        
        # Also check if there are any actual Feb 5 payments
        print(f"🔍 Let's check if there are any payments made on Feb 5 UTC...")
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Checking Feb 5 Payments in Detail")
    print("=" * 50)
    check_feb5_payments()
