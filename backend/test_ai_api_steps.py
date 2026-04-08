import requests
import json

print('=== Testing AI Recommendation API - Steps 3 & 4 ===')

# Test combo recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/combo', timeout=10)
    print(f'Combo Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} combo recommendations')
        for rec in data["recommendations"][:2]:
            print(f'   - {rec["name"]}: {rec["category"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

# Test dietary recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/dietary', timeout=10)
    print(f'Dietary Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} dietary recommendations')
        for rec in data["recommendations"][:2]:
            print(f'   - {rec["name"]}: {rec["category"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

# Test all recommendations (now includes combo and dietary)
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/all', timeout=10)
    print(f'All Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} recommendations')
        print(f'   Types: {data["recommendation_types"]}')
        for rec in data["recommendations"][:3]:
            print(f'   - {rec["name"]}: {rec["recommendation_type"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

print('\n✅ AI Recommendation API endpoints tested!')
