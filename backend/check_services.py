import requests

# Check what's running on each port
login_data = {'email': 'sharan@gmail.com', 'password': 'sharan@1230'}

ports_info = {
    8000: "Main Backend",
    8001: "Unknown Service", 
    8002: "Billing Service"
}

for port, service_name in ports_info.items():
    print(f'\n=== Port {port} ({service_name}) ===')
    
    try:
        # Login
        response = requests.post(f'http://localhost:{port}/api/auth/login', json=login_data)
        if response.status_code == 200:
            token = response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Test billing endpoint
            print(f'  Testing billing endpoint:')
            billing_response = requests.get(f'http://localhost:{port}/api/billing/revenue/summary?start_date=2026-02-05&end_date=2026-02-05', headers=headers)
            print(f'    Billing: {billing_response.status_code}')
            if billing_response.status_code == 200:
                data = billing_response.json()
                print(f'    Revenue: ₹{data.get("summary", {}).get("total_revenue", 0)}')
            else:
                print(f'    Error: {billing_response.text[:100]}')
            
            # Test analytics endpoint
            print(f'  Testing analytics endpoint:')
            analytics_response = requests.get(f'http://localhost:{port}/api/predictive-analytics/dashboard-summary', headers=headers)
            print(f'    Analytics: {analytics_response.status_code}')
            if analytics_response.status_code == 200:
                data = analytics_response.json()
                print(f'    KPIs: {len(data.get("kpis", {}))} metrics')
            else:
                print(f'    Error: {analytics_response.text[:100]}')
                
        else:
            print(f'  Login failed: {response.status_code}')
            
    except Exception as e:
        print(f'  Error: {str(e)[:100]}')
