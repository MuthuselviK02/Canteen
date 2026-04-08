import requests
import json
from datetime import datetime, timedelta

# Test API with date filtering
base_url = "http://localhost:8000"
token = "canteen_token"  # Replace with actual token

def test_date_filtering():
    print("🔍 TESTING DATE FILTERING")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Default (no dates)
    print("\n1. Testing default (no dates):")
    try:
        response = requests.get(f"{base_url}/api/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: KPI data received")
            print(f"   Revenue: {data.get('kpi_metrics', {}).get('current_period', {}).get('revenue', 0)}")
            print(f"   Data points in trends: {len(data.get('revenue_trends', {}).get('daily', {}).get('data', []))}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Custom date range (last 7 days)
    print("\n2. Testing custom date range (last 7 days):")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    try:
        response = requests.get(
            f"{base_url}/api/analytics/dashboard?start_date={start_date}&end_date={end_date}", 
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: KPI data received")
            print(f"   Period: {data.get('kpi_metrics', {}).get('current_period', {}).get('period_start', 'N/A')} to {data.get('kpi_metrics', {}).get('current_period', {}).get('period_end', 'N/A')}")
            print(f"   Revenue: {data.get('kpi_metrics', {}).get('current_period', {}).get('revenue', 0)}")
            print(f"   Data points in trends: {len(data.get('revenue_trends', {}).get('daily', {}).get('data', []))}")
            
            # Show trend data
            trends = data.get('revenue_trends', {}).get('daily', {}).get('data', [])
            print(f"   Trend dates: {[t.get('date', 'N/A') for t in trends[:5]]}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test KPI metrics endpoint directly
    print("\n3. Testing KPI metrics endpoint directly:")
    try:
        response = requests.get(
            f"{base_url}/api/analytics/kpi-metrics?start_date={start_date}&end_date={end_date}", 
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: KPI data received")
            print(f"   Current period revenue: {data.get('current_period', {}).get('revenue', 0)}")
            print(f"   Previous period revenue: {data.get('previous_period', {}).get('revenue', 0)}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_date_filtering()
