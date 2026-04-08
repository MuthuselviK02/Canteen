import requests

# Count orders with Feb 5 in last week filter
BASE_URL = "http://localhost:8000"

def count_feb5_orders():
    """Count orders with Feb 5 date in last week range"""
    login_data = {
        "email": "sharan@gmail.com",
        "password": "sharan@1230"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print("❌ Login failed")
            return
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("❌ No token received")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get last week range (Jan 29 - Feb 5)
        start_date = "2026-01-29"
        end_date = "2026-02-05"
        
        print(f"\n🔍 Checking for Feb 5 orders in last week filter...")
        print(f"   Date range: {start_date} to {end_date}")
        
        # Get invoices
        invoices_response = requests.get(
            f"{BASE_URL}/api/billing/invoices?start_date={start_date}&end_date={end_date}", 
            headers=headers
        )
        
        if invoices_response.status_code == 200:
            invoices = invoices_response.json()
            print(f"📋 Total invoices found: {len(invoices)}")
            
            # Count orders with Feb 5 date
            feb5_count = 0
            for inv in invoices:
                created_at = inv.get('created_at', '')
                if '2026-02-05' in created_at:
                    feb5_count += 1
                    print(f"   ✅ Found Feb 5 invoice: {inv.get('invoice_number', 'N/A')}")
            
            print(f"\n📊 RESULTS:")
            print(f"   Total invoices in last week: {len(invoices)}")
            print(f"   Orders with Feb 5 date: {feb5_count}")
            print(f"   Orders with other dates: {len(invoices) - feb5_count}")
            
            if feb5_count > 0:
                print(f"\n✅ CONFIRMED: {feb5_count} orders with Feb 5 found in last week filter")
            else:
                print(f"\n❌ ISSUE: No orders with Feb 5 found in last week filter")
        else:
            print(f"❌ Failed to get invoices: {invoices_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    count_feb5_orders()
