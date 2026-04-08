#!/usr/bin/env python3
"""
Test the updated inventory service with automatic forecast fetching
"""

from app.database.session import SessionLocal
from app.services.inventory_service import get_inventory_dashboard
from datetime import datetime, timedelta

def test_inventory_service():
    db = SessionLocal()
    
    try:
        start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(days=1)

        print('🧪 Testing Updated Inventory Service')
        print('=' * 40)

        kpis, items = get_inventory_dashboard(db, start_dt, end_dt, category='all')

        print(f'📦 Inventory Results:')
        print(f'  Total items: {kpis["total_items"]}')
        print(f'  Well stocked: {kpis["well_stocked"]}')
        print(f'  Needs restocking: {kpis["needs_restocking"]}')
        print(f'  Out of stock: {kpis["out_of_stock"]}')
        print(f'  No forecast: {kpis["no_forecast"]}')

        # Show sample items with forecasts
        items_with_forecast = [item for item in items if item.get('predicted_future_demand') is not None]
        print(f'\n🎯 Items with forecasts: {len(items_with_forecast)}')

        if items_with_forecast:
            print('Sample items with forecasts:')
            for item in items_with_forecast[:5]:
                print(f'  {item["item_name"]}: {item["remaining_stock"]} stock, '
                      f'{item["predicted_future_demand"]} predicted, '
                      f'status: {item["inventory_status"]}')
        
        success = kpis['no_forecast'] == 0
        if success:
            print(f'\n🎉 SUCCESS! All items now have forecasts!')
        else:
            print(f'\n⚠️ {kpis["no_forecast"]} items still show "No Forecast"')
        
        return success
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    test_inventory_service()
