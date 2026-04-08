#!/usr/bin/env python3
"""
Quick test to check if the inventory service changes are working
"""

from app.database.session import SessionLocal
from app.services.inventory_service import get_inventory_dashboard
from datetime import datetime

def quick_test():
    print("🧪 Quick Inventory Service Test")
    print("=" * 35)
    
    try:
        db = SessionLocal()
        
        # Test with simple dates
        start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt.replace(hour=23, minute=59, second=59)
        
        print(f"Testing with dates: {start_dt} to {end_dt}")
        
        kpis, items = get_inventory_dashboard(db, start_dt, end_dt, category='all')
        
        print(f"✅ SUCCESS: {len(items)} items")
        print(f"KPIs: total={kpis['total_items']}, well_stocked={kpis['well_stocked']}, no_forecast={kpis['no_forecast']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    quick_test()
