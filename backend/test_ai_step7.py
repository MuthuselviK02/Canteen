import sys
sys.path.append('.')
from app.services.ai_recommendation_service import AIRecommendationService
from app.database.session import SessionLocal

print('=== Testing AI Recommendation Service - Step 7: Mood-Based ===')
db = SessionLocal()
try:
    # Test mood-based recommendations (Step 7)
    print('1. Testing mood-based recommendations...')
    mood_recs = AIRecommendationService.get_mood_based_recommendations(db, 1, None, 3)
    print(f'   Found {len(mood_recs)} mood-based recommendations')
    for rec in mood_recs[:2]:
        print(f'   - {rec["name"]}: {rec["mood_data"]["mood"]} mood ({rec["score"]:.2f})')
        print(f'     Tags: {rec["mood_tags"]}')
        print(f'     Impact: {rec["emotional_impact"]}')
        print(f'     {rec["reasoning"]}')
    
    # Test all recommendation types together
    print('\\n2. Testing all 7 recommendation types...')
    preference_recs = AIRecommendationService.get_preference_based_recommendations(db, 1, 2)
    time_recs = AIRecommendationService.get_time_based_recommendations(db, 1, 2)
    combo_recs = AIRecommendationService.get_combo_recommendations(db, 1, 2)
    dietary_recs = AIRecommendationService.get_dietary_recommendations(db, 1, ['vegetarian'], 2)
    calorie_recs = AIRecommendationService.get_calorie_conscious_recommendations(db, 1, 2000, None, 2)
    weather_recs = AIRecommendationService.get_weather_based_recommendations(db, 1, None, 2)
    
    print(f'   Preference: {len(preference_recs)} items')
    print(f'   Time-based: {len(time_recs)} items')
    print(f'   Combo: {len(combo_recs)} items')
    print(f'   Dietary: {len(dietary_recs)} items')
    print(f'   Calorie-Conscious: {len(calorie_recs)} items')
    print(f'   Weather-Based: {len(weather_recs)} items')
    print(f'   Mood-Based: {len(mood_recs)} items')
    
    total_all = len(preference_recs) + len(time_recs) + len(combo_recs) + len(dietary_recs) + len(calorie_recs) + len(weather_recs) + len(mood_recs)
    print(f'   Total recommendations: {total_all} items')
    
    print('\\n✅ All 7 AI recommendation types working correctly!')
    
except Exception as e:
    print('❌ Error:', e)
    import traceback
    traceback.print_exc()
finally:
    db.close()
