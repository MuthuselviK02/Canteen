from app.database.session import get_db
from app.services.historical_analytics_service import HistoricalAnalyticsService
import sys

# Test database connection and analytics
db = next(get_db())
try:
    print('Testing KPI metrics...')
    kpi = HistoricalAnalyticsService.get_kpi_metrics(db)
    print(f'Today revenue: {kpi.get("today", {}).get("revenue", 0)}')
    print(f'Today orders: {kpi.get("today", {}).get("orders", 0)}')
    
    print('\nTesting revenue by time slot...')
    time_slot = HistoricalAnalyticsService.get_revenue_by_time_slot(db)
    print(f'Total revenue: {time_slot.get("total_revenue", 0)}')
    print(f'Time slots: {list(time_slot.get("time_slots", {}).keys())}')
    
    print('\nTesting item performance...')
    items = HistoricalAnalyticsService.get_item_performance_analysis(db, 30)
    print(f'Total items analyzed: {items.get("total_items", 0)}')
    print(f'Top selling items: {len(items.get("top_selling", []))}')
    
    print('\nTesting revenue trends...')
    trends = HistoricalAnalyticsService.get_revenue_trends(db, "daily", 7)
    print(f'Data points: {len(trends.get("data", []))}')
    print(f'Summary revenue: {trends.get("summary", {}).get("total_revenue", 0)}')
    
    print('\n✅ All analytics functions working with real data!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
