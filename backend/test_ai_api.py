import requests
import json

print('=== Testing AI Recommendation API Endpoints ===')

# Test preference recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/preferences', timeout=10)
    print(f'Preference Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} recommendations')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

# Test time-based recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/time-based', timeout=10)
    print(f'Time-based Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} recommendations')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

# Test all recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/all', timeout=10)
    print(f'All Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} recommendations')
        print(f'   Types: {data["recommendation_types"]}')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

print('\n✅ AI Recommendation API endpoints tested!')
