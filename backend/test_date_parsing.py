from app.database.session import get_db
from app.services.historical_analytics_service import HistoricalAnalyticsService
from datetime import datetime, timedelta
import sys

# Test date parsing
db = next(get_db())
try:
    print('🔍 TESTING DATE PARSING ISSUES')
    print('=' * 40)
    
    # Test with no dates (default behavior)
    print('1. Testing default behavior (no dates):')
    try:
        result = HistoricalAnalyticsService.get_kpi_metrics(db)
        print(f'✅ Success: {len(result)} keys returned')
        if 'current_period' in result:
            print(f'   Period: {result["current_period"]["period_start"]} to {result["current_period"]["period_end"]}')
    except Exception as e:
        print(f'❌ Error: {e}')
    
    # Test with custom dates
    print('\n2. Testing custom date range:')
    try:
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 1, 31, 23, 59, 59)
        result = HistoricalAnalyticsService.get_kpi_metrics(db, start_date, end_date)
        print(f'✅ Success: {len(result)} keys returned')
        if 'current_period' in result:
            print(f'   Period: {result["current_period"]["period_start"]} to {result["current_period"]["period_end"]}')
    except Exception as e:
        print(f'❌ Error: {e}')
    
    # Test edge cases
    print('\n3. Testing edge cases:')
    test_cases = [
        ('Same day', datetime(2026, 1, 15), datetime(2026, 1, 15, 23, 59, 59)),
        ('One hour', datetime(2026, 1, 15, 10), datetime(2026, 1, 15, 11)),
        ('Future date', datetime.now() + timedelta(days=1), datetime.now() + timedelta(days=2)),
    ]
    
    for name, start, end in test_cases:
        try:
            result = HistoricalAnalyticsService.get_kpi_metrics(db, start, end)
            print(f'✅ {name}: Success')
        except Exception as e:
            print(f'❌ {name}: {e}')
    
    # Test revenue trends with date range
    print('\n4. Testing revenue trends with date range:')
    try:
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 1, 31, 23, 59, 59)
        result = HistoricalAnalyticsService.get_revenue_trends(db, 'daily', 30)
        print(f'✅ Revenue trends: {len(result.get("data", []))} data points')
        if result.get('data'):
            print(f'   First point: {result["data"][0]["period"]}')
            print(f'   Last point: {result["data"][-1]["period"]}')
    except Exception as e:
        print(f'❌ Revenue trends error: {e}')
        
except Exception as e:
    print(f'❌ General error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
