#!/usr/bin/env python3
"""
Generate Demand Forecasts from Historical Order Data

This script analyzes historical orders and generates demand forecasts
for the inventory system to eliminate "No Forecast" issues.
"""

from app.database.session import SessionLocal
from app.services.predictive_analytics_service import PredictiveAnalyticsService
from app.models.predictive_analytics import DemandForecast
from datetime import datetime, timedelta
import json

def generate_demand_forecasts():
    """Generate demand forecasts based on historical order data"""
    print("🔮 Generating Demand Forecasts from Historical Data")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Clear existing forecasts
        existing_forecasts = db.query(DemandForecast).count()
        print(f"🗑️ Clearing {existing_forecasts} existing forecasts...")
        db.query(DemandForecast).delete()
        db.commit()
        
        # Generate new forecasts
        print("📊 Analyzing historical order data and generating forecasts...")
        forecasts = PredictiveAnalyticsService.forecast_demand(
            db=db,
            forecast_days=7,
            forecast_period='daily'
        )
        
        print(f"🎯 Generated {len(forecasts)} demand forecasts")
        
        # Display sample forecasts
        if forecasts:
            print("\n📋 Sample Forecasts:")
            for i, forecast in enumerate(forecasts[:10]):
                print(f"  {i+1}. Item {forecast['menu_item_id']}: {forecast['predicted_quantity']} units "
                      f"(confidence: {forecast['confidence']:.2f}) for {forecast['forecast_date']}")
        
        # Save forecasts to database
        print("\n💾 Saving forecasts to database...")
        saved_count = 0
        for forecast_data in forecasts:
            forecast = DemandForecast(
                menu_item_id=forecast_data['menu_item_id'],
                forecast_date=datetime.strptime(forecast_data['forecast_date'], '%Y-%m-%d').date(),
                predicted_quantity=forecast_data['predicted_quantity'],
                confidence_score=forecast_data['confidence'],
                forecast_period='daily',
                created_at=datetime.utcnow()
            )
            db.add(forecast)
            saved_count += 1
        
        db.commit()
        print(f"✅ Successfully saved {saved_count} demand forecasts to database!")
        
        # Verify forecasts were saved
        total_forecasts = db.query(DemandForecast).count()
        print(f"📈 Total forecasts in database: {total_forecasts}")
        
        # Show forecasts by menu item
        print("\n🍽️ Forecasts by Menu Item:")
        item_forecasts = db.query(DemandForecast).all()
        for fc in item_forecasts[:15]:
            print(f"  Item {fc.menu_item_id}: {fc.predicted_quantity} units for {fc.forecast_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating forecasts: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()

def verify_forecasts():
    """Verify that forecasts are working with inventory system"""
    print("\n🔍 Verifying Forecasts Integration")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        # Get today's forecasts
        today = datetime.now().date()
        today_forecasts = db.query(DemandForecast).filter(
            DemandForecast.forecast_date == today
        ).all()
        
        print(f"📅 Today's forecasts ({today}): {len(today_forecasts)}")
        
        if today_forecasts:
            print("Sample today's forecasts:")
            for fc in today_forecasts[:5]:
                print(f"  Item {fc.menu_item_id}: {fc.predicted_quantity} units")
        
        # Test inventory integration
        from app.services.inventory_service import get_inventory_dashboard
        
        start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(days=1)
        
        # Create predictions mapping for inventory
        predictions = {fc.menu_item_id: fc.predicted_quantity for fc in today_forecasts}
        
        kpis, items = get_inventory_dashboard(db, start_dt, end_dt, category="all", predicted_demand_by_item_id=predictions)
        
        print(f"\n📦 Inventory Integration Test:")
        print(f"  Total items: {kpis['total_items']}")
        print(f"  Well stocked: {kpis['well_stocked']}")
        print(f"  Needs restocking: {kpis['needs_restocking']}")
        print(f"  Out of stock: {kpis['out_of_stock']}")
        print(f"  No forecast: {kpis['no_forecast']}")
        
        # Show sample items with forecasts
        items_with_forecast = [item for item in items if item.get('predicted_future_demand') is not None]
        print(f"\n🎯 Items with forecasts: {len(items_with_forecast)}")
        
        if items_with_forecast:
            print("Sample items with forecasts:")
            for item in items_with_forecast[:5]:
                print(f"  {item['item_name']}: {item['remaining_stock']} stock, "
                      f"{item['predicted_future_demand']} predicted, "
                      f"status: {item['inventory_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying forecasts: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = generate_demand_forecasts()
    
    if success:
        verify_forecasts()
        print("\n🎉 Demand forecasting setup completed!")
        print("📊 The inventory system should now show predictions instead of 'No Forecast'")
    else:
        print("\n💥 Failed to generate demand forecasts")
