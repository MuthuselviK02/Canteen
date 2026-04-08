import requests
import json

# Test the analytics API endpoint
try:
    response = requests.get('http://localhost:8000/api/analytics/dashboard', 
                          headers={'Authorization': 'Bearer test_token'})
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print('✅ API endpoint is working')
        print(f'KPI Metrics: {"kpi_metrics" in data}')
        print(f'Revenue by Time Slot: {"revenue_by_time_slot" in data}')
        print(f'Item Performance: {"item_performance" in data}')
        print(f'Revenue Trends: {"revenue_trends" in data}')
        
        # Check if data has actual values
        if 'kpi_metrics' in data:
            today_revenue = data['kpi_metrics'].get('today', {}).get('revenue', 0)
            print(f'Today Revenue: {today_revenue}')
    else:
        print(f'❌ API Error: {response.text}')
except Exception as e:
    print(f'❌ Connection Error: {e}')
    print('Backend server may not be running')
