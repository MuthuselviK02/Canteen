import requests
import json

print('=== Testing AI Recommendation API - Step 6: Weather-Based ===')

# Test weather-based recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/weather-based', timeout=10)
    print(f'Weather-Based Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} weather-based recommendations')
        for rec in data["recommendations"][:2]:
            print(f'   - {rec["name"]}: {rec["category"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

# Test all recommendations (now includes weather-based)
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/all', timeout=10)
    print(f'All Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} recommendations')
        print(f'   Types: {data["recommendation_types"]}')
        for rec in data["recommendations"][:6]:
            print(f'   - {rec["name"]}: {rec["recommendation_type"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

print('\n✅ AI Recommendation API endpoints tested!')
