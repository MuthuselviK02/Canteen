import requests
from datetime import datetime, timezone

# Test backend date handling
BASE_URL = "http://localhost:8000"

def test_backend_date_handling():
    """Test how backend handles date parameters"""
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
        
        # Test with exact same timestamp as frontend sends
        test_date = "2026-02-05"
        test_time = "01:38:42.806048"  # From your actual invoice
        
        print(f"\n🔍 Testing backend date handling for: {test_date}")
        print(f"   Frontend sends: {test_date}")
        print(f"   Expected backend should treat as: {test_date}T00:00:00Z")
        
        # Test invoices endpoint
        invoices_response = requests.get(
            f"{BASE_URL}/api/billing/invoices?start_date={test_date}&end_date={test_date}", 
            headers=headers
        )
        
        if invoices_response.status_code == 200:
            invoices = invoices_response.json()
            print(f"   ✅ Backend response: {invoices_response.status_code}")
            
            # Check what dates backend actually uses
            for inv in invoices[:3]:
                created_at = inv.get('created_at', '')
                print(f"   📋 Invoice {inv.get('invoice_number')}: {created_at}")
                
            # Check backend logs
            print(f"\n🔍 Backend date analysis:")
            print(f"   First invoice date: {invoices[0].get('created_at') if invoices else 'N/A'}")
            print(f"   Date range received: {test_date} to {test_date}")
            
            # Check if backend is adding timezone offset
            first_date = invoices[0].get('created_at', '').split('T')[0]
            if first_date != test_date:
                print(f"   ❌ DATE MISMATCH: Backend received {test_date} but first invoice is {first_date}")
            else:
                print(f"   ✅ Date matches: Backend correctly received {test_date}")
        else:
            print(f"   ❌ Failed to get invoices: {invoices_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend_date_handling()
