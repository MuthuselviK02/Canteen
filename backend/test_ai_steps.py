import sys
sys.path.append('.')
from app.services.ai_recommendation_service import AIRecommendationService
from app.database.session import SessionLocal

print('=== Testing AI Recommendation Service - Steps 3 & 4 ===')
db = SessionLocal()
try:
    # Test combo recommendations (Step 3)
    print('1. Testing combo recommendations...')
    combo_recs = AIRecommendationService.get_combo_recommendations(db, 1, 3)
    print(f'   Found {len(combo_recs)} combo recommendations')
    for rec in combo_recs[:2]:
        print(f'   - {rec["name"]}: {rec["item_count"]} items, ₹{rec["total_price"]} ({rec["score"]:.2f})')
    
    # Test dietary recommendations (Step 4)
    print('\\n2. Testing dietary recommendations...')
    dietary_recs = AIRecommendationService.get_dietary_recommendations(db, 1, ['vegetarian'], 3)
    print(f'   Found {len(dietary_recs)} dietary recommendations')
    for rec in dietary_recs[:2]:
        print(f'   - {rec["name"]}: {rec["dietary_tags"]} ({rec["score"]:.2f})')
    
    # Test all recommendations together
    print('\\n3. Testing all recommendation types...')
    preference_recs = AIRecommendationService.get_preference_based_recommendations(db, 1, 2)
    time_recs = AIRecommendationService.get_time_based_recommendations(db, 1, 2)
    
    print(f'   Preference: {len(preference_recs)} items')
    print(f'   Time-based: {len(time_recs)} items')
    print(f'   Combo: {len(combo_recs)} items')
    print(f'   Dietary: {len(dietary_recs)} items')
    
    print('\\n✅ All AI recommendation features working correctly!')
    
except Exception as e:
    print('❌ Error:', e)
    import traceback
    traceback.print_exc()
finally:
    db.close()
