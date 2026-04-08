"""
Test KPI API using urllib (built-in)
"""
import urllib.request
import urllib.parse
import json

def test_kpi_api():
    try:
        # Step 1: Login to get token
        login_data = {
            'email': 'superadmin@admin.com',
            'password': 'admin123'
        }
        
        login_url = 'http://localhost:8000/api/auth/login'
        
        # Create POST request for login
        login_req = urllib.request.Request(
            login_url,
            data=json.dumps(login_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(login_req) as response:
            if response.status == 200:
                login_result = json.loads(response.read().decode('utf-8'))
                token = login_result['access_token']
                print(f"✅ Login successful, got token")
                
                # Step 2: Test KPI endpoint
                kpi_url = 'http://localhost:8000/api/admin/kpi/daily'
                kpi_req = urllib.request.Request(
                    kpi_url,
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                with urllib.request.urlopen(kpi_req) as kpi_response:
                    if kpi_response.status == 200:
                        kpi_result = json.loads(kpi_response.read().decode('utf-8'))
                        print("✅ KPI API Response:")
                        print(json.dumps(kpi_result, indent=2))
                        return True
                    else:
                        print(f"❌ KPI API failed with status: {kpi_response.status}")
                        return False
            else:
                print(f"❌ Login failed with status: {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_kpi_api()
    if success:
        print("\n🎉 KPI API test completed successfully!")
    else:
        print("\n💥 KPI API test failed!")
