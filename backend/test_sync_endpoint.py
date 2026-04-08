#!/usr/bin/env python3
"""
Quick test for the inventory sync endpoint
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_sync_endpoint():
    """Test the inventory sync endpoint"""
    print("🧪 Testing Inventory Sync Endpoint")
    print("=" * 40)
    
    # Step 1: Login as superadmin
    print("\n🔐 Logging in as superadmin...")
    response = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "superadmin@admin.com",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print("✅ Login successful")
    
    # Step 2: Test sync endpoint
    print("\n🔄 Testing sync endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_URL}/api/inventory/sync-inventory", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Sync endpoint working!")
        return True
    else:
        print(f"❌ Sync endpoint failed: {response.status_code}")
        return False

if __name__ == "__main__":
    test_sync_endpoint()
