import requests

# Login first
login_data = {'email': 'superadmin@admin.com', 'password': 'admin123'}
login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
if login_response.ok:
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test billing endpoint
    response = requests.get('http://localhost:8000/api/billing/invoices', headers=headers)
    print(f'Status: {response.status_code}')
    if response.ok:
        invoices = response.json()
        print(f'Success: {len(invoices)} invoices found')
        if invoices:
            print(f'First invoice: {invoices[0].get("invoice_number", "N/A")}')
    else:
        print('Error:', response.text)
else:
    print('Login failed:', login_response.status_code)
