"""
Test what the frontend billing dashboard receives
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_frontend_data():
    try:
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['access_token']
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("📊 Testing Frontend Data Reception:")
            
            # Test what the frontend fetches
            daily_response = requests.get('http://localhost:8000/api/billing/revenue/daily?days=7', headers=headers)
            
            if daily_response.status_code == 200:
                daily_data = daily_response.json()
                daily_revenue = daily_data.get('daily_revenue', [])
                
                print(f"Raw API Response:")
                print(json.dumps(daily_data, indent=2))
                
                print(f"\n📈 Chart Data Analysis:")
                non_zero_days = [day for day in daily_revenue if day['revenue'] > 0]
                print(f"Days with revenue: {len(non_zero_days)}")
                
                for day in non_zero_days:
                    print(f"  {day['date']}: ₹{day['revenue']}")
                
                if len(non_zero_days) > 0:
                    print(f"\n✅ Chart should display data!")
                    print(f"Expected: Line chart with point at ₹{non_zero_days[0]['revenue']}")
                else:
                    print(f"\n❌ No data to display")
                    
            else:
                print(f"❌ API failed: {daily_response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_data()
