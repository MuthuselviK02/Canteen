import requests
import socket

# Check which ports are actually running
ports_to_check = [8000, 8001, 8002]

print('Checking which backend ports are running:')
for port in ports_to_check:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f'  Port {port}: OPEN')
        else:
            print(f'  Port {port}: CLOSED')
    except:
        print(f'  Port {port}: ERROR')

# Test each port with a simple request
print('\nTesting each port:')
login_data = {'email': 'sharan@gmail.com', 'password': 'sharan@1230'}

for port in ports_to_check:
    try:
        print(f'\nTesting port {port}:')
        response = requests.post(f'http://localhost:{port}/api/auth/login', json=login_data, timeout=2)
        print(f'  Status: {response.status_code}')
        if response.status_code == 200:
            print(f'  ✅ Port {port} is working - got login token')
        else:
            print(f'  Response: {response.text[:100]}')
    except requests.exceptions.ConnectTimeout:
        print(f'  ❌ Port {port} - Connection timeout')
    except requests.exceptions.ConnectionError:
        print(f'  ❌ Port {port} - Connection refused')
    except Exception as e:
        print(f'  ❌ Port {port} - Error: {str(e)[:50]}')
