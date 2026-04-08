import sys
sys.path.append('.')
from app.services.ai_recommendation_service import AIRecommendationService
from app.database.session import SessionLocal

print('=== Testing AI Recommendation Service ===')
db = SessionLocal()
try:
    # Test preference-based recommendations
    print('1. Testing preference-based recommendations...')
    recommendations = AIRecommendationService.get_preference_based_recommendations(db, 1, 5)
    print(f'   Found {len(recommendations)} recommendations')
    for rec in recommendations[:2]:
        print(f'   - {rec["name"]}: {rec["score"]:.2f} ({rec["recommendation_type"]})')
    
    # Test time-based recommendations
    print('\n2. Testing time-based recommendations...')
    time_recs = AIRecommendationService.get_time_based_recommendations(db, 1, 3)
    print(f'   Found {len(time_recs)} time-based recommendations')
    for rec in time_recs:
        print(f'   - {rec["name"]}: {rec["meal_type"]} ({rec["score"]:.2f})')
    
    # Test user preferences
    print('\n3. Testing user preference analysis...')
    preferences = AIRecommendationService.get_user_preferences(db, 1)
    print(f'   Total orders: {preferences["total_orders"]}')
    print(f'   Category preferences: {preferences["category_preferences"]}')
    
    print('\n✅ AI Recommendation Service working correctly!')
    
except Exception as e:
    print('❌ Error:', e)
    import traceback
    traceback.print_exc()
finally:
    db.close()
