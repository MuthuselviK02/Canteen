import requests

# Test the exact call the analytics dashboard is making
login_data = {'email': 'sharan@gmail.com', 'password': 'sharan@1230'}

print('Testing the exact API call the analytics dashboard is making:')

try:
    # Login first
    response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test the exact call from PredictiveAIDashboardNew.tsx
    print('\n1. Testing billing call to port 8002 (as coded in the fix):')
    billing_response = requests.get('http://localhost:8002/api/billing/revenue/summary?start_date=2026-02-05&end_date=2026-02-05', headers=headers)
    print(f'   Status: {billing_response.status_code}')
    if billing_response.status_code == 200:
        data = billing_response.json()
        print(f'   Revenue: ₹{data.get("summary", {}).get("total_revenue", 0)}')
        print(f'   Orders: {data.get("summary", {}).get("total_orders", 0)}')
        print(f'   ✅ This should work!')
    else:
        print(f'   Error: {billing_response.text}')
    
    # Test what the frontend would receive
    print('\n2. Testing what the analytics dashboard would convert to:')
    if billing_response.status_code == 200:
        billing_data = billing_response.json()
        
        # Simulate the conversion
        result = {
            "overview": {
                "total_revenue": billing_data.summary?.total_revenue || 0,
                "total_orders": billing_data.summary?.total_orders || 0,
                "avg_order_value": billing_data.summary?.total_orders > 0 ? 
                    billing_data.summary.total_revenue / billing_data.summary.total_orders : 0,
                "growth_rate": billing_data.summary?.growth_rate || 0,
                "payment_rate": billing_data.summary?.paid_invoices > 0 ? 
                    (billing_data.summary.paid_invoices / billing_data.summary.total_invoices) * 100 : 0
            }
        }
        
        print(f'   Converted Revenue: ₹{result["overview"]["total_revenue"]}')
        print(f'   Converted Orders: {result["overview"]["total_orders"]}')
        print(f'   Converted Growth: {result["overview"]["growth_rate"]}%')
        print(f'   ✅ This is what the dashboard should show!')
        
except Exception as e:
    print(f'Error: {e}')
