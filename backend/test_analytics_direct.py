"""
Test analytics endpoint without cache by calling the service directly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from app.services.predictive_analytics_service import PredictiveAnalyticsService

def test_analytics_direct():
    try:
        print("🧪 Testing analytics service directly...")
        
        db = SessionLocal()
        
        # Test the service directly
        analytics_data = PredictiveAnalyticsService.get_dashboard_summary(db)
        
        print("✅ Analytics service call successful")
        print(f"KPIs: {analytics_data.get('kpis', {})}")
        print(f"Trends: {analytics_data.get('trends', {})}")
        print(f"Time slots: {analytics_data.get('time_slot_analysis', {})}")
        
        db.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Analytics Service Directly")
    print("=" * 50)
    test_analytics_direct()
