"""
Test the analytics endpoint by calling it directly without cache
"""
import requests

def test_analytics_no_cache():
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
        
        # Try to call the analytics endpoint with a cache-busting parameter
        print("\n📊 Testing analytics endpoint with cache-busting...")
        
        # Add a timestamp to bypass any caching
        import time
        timestamp = int(time.time())
        
        response = requests.get(f'http://localhost:8000/api/predictive-analytics/dashboard-summary?t={timestamp}', headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Analytics data received')
            
            # Check key metrics
            kpis = data.get('kpis', {})
            print(f'\n📈 Key Performance Indicators:')
            print(f'  Revenue: ₹{kpis.get("revenue", 0)}')
            print(f'  Orders: {kpis.get("orders", 0)}')
            print(f'  Avg Order Value: ₹{kpis.get("avg_order_value", 0)}')
            print(f'  Customers: {kpis.get("customers", 0)}')
            
        else:
            print(f'❌ Analytics endpoint failed: {response.status_code}')
            print(f'Error details: {response.text}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Analytics with Cache Busting")
    print("=" * 50)
    test_analytics_no_cache()
