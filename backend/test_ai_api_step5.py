import requests
import json

print('=== Testing AI Recommendation API - Step 5: Calorie-Conscious ===')

# Test calorie-conscious recommendations
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/calorie-conscious?daily_calorie_goal=2000', timeout=10)
    print(f'Calorie-Conscious Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} calorie-conscious recommendations')
        for rec in data["recommendations"][:2]:
            print(f'   - {rec["name"]}: {rec["category"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

# Test all recommendations (now includes calorie-conscious)
try:
    response = requests.get('http://localhost:8000/api/ai/recommendations/all?daily_calorie_goal=2000', timeout=10)
    print(f'All Recommendations Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Found {data["total_count"]} recommendations')
        print(f'   Types: {data["recommendation_types"]}')
        for rec in data["recommendations"][:5]:
            print(f'   - {rec["name"]}: {rec["recommendation_type"]} ({rec["confidence"]:.2f})')
    else:
        print(f'   Error: {response.text}')
except Exception as e:
    print(f'   Connection Error: {e}')

print('\n✅ AI Recommendation API endpoints tested!')
