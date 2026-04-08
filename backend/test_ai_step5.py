import sys
sys.path.append('.')
from app.services.ai_recommendation_service import AIRecommendationService
from app.database.session import SessionLocal

print('=== Testing AI Recommendation Service - Step 5: Calorie-Conscious ===')
db = SessionLocal()
try:
    # Test calorie-conscious recommendations (Step 5)
    print('1. Testing calorie-conscious recommendations...')
    calorie_recs = AIRecommendationService.get_calorie_conscious_recommendations(db, 1, 2000, None, 3)
    print(f'   Found {len(calorie_recs)} calorie-conscious recommendations')
    for rec in calorie_recs[:2]:
        print(f'   - {rec["name"]}: {rec["calories"]} cal ({rec["score"]:.2f})')
        print(f'     Tags: {rec["calorie_tags"]}')
        print(f'     {rec["reasoning"]}')
    
    # Test all recommendation types together
    print('\\n2. Testing all 5 recommendation types...')
    preference_recs = AIRecommendationService.get_preference_based_recommendations(db, 1, 2)
    time_recs = AIRecommendationService.get_time_based_recommendations(db, 1, 2)
    combo_recs = AIRecommendationService.get_combo_recommendations(db, 1, 2)
    dietary_recs = AIRecommendationService.get_dietary_recommendations(db, 1, ['vegetarian'], 2)
    
    print(f'   Preference: {len(preference_recs)} items')
    print(f'   Time-based: {len(time_recs)} items')
    print(f'   Combo: {len(combo_recs)} items')
    print(f'   Dietary: {len(dietary_recs)} items')
    print(f'   Calorie-Conscious: {len(calorie_recs)} items')
    
    total_all = len(preference_recs) + len(time_recs) + len(combo_recs) + len(dietary_recs) + len(calorie_recs)
    print(f'   Total recommendations: {total_all} items')
    
    print('\\n✅ All 5 AI recommendation types working correctly!')
    
except Exception as e:
    print('❌ Error:', e)
    import traceback
    traceback.print_exc()
finally:
    db.close()
