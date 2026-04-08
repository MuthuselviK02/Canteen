"""
Test to check if the frontend dateRange state is working
"""
import requests
from datetime import datetime, timedelta

# Test if the frontend is actually calling the right API
try:
    login_data = {'email': 'superadmin@admin.com', 'password': 'admin@1230'}
    login_response = requests.post('http://localhost:8002/api/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        print('Testing different dateRange API calls:')
        
        # Test today (days=1)
        response = requests.get('http://localhost:8002/api/billing/revenue/daily?days=1', headers=headers)
        if response.status_code == 200:
            data = response.json()
            daily_revenue = data.get('daily_revenue', [])
            print(f'  Today (days=1): {len(daily_revenue)} days')
            for day in daily_revenue:
                print(f'    {day.get("date")}: ₹{day.get("revenue", 0):.2f}')
        
        # Test week (days=7)
        response = requests.get('http://localhost:8002/api/billing/revenue/daily?days=7', headers=headers)
        if response.status_code == 200:
            data = response.json()
            daily_revenue = data.get('daily_revenue', [])
            print(f'  Week (days=7): {len(daily_revenue)} days')
            for day in daily_revenue[-3:]:  # Show last 3 days
                print(f'    {day.get("date")}: ₹{day.get("revenue", 0):.2f}')
        
        print('\nExpected behavior:')
        print('- When "Today" is selected: Should show 1 day (Feb 5)')
        print('- When "Last 7 Days" is selected: Should show 7 days')
        print('- Check browser console for debug messages')
        
    else:
        print('Login failed')
        
except Exception as e:
    print(f'Error: {e}')
