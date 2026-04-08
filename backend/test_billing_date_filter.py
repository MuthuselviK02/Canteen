"""
Test billing dashboard date filtering
"""
import requests
import json
from datetime import datetime, timedelta

def test_billing_date_filtering():
    try:
        # Login as admin
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        print("1. 🔐 Logging in as admin...")
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
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
        
        print(f"\n2. 📅 Testing date filtering for today ({today_str})...")
        
        # Test invoices endpoint with today's date
        print("\n   Testing /invoices endpoint...")
        invoices_response = requests.get(
            f'http://localhost:8002/api/billing/invoices?start_date={today_str}&end_date={today_str}',
            headers=headers
        )
        
        if invoices_response.status_code == 200:
            invoices = invoices_response.json()
            print(f"   ✅ Found {len(invoices)} invoices for today")
            
            if invoices:
                print(f"   📋 Sample invoice: {invoices[0].get('invoice_number', 'N/A')} - {invoices[0].get('status', 'N/A')}")
            else:
                print("   ⚠️  No invoices found for today")
        else:
            print(f"   ❌ Failed: {invoices_response.status_code}")
        
        # Test revenue summary endpoint with today's date
        print("\n   Testing /revenue/summary endpoint...")
        revenue_response = requests.get(
            f'http://localhost:8002/api/billing/revenue/summary?start_date={today_str}&end_date={today_str}',
            headers=headers
        )
        
        if revenue_response.status_code == 200:
            revenue = revenue_response.json()
            print(f"   ✅ Revenue summary: ₹{revenue.get('summary', {}).get('total_revenue', 0):.2f}")
            print(f"   📊 Total invoices: {revenue.get('summary', {}).get('total_invoices', 0)}")
        else:
            print(f"   ❌ Failed: {revenue_response.status_code}")
        
        # Test with last week
        week_ago = (ist_now - timedelta(days=7)).strftime('%Y-%m-%d')
        print(f"\n3. 📅 Testing date filtering for last week ({week_ago} to {today_str})...")
        
        week_invoices_response = requests.get(
            f'http://localhost:8002/api/billing/invoices?start_date={week_ago}&end_date={today_str}',
            headers=headers
        )
        
        if week_invoices_response.status_code == 200:
            week_invoices = week_invoices_response.json()
            print(f"   ✅ Found {len(week_invoices)} invoices for last week")
            
            if len(week_invoices) > len(invoices):
                print("   ✅ Last week shows more invoices than today (expected)")
            elif len(week_invoices) == len(invoices) and len(invoices) > 0:
                print("   ⚠️  Same number of invoices - might be all from today")
        else:
            print(f"   ❌ Failed: {week_invoices_response.status_code}")
        
        print("\n4. 🎯 Summary:")
        print(f"   Today ({today_str}): {len(invoices)} invoices")
        print(f"   Last week: {len(week_invoices)} invoices")
        
        if len(invoices) == 0 and len(week_invoices) > 0:
            print("   ⚠️  Issue: Today shows 0 invoices but last week shows data")
            print("   💡 This suggests invoices exist but aren't being filtered correctly for today")
        elif len(invoices) > 0:
            print("   ✅ Today's invoices are showing correctly")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Billing Dashboard Date Filtering")
    print("=" * 50)
    test_billing_date_filtering()
