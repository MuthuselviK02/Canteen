import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, ShoppingCart, TrendingUp, Target } from 'lucide-react';
import { fetchSharedMetrics, SharedMetrics } from '@/utils/dashboardDataSync';
import { formatISTTime } from '@/utils/istTime';

interface SharedMetricsCardProps {
  title?: string;
  showLastUpdated?: boolean;
  className?: string;
}

export function SharedMetricsCard({ 
  title = "Today's Performance", 
  showLastUpdated = true,
  className = "" 
}: SharedMetricsCardProps) {
  const [metrics, setMetrics] = useState<SharedMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        setLoading(true);
        const data = await fetchSharedMetrics();
        if (data) {
          setMetrics(data);
        } else {
          setError('Failed to load metrics');
        }
      } catch (err) {
        setError('Error loading metrics');
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
    
    // Refresh every 5 minutes
    const interval = setInterval(loadMetrics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-lg font-medium">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded mb-2 mx-auto w-16"></div>
                <div className="h-8 bg-gray-200 rounded mx-auto w-20"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-lg font-medium">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-red-600 py-4">
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">{title}</CardTitle>
        <Badge variant="outline" className="text-xs">
          Live Data
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {/* Today's Revenue */}
          <div className="space-y-2 text-center p-3 rounded-lg bg-green-50 border border-green-100 hover:bg-green-100 hover:shadow-md transition-all duration-200 cursor-pointer">
            <div className="flex items-center justify-center text-sm font-medium text-green-700">
              <DollarSign className="w-4 h-4 mr-2" />
              Revenue
            </div>
            <div className="text-2xl font-bold text-green-600">
              ₹{metrics?.today_revenue?.toLocaleString() || '0'}
            </div>
          </div>

          {/* Today's Orders */}
          <div className="space-y-2 text-center p-3 rounded-lg bg-blue-50 border border-blue-100 hover:bg-blue-100 hover:shadow-md transition-all duration-200 cursor-pointer">
            <div className="flex items-center justify-center text-sm font-medium text-blue-700">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Orders
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {metrics?.today_orders || '0'}
            </div>
          </div>

          {/* Average Order Value */}
          <div className="space-y-2 text-center p-3 rounded-lg bg-purple-50 border border-purple-100 hover:bg-purple-100 hover:shadow-md transition-all duration-200 cursor-pointer">
            <div className="flex items-center justify-center text-sm font-medium text-purple-700">
              <TrendingUp className="w-4 h-4 mr-2" />
              Avg Order
            </div>
            <div className="text-2xl font-bold text-purple-600">
              ₹{metrics?.avg_order_value?.toFixed(0) || '0'}
            </div>
          </div>

          {/* Completion Rate */}
          <div className="space-y-2 text-center p-3 rounded-lg bg-orange-50 border border-orange-100 hover:bg-orange-100 hover:shadow-md transition-all duration-200 cursor-pointer">
            <div className="flex items-center justify-center text-sm font-medium text-orange-700">
              <Target className="w-4 h-4 mr-2" />
              Completion
            </div>
            <div className="text-2xl font-bold text-orange-600">
              {metrics?.completion_rate?.toFixed(1) || '0'}%
            </div>
          </div>
        </div>

        {showLastUpdated && metrics?.last_updated && (
          <div className="mt-4 pt-4 border-t text-xs text-muted-foreground text-center">
            Last updated: {formatISTTime(new Date(metrics.last_updated))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default SharedMetricsCard;
