"""
Test billing API with correct credentials
"""
import requests
from datetime import datetime, timedelta

def test_billing_api():
    try:
        # Login with correct credentials
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin@1230'
        }
        
        print("🔐 Logging in with correct credentials...")
        login_response = requests.post('http://localhost:8002/api/auth/login', json=login_data)
        
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
        
        # Get today's date in IST
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        today_str = ist_now.strftime('%Y-%m-%d')
        
        print(f"\n📅 Testing API for today ({today_str})...")
        
        # Test invoices endpoint
        print("\n1. Testing /invoices endpoint...")
        invoices_response = requests.get(
            f'http://localhost:8002/api/billing/invoices?start_date={today_str}&end_date={today_str}',
            headers=headers
        )
        
        if invoices_response.status_code == 200:
            invoices = invoices_response.json()
            print(f"   ✅ Found {len(invoices)} invoices for today")
            
            for inv in invoices:
                inv_num = inv.get('invoice_number', 'N/A')
                inv_status = inv.get('status', 'N/A')
                inv_amount = inv.get('total_amount', 0)
                inv_created = inv.get('created_at', 'N/A')
                print(f"   📋 Invoice {inv_num}: {inv_status} - ₹{inv_amount}")
                print(f"      Created: {inv_created}")
        else:
            print(f"   ❌ Invoices API failed: {invoices_response.status_code}")
            print(f"   Response: {invoices_response.text}")
        
        # Test revenue summary endpoint
        print("\n2. Testing /revenue/summary endpoint...")
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
            pending_invoices = summary.get('pending_invoices', 0)
            
            print(f"   💰 Total Revenue: ₹{total_revenue:.2f}")
            print(f"   📊 Total Invoices: {total_invoices}")
            print(f"   ✅ Paid Invoices: {paid_invoices}")
            print(f"   ⏳ Pending Invoices: {pending_invoices}")
            
            if total_invoices > 0:
                print(f"   🎯 SUCCESS: Found {total_invoices} invoices for today!")
            else:
                print(f"   ⚠️  ISSUE: No invoices found for today")
        else:
            print(f"   ❌ Revenue API failed: {revenue_response.status_code}")
            print(f"   Response: {revenue_response.text}")
        
        # Test last week for comparison
        week_ago = (ist_now - timedelta(days=7)).strftime('%Y-%m-%d')
        print(f"\n3. Testing /invoices endpoint for last week ({week_ago} to {today_str})...")
        
        week_invoices_response = requests.get(
            f'http://localhost:8002/api/billing/invoices?start_date={week_ago}&end_date={today_str}',
            headers=headers
        )
        
        if week_invoices_response.status_code == 200:
            week_invoices = week_invoices_response.json()
            print(f"   ✅ Found {len(week_invoices)} invoices for last week")
            
            if len(week_invoices) > len(invoices):
                print(f"   📈 Last week has more invoices ({len(week_invoices)}) than today ({len(invoices)})")
            elif len(week_invoices) == len(invoices) and len(invoices) > 0:
                print(f"   🤔 Same number of invoices - might all be from today")
            else:
                print(f"   ⚠️  Today has more invoices than last week")
        else:
            print(f"   ❌ Week invoices API failed: {week_invoices_response.status_code}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Today ({today_str}): {len(invoices)} invoices")
        print(f"   Last Week: {len(week_invoices)} invoices")
        
        if len(invoices) == 0 and len(week_invoices) > 0:
            print(f"   🔍 ISSUE: Today shows 0 but last week shows {len(week_invoices)}")
            print(f"   💡 Check if the date filtering is working correctly")
        elif len(invoices) > 0:
            print(f"   ✅ SUCCESS: Today's invoices are showing correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Billing API with Correct Credentials")
    print("=" * 50)
    test_billing_api()
