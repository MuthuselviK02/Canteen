from app.database.session import get_db
from app.services.historical_analytics_service import HistoricalAnalyticsService

db = next(get_db())
try:
    print('🔧 TESTING LOW SELLING ITEMS FIX')
    print('=' * 40)
    
    items = HistoricalAnalyticsService.get_item_performance_analysis(db, 30)
    
    print(f'Total items: {items.get("total_items", 0)}')
    print(f'Top selling items: {len(items.get("top_selling", []))}')
    print(f'Low selling items: {len(items.get("low_selling", []))}')
    
    if items.get('low_selling'):
        print('\n📉 LOW SELLING ITEMS NOW:')
        for i, item in enumerate(items['low_selling'][:5], 1):
            print(f'{i}. {item["name"]} - ₹{item["total_revenue"]:.2f} ({item["total_orders"]} orders) - {item["suggestion"]}')
        print('\n✅ Low selling items section is now working!')
    else:
        print('\n❌ Still empty')
        
except Exception as e:
    print(f'❌ Error: {e}')
finally:
    db.close()
