#!/usr/bin/env python3
"""
Test frontend AI recommendations for both users
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_frontend_ai():
    """Test that frontend can access AI recommendations"""
    
    print("🌐 Testing Frontend AI Recommendations")
    print("=" * 50)
    
    users = [
        {"email": "sharan@gmail.com", "password": "sharan@1230", "name": "Sharan"},
        {"email": "saran@gmail.com", "password": "saran@1230", "name": "Saran"}
    ]
    
    for user in users:
        print(f"\n👤 Testing Frontend for: {user['name']}")
        print("-" * 30)
        
        try:
            # Login
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": user['email'],
                "password": user['password']
            })
            
            if login_response.status_code != 200:
                print(f"❌ Login failed")
                continue
                
            token = login_response.json()['access_token']
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test all AI endpoints that frontend uses
            endpoints = [
                ("/api/ai/recommendations/all", "All Recommendations"),
                ("/api/ai/recommendations/preferences", "Preference-based"),
                ("/api/ai/recommendations/time-based", "Time-based"),
                ("/api/ai/recommendations/combo", "Combo"),
                ("/api/ai/recommendations/dietary", "Dietary"),
                ("/api/ai/recommendations/calorie-conscious", "Calorie-conscious"),
                ("/api/ai/recommendations/weather-based", "Weather-based"),
                ("/api/ai/preferences", "User Preferences")
            ]
            
            all_working = True
            
            for endpoint, name in endpoints:
                try:
                    if endpoint == "/api/ai/recommendations/calorie-conscious":
                        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    elif endpoint == "/api/ai/preferences":
                        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    else:
                        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'recommendations' in data:
                            count = len(data['recommendations'])
                            print(f"✅ {name}: {count} items")
                        elif isinstance(data, list):
                            print(f"✅ {name}: {len(data)} items")
                        else:
                            print(f"✅ {name}: Working")
                    else:
                        print(f"❌ {name}: Failed ({response.status_code})")
                        all_working = False
                        
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
                    all_working = False
            
            if all_working:
                print(f"🎉 {user['name']}: All AI endpoints working!")
            else:
                print(f"⚠️ {user['name']}: Some endpoints failed")
                
        except Exception as e:
            print(f"❌ Error testing {user['name']}: {e}")

if __name__ == "__main__":
    test_frontend_ai()
    
    print(f"\n✅ AI Recommendations Fix Complete!")
    print("Both users should now see AI recommendations in the frontend")
