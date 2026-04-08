import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  Timer,
  TrendingUp,
  TrendingDown,
  ChefHat,
  Activity,
  Target,
  AlertTriangle,
  CheckCircle,
  Zap,
  BarChart3,
  Users,
  Flame
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useOrders } from '@/contexts/OrderContext';
import { formatISTTime } from '@/utils/istTime';

interface KitchenAnalyticsData {
  today_stats: {
    total_orders: number;
    completed_orders: number;
    avg_prep_time: number;
    fastest_prep_time: number;
    slowest_prep_time: number;
  };
  current_queue: {
    pending_count: number;
    preparing_count: number;
    ready_count: number;
    total_active_orders: number;
  };
  efficiency: {
    completion_rate: number;
    avg_orders_per_hour: number;
    peak_hour_performance: number;
    efficiency_score: number;
  };
  alerts: {
    long_waiting_orders: number;
    overdue_orders: number;
    high_volume_alert: boolean;
  };
  hourly_performance: Array<{
    hour: number;
    completed: number;
    avg_time: number;
  }>;
}

export function KitchenAnalytics() {
  const { orders } = useOrders();
  const [analytics, setAnalytics] = useState<KitchenAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(timer);
  }, []);

  const fetchKitchenAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const response = await fetch(buildApiUrl('/api/analytics/kitchen'), {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP error! status: ${response.status}${errorData.detail ? ` - ${errorData.detail}` : ''}`);
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      console.error('Error fetching kitchen analytics:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch kitchen analytics');
      
      // Fallback to client-side calculation and clear error after successful calculation
      calculateClientSideAnalytics();
      // Don't set error state permanently, allow fallback analytics to show
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKitchenAnalytics();
    
    // Set up real-time updates with different intervals based on alert level
    const getUpdateInterval = () => {
      if (!analytics) return 30000; // Default 30 seconds
      
      const alertLevel = getAlertLevel();
      if (alertLevel === 'critical') return 10000; // 10 seconds for critical
      if (alertLevel === 'warning') return 20000; // 20 seconds for warning
      return 30000; // 30 seconds for normal
    };
    
    const interval = setInterval(fetchKitchenAnalytics, getUpdateInterval());
    
    return () => clearInterval(interval);
  }, [orders, currentTime, analytics?.alerts]);

  const calculateClientSideAnalytics = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const todayOrders = orders.filter(order => 
      new Date(order.createdAt) >= today
    );

    const completedToday = todayOrders.filter(order => 
      order.status === 'completed' && order.completedAt
    );

    // Calculate preparation times
    const prepTimes = completedToday.map(order => {
      if (order.startedPreparationAt && order.completedAt) {
        const start = new Date(order.startedPreparationAt);
        const end = new Date(order.completedAt);
        return (end.getTime() - start.getTime()) / (1000 * 60); // minutes
      }
      return null;
    }).filter(Boolean) as number[];

    const avgPrepTime = prepTimes.length > 0 
      ? prepTimes.reduce((a, b) => a + b, 0) / prepTimes.length 
      : 0;

    const fastestPrepTime = prepTimes.length > 0 ? Math.min(...prepTimes) : 0;
    const slowestPrepTime = prepTimes.length > 0 ? Math.max(...prepTimes) : 0;

    // Current queue status
    const pendingCount = orders.filter(o => o.status === 'pending').length;
    const preparingCount = orders.filter(o => o.status === 'preparing').length;
    const readyCount = orders.filter(o => o.status === 'ready').length;

    // Efficiency metrics
    const completionRate = todayOrders.length > 0 
      ? (completedToday.length / todayOrders.length) * 100 
      : 0;

    const hoursElapsed = Math.max(1, (currentTime.getTime() - today.getTime()) / (1000 * 60 * 60));
    const avgOrdersPerHour = completedToday.length / hoursElapsed;

    // Peak hour performance (12-2 PM)
    const peakHourOrders = completedToday.filter(order => {
      const hour = new Date(order.createdAt).getHours();
      return hour >= 12 && hour <= 14;
    });
    const peakHourPerformance = peakHourOrders.length;

    // Efficiency score (0-100)
    const efficiencyScore = Math.min(100, Math.round(
      (completionRate * 0.4) + 
      (avgOrdersPerHour > 10 ? 40 : avgOrdersPerHour * 4) + 
      (avgPrepTime < 15 ? 20 : Math.max(0, 20 - avgPrepTime))
    ));

    // Alerts
    const longWaitingOrders = orders.filter(order => {
      if (order.status === 'pending' || order.status === 'preparing') {
        const waitTime = (currentTime.getTime() - new Date(order.createdAt).getTime()) / (1000 * 60);
        return waitTime > 30; // Orders waiting more than 30 minutes
      }
      return false;
    }).length;

    const overdueOrders = orders.filter(order => {
      if (order.estimatedTime && (order.status === 'pending' || order.status === 'preparing')) {
        const elapsed = (currentTime.getTime() - new Date(order.createdAt).getTime()) / (1000 * 60);
        return elapsed > order.estimatedTime + 10; // 10 minutes grace period
      }
      return false;
    }).length;

    const highVolumeAlert = pendingCount > 10 || preparingCount > 5;

    // Hourly performance for today
    const hourlyPerformance = Array.from({ length: currentTime.getHours() + 1 }, (_, hour) => {
      const hourOrders = completedToday.filter(order => 
        new Date(order.createdAt).getHours() === hour
      );
      
      const hourPrepTimes = hourOrders.map(order => {
        if (order.startedPreparationAt && order.completedAt) {
          const start = new Date(order.startedPreparationAt);
          const end = new Date(order.completedAt);
          return (end.getTime() - start.getTime()) / (1000 * 60);
        }
        return null;
      }).filter(Boolean) as number[];

      return {
        hour,
        completed: hourOrders.length,
        avg_time: hourPrepTimes.length > 0 
          ? hourPrepTimes.reduce((a, b) => a + b, 0) / hourPrepTimes.length 
          : 0
      };
    });

    setAnalytics({
      today_stats: {
        total_orders: todayOrders.length,
        completed_orders: completedToday.length,
        avg_prep_time: Math.round(avgPrepTime * 10) / 10,
        fastest_prep_time: Math.round(fastestPrepTime * 10) / 10,
        slowest_prep_time: Math.round(slowestPrepTime * 10) / 10,
      },
      current_queue: {
        pending_count: pendingCount,
        preparing_count: preparingCount,
        ready_count: readyCount,
        total_active_orders: pendingCount + preparingCount + readyCount,
      },
      efficiency: {
        completion_rate: Math.round(completionRate * 10) / 10,
        avg_orders_per_hour: Math.round(avgOrdersPerHour * 10) / 10,
        peak_hour_performance: peakHourPerformance,
        efficiency_score: efficiencyScore,
      },
      alerts: {
        long_waiting_orders: longWaitingOrders,
        overdue_orders: overdueOrders,
        high_volume_alert: highVolumeAlert,
      },
      hourly_performance: hourlyPerformance,
    });
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes.toFixed(1)}m`;
    } else {
      const hours = Math.floor(minutes / 60);
      const mins = Math.round(minutes % 60);
      return `${hours}h ${mins}m`;
    }
  };

  const getEfficiencyColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAlertLevel = () => {
    if (!analytics) return 'normal';
    if (analytics.alerts.overdue_orders > 0 || analytics.alerts.high_volume_alert) return 'critical';
    if (analytics.alerts.long_waiting_orders > 0) return 'warning';
    return 'normal';
  };

  // Simple test render first
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
              <AlertTriangle className="h-5 w-5" />
              <span>No analytics data available</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Always show analytics if we have data, regardless of error state
  const alertLevel = getAlertLevel();

  return (
    <div className="space-y-6">
      {/* Show warning if there's an error but we still have analytics */}
      {error && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-yellow-600">
              <AlertTriangle className="h-5 w-5" />
              <span>Using real-time data (API unavailable)</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Show analytics if available */}
      {analytics && (
        <>
          {/* Real-time Status Header */}
          <Card className={`border-l-4 ${
            alertLevel === 'critical' 
              ? 'border-red-500 bg-red-50' 
              : alertLevel === 'warning' 
              ? 'border-yellow-500 bg-yellow-50'
              : 'border-green-500 bg-green-50'
          }`}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full animate-pulse ${
                    alertLevel === 'critical' 
                      ? 'bg-red-500' 
                      : alertLevel === 'warning' 
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`} />
                  <div>
                    <h3 className={`font-semibold ${
                      alertLevel === 'critical' 
                        ? 'text-red-800' 
                        : alertLevel === 'warning' 
                        ? 'text-yellow-800'
                        : 'text-green-800'
                    }`}>
                      Kitchen Status: {alertLevel === 'critical' ? 'Critical' : alertLevel === 'warning' ? 'Warning' : 'Normal'}
                    </h3>
                    <p className={`text-sm ${
                      alertLevel === 'critical' 
                        ? 'text-red-700' 
                        : alertLevel === 'warning' 
                        ? 'text-yellow-700'
                        : 'text-green-700'
                    }`}>
                      {alertLevel === 'critical' 
                        ? `${analytics.alerts.overdue_orders} overdue orders. Immediate attention required!`
                        : alertLevel === 'warning' 
                        ? `${analytics.alerts.long_waiting_orders} orders waiting longer than 30 minutes.`
                        : `Kitchen operating normally. ${analytics.current_queue.total_active_orders} active orders.`
                      }
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground">Last Updated</div>
                  <div className="text-lg font-semibold">{formatISTTime(currentTime)}</div>
                </div>
              </div>
            </CardContent>
          </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Queue</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
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
            <CardTitle className="text-sm font-medium">Avg Prep Time</CardTitle>
            <Timer className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatTime(analytics.today_stats.avg_prep_time)}</div>
            <div className="flex gap-2 mt-1">
              <span className="text-xs text-muted-foreground">
                Fast: {formatTime(analytics.today_stats.fastest_prep_time)}
              </span>
              <span className="text-xs text-muted-foreground">
                Slow: {formatTime(analytics.today_stats.slowest_prep_time)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
            <Target className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.efficiency.completion_rate}%</div>
            <div className="text-xs text-muted-foreground">
              {analytics.today_stats.completed_orders} of {analytics.today_stats.total_orders} orders
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Efficiency Score</CardTitle>
            <Zap className={`h-4 w-4 ${getEfficiencyColor(analytics.efficiency.efficiency_score)}`} />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getEfficiencyColor(analytics.efficiency.efficiency_score)}`}>
              {analytics.efficiency.efficiency_score}/100
            </div>
            <div className="text-xs text-muted-foreground">
              {analytics.efficiency.avg_orders_per_hour} orders/hr
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Today's Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Peak Hour (12-2 PM):</span>
                <div className="font-semibold">{analytics.efficiency.peak_hour_performance} orders</div>
              </div>
              <div>
                <span className="text-muted-foreground">Orders/Hour:</span>
                <div className="font-semibold">{analytics.efficiency.avg_orders_per_hour}</div>
              </div>
              <div>
                <span className="text-muted-foreground">Completed Today:</span>
                <div className="font-semibold">{analytics.today_stats.completed_orders}</div>
              </div>
              <div>
                <span className="text-muted-foreground">Ready for Pickup:</span>
                <div className="font-semibold">{analytics.current_queue.ready_count}</div>
              </div>
            </div>

            {/* Hourly Performance Bars */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-muted-foreground">Hourly Performance</h4>
              <div className="space-y-1">
                {analytics.hourly_performance.slice(-8).map(({ hour, completed, avg_time }) => (
                  <div key={hour} className="flex items-center gap-3">
                    <div className="w-12 text-xs text-muted-foreground">{hour}:00</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                      <div 
                        className="bg-blue-500 h-full rounded-full flex items-center justify-end pr-2"
                        style={{ width: `${Math.min(100, completed * 10)}%` }}
                      >
                        {completed > 0 && (
                          <span className="text-xs text-white font-medium">{completed}</span>
                        )}
                      </div>
                    </div>
                    {avg_time > 0 && (
                      <div className="text-xs text-muted-foreground w-16 text-right">
                        {formatTime(avg_time)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Kitchen Status Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <ChefHat className="h-8 w-8 text-blue-600" />
              <div>
                <h3 className="font-semibold text-blue-900">Kitchen Status</h3>
                <p className="text-sm text-blue-700">
                  {analytics.current_queue.total_active_orders === 0 
                    ? 'Ready for orders' 
                    : `Processing ${analytics.current_queue.total_active_orders} orders`
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-50 to-green-100">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <h3 className="font-semibold text-green-900">Today's Progress</h3>
                <p className="text-sm text-green-700">
                  {analytics.today_stats.completed_orders} orders completed
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-orange-50 to-orange-100">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Flame className="h-8 w-8 text-orange-600" />
              <div>
                <h3 className="font-semibold text-orange-900">Performance</h3>
                <p className="text-sm text-orange-700">
                  {analytics.efficiency.efficiency_score >= 80 ? 'Excellent' : 
                   analytics.efficiency.efficiency_score >= 60 ? 'Good' : 'Needs Improvement'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
        </>
      )}
    </div>
  );
}
