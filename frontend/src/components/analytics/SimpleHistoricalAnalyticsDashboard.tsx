import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';

interface SimpleAnalyticsData {
  kpi_metrics?: any;
  revenue_by_time_slot?: any;
  item_performance?: any;
  revenue_trends?: any;
  last_updated?: string;
}

const SimpleHistoricalAnalyticsDashboard: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<SimpleAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Fetching analytics data...');
      
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      console.log('📡 Making API request...');
      const response = await fetch(buildApiUrl('/api/analytics/dashboard'), {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('📊 Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API Error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data: SimpleAnalyticsData = await response.json();
      console.log('✅ Analytics data received:', data);
      
      setAnalyticsData(data);
    } catch (err) {
      console.error('❌ Error fetching analytics data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const formatINR = (amount: number) => {
    if (!Number.isFinite(amount)) return '₹0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-4">Loading analytics data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            <span>Error loading analytics data: {error}</span>
          </div>
          <Button onClick={fetchAnalyticsData} className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!analyticsData) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2 text-gray-700">
            <AlertTriangle className="h-5 w-5" />
            <span>Analytics data is unavailable.</span>
          </div>
          <Button onClick={fetchAnalyticsData} className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Analytics Dashboard (Debug Version)</h1>
          <p className="text-gray-600">Historical and real-time business insights</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={fetchAnalyticsData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Debug Info */}
      <Card>
        <CardHeader>
          <CardTitle>Debug Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><strong>Data Received:</strong> {analyticsData ? 'Yes' : 'No'}</p>
            <p><strong>Last Updated:</strong> {analyticsData?.last_updated || 'N/A'}</p>
            <p><strong>KPI Metrics:</strong> {analyticsData?.kpi_metrics ? 'Available' : 'Missing'}</p>
            <p><strong>Revenue by Time Slot:</strong> {analyticsData?.revenue_by_time_slot ? 'Available' : 'Missing'}</p>
            <p><strong>Item Performance:</strong> {analyticsData?.item_performance ? 'Available' : 'Missing'}</p>
            <p><strong>Revenue Trends:</strong> {analyticsData?.revenue_trends ? 'Available' : 'Missing'}</p>
          </div>
        </CardContent>
      </Card>

      {/* KPI Metrics */}
      {analyticsData.kpi_metrics && (
        <Card>
          <CardHeader>
            <CardTitle>Today's KPI Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold text-blue-600">Revenue</h3>
                <p className="text-2xl font-bold">{formatINR(analyticsData.kpi_metrics.today?.revenue || 0)}</p>
                <p className="text-sm text-gray-600">vs Yesterday</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-600">Orders</h3>
                <p className="text-2xl font-bold">{analyticsData.kpi_metrics.today?.orders || 0}</p>
                <p className="text-sm text-gray-600">vs Yesterday</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <h3 className="font-semibold text-purple-600">Avg Order Value</h3>
                <p className="text-2xl font-bold">{formatINR(analyticsData.kpi_metrics.today?.avg_order_value || 0)}</p>
                <p className="text-sm text-gray-600">vs Yesterday</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <h3 className="font-semibold text-orange-600">Customers</h3>
                <p className="text-2xl font-bold">{analyticsData.kpi_metrics.today?.unique_customers || 0}</p>
                <p className="text-sm text-gray-600">vs Yesterday</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Time Slot Analysis */}
      {analyticsData.revenue_by_time_slot && (
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Time Slot</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {Object.entries(analyticsData.revenue_by_time_slot.time_slots || {}).map(([slot, data]: [string, any]) => (
                <div key={slot} className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold">{slot === 'LateNight' ? 'Late Night' : slot}</h3>
                  <p className="text-xl font-bold text-blue-600">{formatINR(data.revenue || 0)}</p>
                  <p className="text-sm text-gray-600">{data.orders || 0} orders</p>
                  <p className="text-sm font-medium">{(data.percentage || 0).toFixed(1)}% of total</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Raw Data Display */}
      <Card>
        <CardHeader>
          <CardTitle>Raw Data (for debugging)</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-96">
            {JSON.stringify(analyticsData, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
};

export default SimpleHistoricalAnalyticsDashboard;
