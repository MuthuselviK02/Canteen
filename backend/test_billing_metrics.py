"""
Test specific billing dashboard metrics endpoints
"""
import requests
from datetime import datetime, timedelta

def test_billing_metrics():
    try:
        # Login with correct credentials
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin@1230'
        }
        
        print("🔐 Logging in...")
        login_response = requests.post('http://localhost:8002/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            return
        
        token = login_response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Login successful")
        
        # Get today's date in IST
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        today_str = ist_now.strftime('%Y-%m-%d')
        
        print(f"\n📅 Testing metrics for today ({today_str})...")
        
        # Test revenue summary for avg order value calculation
        print("\n1. Testing /revenue/summary endpoint...")
        revenue_response = requests.get(
            f'http://localhost:8002/api/billing/revenue/summary?start_date={today_str}&end_date={today_str}',
            headers=headers
        )
        
        if revenue_response.status_code == 200:
            revenue = revenue_response.json()
            summary = revenue.get('summary', {})
            total_revenue = summary.get('total_revenue', 0)
            total_invoices = summary.get('total_invoices', 0)
            paid_invoices = summary.get('paid_invoices', 0)
            
            print(f"   💰 Total Revenue: ₹{total_revenue:.2f}")
            print(f"   📊 Total Invoices: {total_invoices}")
            print(f"   ✅ Paid Invoices: {paid_invoices}")
            
            # Calculate avg order value
            if paid_invoices > 0:
                avg_order_value = total_revenue / paid_invoices
                print(f"   💡 Avg Order Value: ₹{avg_order_value:.2f}")
            else:
                print(f"   💡 Avg Order Value: ₹0.00 (no paid invoices)")
        else:
            print(f"   ❌ Revenue API failed: {revenue_response.status_code}")
        
        # Test performance metrics endpoint
        print("\n2. Testing /performance/metrics endpoint...")
        perf_response = requests.get(
            'http://localhost:8002/api/billing/performance/metrics',
            headers=headers
        )
        
        if perf_response.status_code == 200:
            perf = perf_response.json()
            print(f"   📈 Performance Metrics: {perf}")
        else:
            print(f"   ❌ Performance API failed: {perf_response.status_code}")
            print(f"   Response: {perf_response.text}")
        
        # Test revenue trends endpoint
        print("\n3. Testing /revenue/daily endpoint...")
        daily_response = requests.get(
            f'http://localhost:8002/api/billing/revenue/daily?days=30',
            headers=headers
        )
        
        if daily_response.status_code == 200:
            daily = daily_response.json()
            daily_revenue = daily.get('daily_revenue', [])
            print(f"   📊 Daily Revenue: {len(daily_revenue)} days of data")
            
            # Show last few days
            for day in daily_revenue[-5:]:
                print(f"      {day.get('date', 'N/A')}: ₹{day.get('revenue', 0):.2f} ({day.get('orders', 0)} orders)")
        else:
            print(f"   ❌ Daily Revenue API failed: {daily_response.status_code}")
            print(f"   Response: {daily_response.text}")
        
        # Test month comparison for revenue growth
        print("\n4. Testing month-over-month comparison...")
        
        # This month (Feb 5)
        this_month_start = datetime(2026, 2, 1)  # Feb 1
        this_month_ist = this_month_start - ist_offset  # Convert to UTC
        
        # Last month (Jan 1)
        last_month_start = datetime(2026, 1, 1)  # Jan 1
        last_month_ist = last_month_start - ist_offset  # Convert to UTC
        
        # Test this month
        this_month_response = requests.get(
            f'http://localhost:8002/api/billing/revenue/summary?start_date=2026-02-01&end_date={today_str}',
            headers=headers
        )
        
        # Test last month
        last_month_response = requests.get(
            f'http://localhost:8002/api/billing/revenue/summary?start_date=2026-01-01&end_date=2026-01-31',
            headers=headers
        )
        
        if this_month_response.status_code == 200 and last_month_response.status_code == 200:
            this_month = this_month_response.json().get('summary', {})
            last_month = last_month_response.json().get('summary', {})
            
            this_revenue = this_month.get('total_revenue', 0)
            last_revenue = last_month.get('total_revenue', 0)
            
            print(f"   💰 This Month Revenue: ₹{this_revenue:.2f}")
            print(f"   💰 Last Month Revenue: ₹{last_revenue:.2f}")
            
            if last_revenue > 0:
                growth = ((this_revenue - last_revenue) / last_revenue) * 100
                print(f"   📈 Revenue Growth: {growth:+.1f}%")
            else:
                print(f"   📈 Revenue Growth: +100.0% (first month)")
        else:
            print(f"   ❌ Month comparison failed")
        
        # Test payment rate calculation
        print("\n5. Testing payment rate calculation...")
        if total_invoices > 0:
            payment_rate = (paid_invoices / total_invoices) * 100
            print(f"   💳 Payment Rate: {payment_rate:.1f}%")
            print(f"   📊 {paid_invoices}/{total_invoices} invoices paid")
        else:
            print(f"   💳 Payment Rate: 0.0%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Billing Dashboard Metrics")
    print("=" * 50)
    test_billing_metrics()
