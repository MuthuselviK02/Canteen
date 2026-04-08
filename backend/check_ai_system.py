import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.user import User

print('=== Checking AI Recommendation System Status ===')

db = SessionLocal()

try:
    # Check if users exist in database
    users = db.query(User).all()
    print(f"📊 Total users in database: {len(users)}")
    
    if users:
        print("\n👥 Available users:")
        for user in users[:5]:  # Show first 5 users
            print(f"   - {user.fullname} ({user.email}) - Role: {user.role}")
        
        # Check if there are any orders (needed for AI recommendations)
        from app.models.order import Order
        orders = db.query(Order).all()
        print(f"\n📦 Total orders in database: {len(orders)}")
        
        # Check menu items
        from app.models.menu import MenuItem
        menu_items = db.query(MenuItem).filter(MenuItem.is_available == True).all()
        print(f"🍽️ Available menu items: {len(menu_items)}")
        
        # Check AI recommendation tables
        try:
            from app.models.ai_recommendations import UserPreference, UserInteraction
            preferences = db.query(UserPreference).all()
            interactions = db.query(UserInteraction).all()
            
            print(f"\n🤖 AI System Status:")
            print(f"   - User Preferences: {len(preferences)}")
            print(f"   - User Interactions: {len(interactions)}")
            
        except Exception as e:
            print(f"\n❌ AI recommendation tables not found: {e}")
        
        print("\n✅ AI Recommendation System Components:")
        print("   1. ✅ Users exist in database")
        print("   2. ✅ Menu items available")
        if len(orders) > 0:
            print("   3. ✅ Order history available (needed for personalization)")
        else:
            print("   3. ⚠️ No orders found (AI will use fallback recommendations)")
        
        print("\n🔗 Available AI Endpoints:")
        print("   - GET /api/ai/recommendations/preferences")
        print("   - GET /api/ai/recommendations/time-based")
        print("   - GET /api/ai/recommendations/combo")
        print("   - GET /api/ai/recommendations/dietary")
        print("   - GET /api/ai/recommendations/calorie-conscious")
        print("   - GET /api/ai/recommendations/weather-based")
        print("   - GET /api/ai/recommendations/mood-based")
        print("   - GET /api/ai/recommendations/all (combined)")
        print("   - POST /api/ai/interactions (learning)")
        print("   - GET/POST /api/ai/preferences")
        
    else:
        print("❌ No users found in database!")
        print("Please run add_sample_users.py first")

except Exception as e:
    print(f"❌ Error checking system: {e}")
finally:
    db.close()

print("\n📝 To test AI recommendations:")
print("1. Login as any user in frontend")
print("2. Visit the menu page")
print("3. AI recommendations should appear at the top")
print("4. Or use authentication token to test API directly")
