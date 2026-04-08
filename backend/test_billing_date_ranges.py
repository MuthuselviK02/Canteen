"""
Test billing endpoint with different date ranges for analytics dashboard
"""
import requests
from datetime import datetime, timedelta

def test_billing_date_ranges():
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
        
        print("✅ Login successful")
        
        # Test different date ranges
        date_ranges = [
            ("Today", "2026-02-05", "2026-02-05"),
            ("Last 7 Days", "2026-01-30", "2026-02-05"),
            ("Last 30 Days", "2026-01-06", "2026-02-05")
        ]
        
        for range_name, start_date, end_date in date_ranges:
            print(f"\n📊 Testing {range_name} ({start_date} to {end_date})...")
            
            response = requests.get(
                f'http://localhost:8002/api/billing/revenue/summary?start_date={start_date}&end_date={end_date}',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                
                print(f'  ✅ Revenue: ₹{summary.get("total_revenue", 0)}')
                print(f'  ✅ Orders: {summary.get("total_orders", 0)}')
                print(f'  ✅ Avg Order Value: ₹{summary.get("total_orders", 0) and summary.get("total_revenue", 0) / summary.get("total_orders", 1) or 0:.2f}')
                print(f'  ✅ Growth Rate: {summary.get("growth_rate", 0)}%')
            else:
                print(f'  ❌ Failed: {response.status_code} - {response.text}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Billing Date Ranges for Analytics")
    print("=" * 50)
    test_billing_date_ranges()
