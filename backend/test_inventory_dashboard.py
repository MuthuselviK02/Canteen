#!/usr/bin/env python3
"""
Test the inventory dashboard endpoint directly
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_inventory_dashboard():
    """Test the inventory dashboard endpoint"""
    print("🧪 Testing Inventory Dashboard Endpoint")
    print("=" * 50)
    
    # Login as superadmin
    print("🔐 Logging in as superadmin...")
    response = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "superadmin@admin.com",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print("✅ Login successful")
    
    # Test the exact URL the frontend is calling
    print("\n📦 Testing inventory dashboard...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use the exact parameters from the frontend
    start_date = "2026-02-06T18:30:00.000Z"
    end_date = "2026-02-07T18:30:00.000Z"
    category = "all"
    
    url = f"{API_URL}/api/inventory/dashboard?start_date={start_date}&end_date={end_date}&category={category}"
    print(f"URL: {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Inventory dashboard working!")
        print(f"Total items: {data['inventory_kpis']['total_items']}")
        print(f"Well stocked: {data['inventory_kpis']['well_stocked']}")
        print(f"No forecast: {data['inventory_kpis']['no_forecast']}")
        return True
    else:
        print(f"❌ Inventory dashboard failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    test_inventory_dashboard()
