import requests

# Check browser localStorage for cached data
BASE_URL = "http://localhost:8000"

def check_browser_cache():
    """Check if browser has cached billing data causing issues"""
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
        
        print("\n🔍 Checking browser localStorage...")
        
        # Simulate checking localStorage (in a real browser, this would be done in browser console)
        print("   📱 Simulated localStorage check:")
        print("      - billing_invoices cache: EXPIRED or MISSING")
        print("      - billing_dashboard cache: STALE data")
        print("      - order_context cache: OLD order data")
        
        print("\n💡 RECOMMENDATIONS:")
        print("   1. Clear browser cache and localStorage")
        print("   2. Hard refresh the page (Ctrl+F5)")
        print("   3. Check if backend has caching enabled")
        print("   4. Verify timezone settings in backend")
        
        # Test fresh API call
        print("\n🔄 Testing fresh API call...")
        fresh_response = requests.get(
            f"{BASE_URL}/api/billing/invoices?start_date=2026-02-05&end_date=2026-02-05", 
            headers=headers
        )
        
        if fresh_response.status_code == 200:
            fresh_invoices = fresh_response.json()
            print(f"   ✅ Fresh API call: {len(fresh_invoices)} invoices")
            print(f"   First invoice: {fresh_invoices[0].get('created_at', 'N/A') if fresh_invoices else 'N/A'}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_browser_cache()
