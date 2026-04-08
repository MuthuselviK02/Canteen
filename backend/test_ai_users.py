#!/usr/bin/env python3
"""
Test AI recommendations for different users
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_ai_recommendations():
    """Test AI recommendations for both users"""
    
    print("🧪 Testing AI Recommendations for Different Users")
    print("=" * 60)
    
    # Test users
    users = [
        {"email": "sharan@gmail.com", "password": "sharan@1230", "name": "Sharan"},
        {"email": "saran@gmail.com", "password": "saran@1230", "name": "Saran"}
    ]
    
    for user in users:
        print(f"\n👤 Testing User: {user['name']} ({user['email']})")
        print("-" * 40)
        
        # Login
        try:
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": user['email'],
                "password": user['password']
            })
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                continue
                
            token = login_response.json()['access_token']
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print(f"✅ Login successful")
            
            # Test AI recommendations
            try:
                ai_response = requests.get(f"{BASE_URL}/api/ai/recommendations/all", headers=headers)
                
                if ai_response.status_code == 200:
                    ai_data = ai_response.json()
                    recommendations = ai_data.get('recommendations', [])
                    
                    print(f"✅ AI Recommendations: {len(recommendations)} items")
                    
                    if recommendations:
                        print("📋 Sample recommendations:")
                        for i, rec in enumerate(recommendations[:3]):
                            print(f"  {i+1}. {rec['name']} - ₹{rec['price']} ({rec['recommendation_type']})")
                            print(f"     Confidence: {rec['confidence']:.2f}")
                            print(f"     Reasoning: {rec['reasoning']}")
                    else:
                        print("⚠️ No recommendations returned")
                        
                else:
                    print(f"❌ AI Recommendations failed: {ai_response.status_code}")
                    if ai_response.status_code == 500:
                        print(f"Error: {ai_response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing AI recommendations: {e}")
            
            # Test user preferences
            try:
                prefs_response = requests.get(f"{BASE_URL}/api/ai/preferences", headers=headers)
                
                if prefs_response.status_code == 200:
                    prefs_data = prefs_response.json()
                    print(f"✅ User Preferences: {len(prefs_data)} preferences")
                    
                    if prefs_data:
                        print("📊 Preferences:")
                        for pref in prefs_data[:3]:
                            print(f"  - {pref['preference_type']}: {pref['preference_value']} (weight: {pref['weight']})")
                    else:
                        print("⚠️ No preferences found")
                else:
                    print(f"❌ User Preferences failed: {prefs_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing user preferences: {e}")
                
        except Exception as e:
            print(f"❌ Login error: {e}")

def test_order_history():
    """Test order history for both users"""
    
    print(f"\n📦 Testing Order History")
    print("=" * 60)
    
    users = [
        {"email": "sharan@gmail.com", "password": "sharan@1230", "name": "Sharan"},
        {"email": "saran@gmail.com", "password": "saran@1230", "name": "Saran"}
    ]
    
    for user in users:
        print(f"\n👤 Order History for: {user['name']}")
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
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get orders
            orders_response = requests.get(f"{BASE_URL}/api/orders/", headers=headers)
            
            if orders_response.status_code == 200:
                orders = orders_response.json()
                print(f"✅ Found {len(orders)} orders")
                
                if orders:
                    total_spent = sum(order.get('total', 0) for order in orders)
                    print(f"💰 Total spent: ₹{total_spent}")
                    print(f"📅 Recent orders:")
                    for order in orders[:3]:
                        print(f"  - Order #{order.get('id')} on {order.get('created_at', 'Unknown date')}")
                else:
                    print("⚠️ No order history found")
            else:
                print(f"❌ Orders failed: {orders_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_recommendations()
    test_order_history()
    
    print(f"\n🎯 Analysis:")
    print("If Sharan has recommendations but Saran doesn't, the issue is likely:")
    print("1. Saran has no order history/preferences")
    print("2. Fallback recommendations aren't working properly")
    print("3. There's an error in the AI service for new users")
