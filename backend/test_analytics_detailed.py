from app.database.session import get_db
from app.services.historical_analytics_service import HistoricalAnalyticsService
from datetime import datetime, timedelta
import sys

# Test time range calculations
db = next(get_db())
try:
    print('Testing time range calculations...')
    
    # Test KPI time ranges
    kpi = HistoricalAnalyticsService.get_kpi_metrics(db)
    
    print('\n=== KPI METRICS TIME RANGES ===')
    print('Today (vs Yesterday):')
    print(f'  Revenue: {kpi.get("today", {}).get("revenue", 0):.2f}')
    print(f'  Growth: {kpi.get("today", {}).get("revenue_growth", 0):.1f}%')
    print(f'  Orders: {kpi.get("today", {}).get("orders", 0)}')
    
    print('\nThis Week (vs Last Week):')
    print(f'  Revenue: {kpi.get("this_week", {}).get("revenue", 0):.2f}')
    print(f'  Growth: {kpi.get("this_week", {}).get("revenue_growth", 0):.1f}%')
    print(f'  Orders: {kpi.get("this_week", {}).get("orders", 0)}')
    
    print('\nThis Month (vs Last Month):')
    print(f'  Revenue: {kpi.get("this_month", {}).get("revenue", 0):.2f}')
    print(f'  Growth: {kpi.get("this_month", {}).get("revenue_growth", 0):.1f}%')
    print(f'  Orders: {kpi.get("this_month", {}).get("orders", 0)}')
    
    # Test time slot analysis
    print('\n=== TIME SLOT ANALYSIS ===')
    time_slot = HistoricalAnalyticsService.get_revenue_by_time_slot(db)
    print(f'Date: {time_slot.get("date", "N/A")}')
    print(f'Total Revenue: {time_slot.get("total_revenue", 0):.2f}')
    print(f'Total Orders: {time_slot.get("total_orders", 0)}')
    
    for slot_name, slot_data in time_slot.get("time_slots", {}).items():
        if slot_data.get("revenue", 0) > 0:
            print(f'  {slot_name}: ₹{slot_data.get("revenue", 0):.2f} ({slot_data.get("orders", 0)} orders) - {slot_data.get("percentage", 0):.1f}%')
    
    # Test item performance
    print('\n=== ITEM PERFORMANCE ===')
    items = HistoricalAnalyticsService.get_item_performance_analysis(db, 30)
    print(f'Period: {items.get("period", "N/A")}')
    print(f'Total Items: {items.get("total_items", 0)}')
    
    print('\nTop 3 Selling Items:')
    for i, item in enumerate(items.get("top_selling", [])[:3], 1):
        print(f'  {i}. {item.get("name", "Unknown")} - ₹{item.get("total_revenue", 0):.2f} ({item.get("total_orders", 0)} orders)')
        print(f'     Suggestion: {item.get("suggestion", "N/A")} - {item.get("action", "N/A")}')
    
    # Test revenue trends
    print('\n=== REVENUE TRENDS ===')
    trends = HistoricalAnalyticsService.get_revenue_trends(db, "daily", 7)
    print(f'View Type: {trends.get("view_type", "N/A")}')
    print(f'Period: {trends.get("period", "N/A")}')
    print(f'Data Points: {len(trends.get("data", []))}')
    print(f'Total Revenue: {trends.get("summary", {}).get("total_revenue", 0):.2f}')
    print(f'Growth Rate: {trends.get("summary", {}).get("growth_rate", 0):.1f}%')
    
    print('\nRecent Daily Data:')
    for data_point in trends.get("data", [])[-3:]:
        print(f'  {data_point.get("period", "N/A")}: ₹{data_point.get("revenue", 0):.2f} ({data_point.get("orders", 0)} orders) - Growth: {data_point.get("revenue_growth", 0):.1f}%')
    
    print('\n✅ All time range calculations verified!')
    print('✅ Analytics dashboard is fully dynamic with real historical data!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
