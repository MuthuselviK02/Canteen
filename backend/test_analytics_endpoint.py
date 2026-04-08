"""
Test analytics dashboard endpoint
"""
import requests
from datetime import datetime, timedelta

def test_analytics_endpoint():
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
        
        # Test analytics dashboard endpoint
        print("\n📊 Testing analytics dashboard endpoint...")
        response = requests.get('http://localhost:8000/api/predictive-analytics/dashboard-summary', headers=headers)
        
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
            
            # Check trends
            trends = data.get('trends', {})
            print(f'\n📊 Trends:')
            print(f'  Revenue Growth: {trends.get("revenue_growth", 0)}%')
            print(f'  Order Growth: {trends.get("order_growth", 0)}%')
            
            # Check time slot data
            time_slots = data.get('time_slot_analysis', {})
            print(f'\n⏰ Time Slot Analysis:')
            print(f'  Total Revenue: ₹{time_slots.get("total_revenue", 0)}')
            print(f'  Total Orders: {time_slots.get("total_orders", 0)}')
            
            slots = time_slots.get('slots', {})
            for slot_name, slot_data in slots.items():
                revenue = slot_data.get('revenue', 0)
                orders = slot_data.get('orders', 0)
                print(f'    {slot_name}: ₹{revenue} ({orders} orders)')
            
        else:
            print(f'❌ Analytics endpoint failed: {response.status_code}')
            print(f'Error details: {response.text}')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("🧪 Testing Analytics Dashboard Endpoint")
    print("=" * 50)
    test_analytics_endpoint()
