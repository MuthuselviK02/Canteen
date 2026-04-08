import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useOrders } from '@/contexts/OrderContext';
import { getCurrentISTTime } from '@/utils/istTime';

export function KitchenAnalyticsMinimal() {
  const { orders } = useOrders();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    // Simple client-side calculation as fallback
    const calculateClientSideAnalytics = () => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const todayOrders = orders.filter(order => 
        new Date(order.createdAt) >= today
      );

      const completedToday = todayOrders.filter(order => 
        order.status === 'completed' && order.completedAt
      );

      console.log('Kitchen Analytics Debug:', {
        totalOrders: orders.length,
        todayOrders: todayOrders.length,
        completedToday: completedToday.length,
        completionRate: todayOrders.length > 0 ? (completedToday.length / todayOrders.length) * 100 : 0
      });

      const pendingCount = orders.filter(o => o.status === 'pending').length;
      const preparingCount = orders.filter(o => o.status === 'preparing').length;
      const readyCount = orders.filter(o => o.status === 'ready').length;

      setAnalytics({
        today_stats: {
          total_orders: todayOrders.length,
          completed_orders: completedToday.length,
          avg_prep_time: 0,
          fastest_prep_time: 0,
          slowest_prep_time: 0,
        },
        current_queue: {
          pending_count: pendingCount,
          preparing_count: preparingCount,
          ready_count: readyCount,
          total_active_orders: pendingCount + preparingCount + readyCount,
        },
        efficiency: {
          completion_rate: todayOrders.length > 0 ? (completedToday.length / todayOrders.length) * 100 : 0,
          avg_orders_per_hour: 0,
          peak_hour_performance: 0,
          efficiency_score: 50,
        },
        alerts: {
          long_waiting_orders: 0,
          overdue_orders: 0,
          high_volume_alert: false,
        },
        hourly_performance: [],
        kitchen_status: {
          status: 'normal',
          estimated_clear_time: 0,
          staff_efficiency: true
        }
      });
    };

    calculateClientSideAnalytics();
  }, [orders]);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Kitchen Analytics</h2>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Kitchen Analytics</h2>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-600">
              <span>No analytics data available</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Simple Status Header */}
      <Card className="border-l-4 border-green-500 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
              <div>
                <h3 className="font-semibold text-green-800">Kitchen Status: Normal</h3>
                <p className="text-sm text-green-700">
                  Kitchen operating normally. {analytics.current_queue.total_active_orders} active orders.
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Last Updated</div>
              <div className="text-lg font-semibold">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Queue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.current_queue.total_active_orders}</div>
            <div className="flex gap-2 mt-1">
              <Badge variant="secondary" className="text-xs">
                {analytics.current_queue.pending_count} pending
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {analytics.current_queue.preparing_count} preparing
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Orders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.today_stats.total_orders}</div>
            <div className="text-xs text-muted-foreground">
              Completed: {analytics.today_stats.completed_orders}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.efficiency.completion_rate.toFixed(1)}%</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Efficiency Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{analytics.efficiency.efficiency_score}/100</div>
          </CardContent>
        </Card>
      </div>

      {/* Status Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                <span className="text-white text-xs font-bold">K</span>
              </div>
              <div>
                <h3 className="font-semibold text-blue-900">Kitchen Status</h3>
                <p className="text-sm text-blue-700">
                  Processing {analytics.current_queue.total_active_orders} orders
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
