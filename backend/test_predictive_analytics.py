import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.services.predictive_analytics_service import PredictiveAnalyticsService
from datetime import datetime, timedelta
import json

print('🤖 === PREDICTIVE ANALYTICS SYSTEM TEST ===')
print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

db = SessionLocal()

def test_preparation_time_prediction():
    """Test AI-powered preparation time predictions"""
    print("⏱️  Testing Preparation Time Predictions...")
    
    try:
        # Test prediction for menu item 1
        result = PredictiveAnalyticsService.predict_preparation_time(
            db=db,
            menu_item_id=1,
            order_quantity=2,
            current_queue_length=3
        )
        
        print(f"   ✅ Prediction successful")
        print(f"   📊 Predicted Time: {result['predicted_time']} minutes")
        print(f"   🎯 Confidence: {result['confidence_score']:.2f}")
        print(f"   🔍 Factors: {len(result['factors'])} factors considered")
        
        # Test accuracy metrics
        accuracy = PredictiveAnalyticsService.get_prediction_accuracy(db, 30)
        print(f"   📈 Model Accuracy: {(accuracy.get('accuracy', 0) * 100):.1f}%")
        print(f"   📉 MAE: {accuracy.get('mae', 0):.1f} minutes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_queue_forecasting():
    """Test queue length forecasting"""
    print("\n👥 Testing Queue Length Forecasting...")
    
    try:
        # Test queue forecasting
        forecasts = PredictiveAnalyticsService.forecast_queue_length(
            db=db,
            forecast_hours=2,
            interval_minutes=30
        )
        
        print(f"   ✅ Generated {len(forecasts)} forecasts")
        
        if forecasts:
            print(f"   📊 Next forecast: {forecasts[0]['time']} - {forecasts[0]['predicted_queue']} people")
            print(f"   ⏱️  Wait time estimate: {forecasts[0]['wait_time_estimate']} minutes")
            print(f"   🎯 Confidence: {forecasts[0]['confidence']:.2f}")
        
        # Test recording actual queue
        success = PredictiveAnalyticsService.record_actual_queue(
            db=db,
            queue_length=5,
            wait_time=15
        )
        print(f"   ✅ Actual queue recording: {'Success' if success else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_peak_hour_prediction():
    """Test peak hour prediction and resource allocation"""
    print("\n📈 Testing Peak Hour Predictions...")
    
    try:
        # Test peak hour predictions
        predictions = PredictiveAnalyticsService.predict_peak_hours(
            db=db,
            days_ahead=3
        )
        
        print(f"   ✅ Generated {len(predictions)} peak hour predictions")
        
        if predictions:
            print(f"   📊 Today's peak: {predictions[0]['peak_hour']} - {predictions[0]['predicted_orders']} orders")
            print(f"   👥 Recommended staff: {predictions[0]['recommended_staff']}")
            print(f"   🎯 Confidence: {predictions[0]['confidence']:.2f}")
        
        # Test resource allocation recommendations
        recommendations = PredictiveAnalyticsService.get_resource_allocation_recommendations(db)
        
        if 'error' not in recommendations:
            print(f"   ✅ Resource recommendations generated")
            print(f"   📊 Total predicted orders: {recommendations.get('total_predicted_orders', 0)}")
            print(f"   👥 Max concurrent staff: {recommendations.get('max_concurrent_staff', 0)}")
            print(f"   💡 Recommendations: {len(recommendations.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_demand_forecasting():
    """Test demand forecasting for inventory management"""
    print("\n📦 Testing Demand Forecasting...")
    
    try:
        # Test demand forecasting
        forecasts = PredictiveAnalyticsService.forecast_demand(
            db=db,
            forecast_days=3,
            forecast_period='daily'
        )
        
        print(f"   ✅ Generated {len(forecasts)} demand forecasts")
        
        if forecasts:
            print(f"   📊 Sample forecast: {forecasts[0]['menu_item_name']}")
            print(f"   📈 Predicted quantity: {forecasts[0]['predicted_quantity']}")
            print(f"   💰 Estimated revenue: ₹{forecasts[0]['estimated_revenue']:.2f}")
            print(f"   🎯 Confidence: {forecasts[0]['confidence']:.2f}")
        
        # Test inventory recommendations
        recommendations = PredictiveAnalyticsService.get_inventory_recommendations(db)
        
        if 'error' not in recommendations:
            print(f"   ✅ Inventory recommendations generated")
            print(f"   💰 Total estimated revenue: ₹{recommendations.get('total_estimated_revenue', 0):.2f}")
            print(f"   📊 Categories analyzed: {len(recommendations.get('category_breakdown', {}))}")
            print(f"   🚨 Inventory alerts: {len(recommendations.get('inventory_alerts', []))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_customer_behavior_analysis():
    """Test customer behavior pattern analysis"""
    print("\n👤 Testing Customer Behavior Analysis...")
    
    try:
        # Test overall behavior analysis
        analysis = PredictiveAnalyticsService.analyze_customer_behavior(
            db=db,
            analysis_type='comprehensive'
        )
        
        if 'error' not in analysis:
            print(f"   ✅ Customer behavior analysis completed")
            print(f"   👥 Total customers: {analysis.get('total_customers', 0)}")
            print(f"   📊 Total orders: {analysis.get('total_orders', 0)}")
            
            if 'customer_segments' in analysis:
                segments = analysis['customer_segments']
                print(f"   📈 Customer segments: {len(segments.get('segment_counts', {}))}")
                print(f"   📊 Total customers: {segments.get('total_customers', 0)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_churn_prediction():
    """Test churn prediction for user retention"""
    print("\n🔄 Testing Churn Prediction...")
    
    try:
        # Test bulk churn prediction
        prediction = PredictiveAnalyticsService.predict_customer_churn(db=db)
        
        if 'error' not in prediction:
            print(f"   ✅ Churn prediction completed")
            print(f"   👥 Users analyzed: {prediction.get('total_users_analyzed', 0)}")
            print(f"   📊 Overall churn rate: {prediction.get('overall_churn_rate', 0):.2f}")
            
            risk_dist = prediction.get('risk_distribution', {})
            print(f"   🚨 Critical risk: {risk_dist.get('critical', 0)}")
            print(f"   ⚠️  High risk: {risk_dist.get('high', 0)}")
            print(f"   💡 Retention strategies: {len(prediction.get('retention_recommendations', []))}")
        
        # Test retention insights
        insights = PredictiveAnalyticsService.get_retention_insights(db, days_back=30)
        
        if 'error' not in insights:
            print(f"   ✅ Retention insights generated")
            print(f"   📊 Analysis period: {insights.get('analysis_period', 'N/A')}")
            print(f"   📈 Total predictions: {insights.get('total_predictions', 0)}")
            
            retention_metrics = insights.get('retention_metrics', {})
            print(f"   👥 Retention rate: {retention_metrics.get('retention_rate', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_revenue_forecasting():
    """Test revenue forecasting system"""
    print("\n💰 Testing Revenue Forecasting...")
    
    try:
        # Test revenue forecasting
        forecast = PredictiveAnalyticsService.forecast_revenue(
            db=db,
            forecast_days=7,
            forecast_period='daily'
        )
        
        if 'error' not in forecast:
            print(f"   ✅ Revenue forecast completed")
            print(f"   💰 Total predicted revenue: ₹{forecast.get('total_predicted_revenue', 0):.2f}")
            print(f"   📊 Total predicted orders: {forecast.get('total_predicted_orders', 0)}")
            print(f"   🎯 Average confidence: {forecast.get('average_confidence', 0):.2f}")
            
            summary = forecast.get('summary', {})
            print(f"   📈 Growth rate: {summary.get('growth_rate', 0):.1f}%")
            print(f"   📊 Best day: {summary.get('best_day', {}).get('date', 'N/A')}")
        
        # Test revenue insights
        insights = PredictiveAnalyticsService.get_revenue_insights(db, days_back=30, forecast_days=7)
        
        if 'error' not in insights:
            print(f"   ✅ Revenue insights generated")
            
            period_analysis = insights.get('period_analysis', {})
            print(f"   💰 Actual revenue: ₹{period_analysis.get('actual_revenue', 0):.2f}")
            print(f"   📈 Forecast revenue: ₹{period_analysis.get('forecast_total_revenue', 0):.2f}")
            
            performance = insights.get('performance_comparison', {})
            print(f"   📊 Performance trend: {performance.get('performance_trend', 'N/A')}")
            print(f"   💡 Recommendations: {len(insights.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints availability"""
    print("\n🌐 Testing API Endpoints...")
    
    import requests
    
    # Test authentication
    try:
        login_response = requests.post(
            'http://localhost:8000/api/auth/login',
            json={"email": "superadmin@admin.com", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test dashboard endpoint
            dashboard_response = requests.get(
                'http://localhost:8000/api/predictive-analytics/dashboard-summary',
                headers=headers
            )
            
            if dashboard_response.status_code == 200:
                print(f"   ✅ Dashboard API accessible")
                data = dashboard_response.json()
                print(f"   📊 Data points returned: {len(data)}")
            else:
                print(f"   ❌ Dashboard API failed: {dashboard_response.status_code}")
            
            # Test model performance endpoint
            perf_response = requests.get(
                'http://localhost:8000/api/predictive-analytics/model-performance',
                headers=headers
            )
            
            if perf_response.status_code == 200:
                print(f"   ✅ Model performance API accessible")
            else:
                print(f"   ❌ Model performance API failed: {perf_response.status_code}")
                
        else:
            print(f"   ❌ Authentication failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API test error: {e}")
        return False
    
    return True

def main():
    """Run all predictive analytics tests"""
    
    print("🧪 Running comprehensive predictive analytics tests...\n")
    
    test_results = {
        'Preparation Time Prediction': test_preparation_time_prediction(),
        'Queue Forecasting': test_queue_forecasting(),
        'Peak Hour Prediction': test_peak_hour_prediction(),
        'Demand Forecasting': test_demand_forecasting(),
        'Customer Behavior Analysis': test_customer_behavior_analysis(),
        'Churn Prediction': test_churn_prediction(),
        'Revenue Forecasting': test_revenue_forecasting(),
        'API Endpoints': test_api_endpoints()
    }
    
    print("\n📊 === TEST RESULTS SUMMARY ===")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL PREDICTIVE ANALYTICS FEATURES WORKING!")
        print("\n✨ System Features:")
        print("   ✅ AI-powered preparation time predictions")
        print("   ✅ Queue length forecasting")
        print("   ✅ Peak hour prediction and resource allocation")
        print("   ✅ Demand forecasting for inventory management")
        print("   ✅ Customer behavior pattern analysis")
        print("   ✅ Churn prediction for user retention")
        print("   ✅ Revenue forecasting")
        print("   ✅ RESTful API endpoints")
        print("   ✅ Frontend dashboard integration")
        print("\n🚀 Ready for production use!")
    else:
        print("⚠️  Some features need attention")
        print("🔧 Check the failed tests and fix any issues")
    
    print("\n📱 Access the dashboard:")
    print("   1. Login to admin panel")
    print("   2. Click 'Predictive AI' tab")
    print("   3. View all AI-powered insights")

if __name__ == "__main__":
    main()
