import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import DateRangePicker from '@/components/analytics/DateRangePicker';
import EnhancedAnalyticsChart from '@/components/analytics/EnhancedAnalyticsChart';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  ShoppingCart,
  Clock,
  Calendar,
  Target,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { formatISTTime, formatISTDate, getBusinessDayForAPI, getISTDateRange } from '@/utils/istTime';

// Types for analytics data
interface KPIMetrics {
  current_period: {
    revenue: number;
    orders: number;
    avg_order_value: number;
    unique_customers: number;
    revenue_growth: number;
    orders_growth: number;
    avg_order_growth: number;
    customers_growth: number;
    period_start: string;
    period_end: string;
  };
  previous_period: {
    revenue: number;
    orders: number;
    avg_order_value: number;
    unique_customers: number;
    period_start: string;
    period_end: string;
  };
}

interface TimeSlotData {
  revenue: number;
  orders: number;
  percentage: number;
  items: Array<{
    name: string;
    quantity: number;
    revenue: number;
  }>;
}

interface RevenueByTimeSlot {
  date: string;
  total_revenue: number;
  total_orders: number;
  time_slots: {
    Breakfast: TimeSlotData;
    Lunch: TimeSlotData;
    Snacks: TimeSlotData;
    Dinner: TimeSlotData;
    LateNight: TimeSlotData;
  };
}

interface ItemPerformance {
  name: string;
  category: string;
  price: number;
  total_quantity: number;
  total_orders: number;
  avg_quantity_per_order: number;
  total_revenue: number;
  suggestion: string;
  action: string;
}

interface RevenueTrendPoint {
  period: string;
  date: string;  // Add date field for charts
  revenue: number;
  orders: number;
  customers: number;
  avg_order_value: number;
  revenue_growth: number;
  orders_growth: number;
  customers_growth: number;
  target_revenue: number;
  target_achieved: number;
}

interface RevenueTrends {
  view_type: string;
  period: string;
  data: RevenueTrendPoint[];
  summary: {
    total_revenue: number;
    total_orders: number;
    avg_revenue_per_period: number;
    growth_rate: number;
  };
}

interface AnalyticsData {
  kpi_metrics: KPIMetrics;
  revenue_by_time_slot: RevenueByTimeSlot;
  item_performance: {
    period: string;
    total_items: number;
    top_selling: ItemPerformance[];
    low_selling: ItemPerformance[];
  };
  revenue_trends: {
    daily: RevenueTrends;
    weekly: RevenueTrends;
    monthly: RevenueTrends;
  };
  last_updated: string;
}

const HistoricalAnalyticsDashboard: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get business day for consistency with billing
  const getBusinessDay = () => {
    return getBusinessDayForAPI();
  };

  const [selectedDate, setSelectedDate] = useState<string>(getBusinessDay());

  // Set default date range to last 7 days for better analytics visibility
  const dateRange = getISTDateRange(6); // Last 7 days including today
  const [startDate, setStartDate] = useState<string>(dateRange.start);
  const [endDate, setEndDate] = useState<string>(dateRange.end);
  const [showDateRange, setShowDateRange] = useState(false);

  // Simple cache
  const cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

  const getCachedData = (key: string): any | null => {
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.data;
    }
    cache.delete(key);
    return null;
  };

  const setCachedData = (key: string, data: any, ttl: number = 300000): void => {
    cache.set(key, { data, timestamp: Date.now(), ttl });
  };

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check cache first
      const cacheKey = `analytics_dashboard_${startDate}_${endDate}`;
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        setAnalyticsData(cachedData);
        setLoading(false);
        return;
      }

      const token = localStorage.getItem('canteen_token');
      console.log('🔑 Token check:', {
        hasToken: !!token,
        tokenLength: token?.length || 0,
        tokenPreview: token ? `${token.substring(0, 20)}...` : 'none'
      });

      if (!token) {
        console.error('❌ No authentication token found in localStorage');
        setError('Please login to access analytics dashboard');
        setLoading(false);
        return;
      }

      // Build URL with date parameters
      let url = buildApiUrl('/api/analytics/dashboard');
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (params.toString()) url += `?${params.toString()}`;

      console.log('🔄 Fetching analytics data:', {
        startDate,
        endDate,
        url,
        cacheKey
      });

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('📡 Analytics API Response:', {
        status: response.status,
        statusText: response.statusText,
        url: url
      });

      if (!response.ok) {
        console.error('❌ Analytics API Error Response:', {
          status: response.status,
          statusText: response.statusText,
          text: await response.text()
        });

        // Handle specific authentication errors
        if (response.status === 401) {
          console.error('🔐 Authentication failed - token may be expired');
          localStorage.removeItem('canteen_token'); // Clear invalid token
          setError('Your session has expired. Please login again.');
          setTimeout(() => {
            window.location.href = '/login'; // Redirect to login after delay
          }, 3000);
          return;
        }

        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: AnalyticsData = await response.json();

      // Validate data structure
      if (!data || typeof data !== 'object') {
        console.error('❌ Invalid analytics data structure:', data);
        setError('Invalid analytics data received');
        setAnalyticsData(null);
        return;
      }

      setAnalyticsData(data);

      // Cache for 5 minutes
      setCachedData(cacheKey, data, 300000);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, [startDate, endDate, showDateRange]);

  // Auto-apply today's date range on initial load
  useEffect(() => {
    if (startDate && endDate && startDate === endDate) {
      fetchAnalyticsData();
    }
  }, []);

  // Safe data access helpers
  const safeGetKpiValue = (path: string, fallback: any = 0) => {
    try {
      const pathParts = path.split('.');
      let value = analyticsData?.kpi_metrics;
      for (const part of pathParts) {
        if (value && typeof value === 'object' && value[part]) {
          value = value[part];
        } else {
          return fallback;
        }
      }
      return value || fallback;
    } catch (e) {
      console.error('Error accessing KPI data:', e);
      return fallback;
    }
  };

  const safeGetRevenueTrends = (path: string, fallback: any = []) => {
    try {
      const pathParts = path.split('.');
      let value = analyticsData?.revenue_trends;

      for (const part of pathParts) {
        if (value && typeof value === 'object' && value[part] !== undefined) {
          value = value[part];
        } else {
          return fallback;
        }
      }
      return value || fallback;
    } catch (e) {
      console.error('Error accessing revenue trends:', e);
      return fallback;
    }
  };

  const getZeroFilledTrendData = (): RevenueTrendPoint[] => {
    if (!startDate || !endDate) return [];

    const rawData = safeGetRevenueTrends('daily.data', []) as RevenueTrendPoint[];

    const parseApiDateToUtc = (value: string): Date | null => {
      if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        const [y, m, d] = value.split('-').map(Number);
        if (!Number.isFinite(y) || !Number.isFinite(m) || !Number.isFinite(d)) return null;
        return new Date(Date.UTC(y, m - 1, d));
      }
      const parsed = new Date(value);
      if (!Number.isFinite(parsed.getTime())) return null;
      return new Date(Date.UTC(parsed.getUTCFullYear(), parsed.getUTCMonth(), parsed.getUTCDate()));
    };

    let start = parseApiDateToUtc(startDate);
    let end = parseApiDateToUtc(endDate);
    if (!start || !end) return rawData || [];
    if (end.getTime() < start.getTime()) {
      const tmp = start;
      start = end;
      end = tmp;
    }

    const diffDays = Math.floor((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)) + 1;
    if (!Number.isFinite(diffDays) || diffDays < 1) return rawData || [];
    const bucketType: 'hourly' | 'daily' = diffDays <= 2 ? 'hourly' : 'daily';

    const expectedBuckets: string[] = [];
    if (bucketType === 'hourly') {
      for (let dayIndex = 0; dayIndex < diffDays; dayIndex++) {
        const day = new Date(start.getTime() + dayIndex * 24 * 60 * 60 * 1000);
        const ymd = day.toISOString().slice(0, 10);
        for (let hour = 0; hour < 24; hour++) {
          expectedBuckets.push(`${ymd} ${String(hour).padStart(2, '0')}:00`);
        }
      }
    } else {
      for (let dayIndex = 0; dayIndex < diffDays; dayIndex++) {
        const day = new Date(start.getTime() + dayIndex * 24 * 60 * 60 * 1000);
        expectedBuckets.push(day.toISOString().slice(0, 10));
      }
    }

    const lookup = new Map<string, RevenueTrendPoint>();
    for (const p of rawData || []) {
      if (p?.date) lookup.set(p.date, p);
    }

    return expectedBuckets.map((bucket) => {
      const existing = lookup.get(bucket);
      if (existing) return existing;
      return {
        period: bucket,
        date: bucket,
        revenue: 0,
        orders: 0,
        customers: 0,
        avg_order_value: 0,
        revenue_growth: 0,
        orders_growth: 0,
        customers_growth: 0,
        target_revenue: 0,
        target_achieved: 0
      };
    });
  };

  const formatINR = (amount: number) => {
    if (!Number.isFinite(amount)) return '₹0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const getGrowthIcon = (value: number) => {
    if (value > 0) return <ArrowUp className="h-4 w-4 text-green-600" />;
    if (value < 0) return <ArrowDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const getGrowthColor = (value: number) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getSuggestionBadge = (suggestion: string) => {
    const colors = {
      promote: 'bg-green-100 text-green-800',
      maintain: 'bg-blue-100 text-blue-800',
      optimize: 'bg-yellow-100 text-yellow-800',
      improve: 'bg-orange-100 text-orange-800',
      remove: 'bg-red-100 text-red-800'
    };
    return colors[suggestion as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const KPICard: React.FC<{
    title: string;
    value: string;
    growth: number;
    icon: React.ReactNode;
    subtitle: string;
  }> = ({ title, value, growth, icon, subtitle }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            <div className="flex items-center space-x-1 mt-1">
              {getGrowthIcon(growth)}
              <span className={`text-sm font-medium ${getGrowthColor(growth)}`}>
                {formatPercent(growth)}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          </div>
          <div className="p-3 bg-blue-50 rounded-full">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
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
          <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
          <p className="text-gray-600">Historical and real-time business insights</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline">
            Last updated: {formatISTTime(new Date(analyticsData.last_updated))}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowDateRange(!showDateRange)}
          >
            <Calendar className="h-4 w-4 mr-2" />
            Date Range
          </Button>
          <Button variant="outline" size="sm" onClick={fetchAnalyticsData}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Date Range Picker */}
      {showDateRange && (
        <DateRangePicker
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onApply={() => {
            setShowDateRange(false);
            fetchAnalyticsData();
          }}
        />
      )}

      {/* KPI Metrics */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Key Performance Indicators</h2>

        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              title="Total Revenue"
              value={formatINR(safeGetKpiValue('current_period.revenue'))}
              growth={safeGetKpiValue('current_period.revenue_growth')}
              icon={<DollarSign className="h-6 w-6 text-blue-600" />}
              subtitle="vs previous period"
            />
            <KPICard
              title="Orders"
              value={safeGetKpiValue('current_period.orders')?.toString() || '0'}
              growth={safeGetKpiValue('current_period.orders_growth')}
              icon={<ShoppingCart className="h-6 w-6 text-green-600" />}
              subtitle="vs previous period"
            />
            <KPICard
              title="Avg Order Value"
              value={formatINR(safeGetKpiValue('current_period.avg_order_value'))}
              growth={safeGetKpiValue('current_period.avg_order_growth')}
              icon={<Target className="h-6 w-6 text-purple-600" />}
              subtitle="vs previous period"
            />
            <KPICard
              title="Customers"
              value={safeGetKpiValue('current_period.unique_customers')?.toString() || '0'}
              growth={safeGetKpiValue('current_period.customers_growth')}
              icon={<Users className="h-6 w-6 text-orange-600" />}
              subtitle="vs previous period"
            />
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Analytics Trends</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <EnhancedAnalyticsChart
            title="Revenue Trends"
            data={getZeroFilledTrendData()}
            type="revenue"
            color="#3b82f6"
            height={350}
          />
          <EnhancedAnalyticsChart
            title="Order Trends"
            data={getZeroFilledTrendData()}
            type="orders"
            color="#10b981"
            height={350}
          />
          <EnhancedAnalyticsChart
            title="Customer Trends"
            data={getZeroFilledTrendData()}
            type="customers"
            color="#f59e0b"
            height={350}
          />
          <EnhancedAnalyticsChart
            title="Average Order Value"
            data={getZeroFilledTrendData()}
            type="avg_order_value"
            color="#8b5cf6"
            height={350}
          />
        </div>
      </div>

      {/* Revenue by Time Slot */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Revenue by Time Slot</h2>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Time Slot Analysis - {analyticsData.revenue_by_time_slot?.date || 'Today'}</CardTitle>
              <div className="text-sm text-gray-600">
                Total Revenue: {formatINR(analyticsData.revenue_by_time_slot?.total_revenue || 0)} |
                Orders: {analyticsData.revenue_by_time_slot?.total_orders || 0}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {Object.entries(analyticsData.revenue_by_time_slot?.time_slots || {}).map(([slot, data]) => {
                const displaySlot = slot === 'LateNight' ? 'Late Night' : slot;
                return (
                  <Card key={slot} className="border-l-4 border-l-blue-500">
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-lg">{displaySlot}</h3>
                      <p className="text-2xl font-bold text-blue-600">{formatINR(data.revenue || 0)}</p>
                      <p className="text-sm text-gray-600">{data.orders || 0} orders</p>
                      <p className="text-sm font-medium">{(data.percentage || 0).toFixed(1)}% of total</p>
                      {data.items && data.items.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500">Top item:</p>
                          <p className="text-sm font-medium truncate">{data.items[0].name}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Item Performance */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Item Performance Analysis</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Selling Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Top Selling Items
              </CardTitle>
              <p className="text-sm text-gray-600">{analyticsData.item_performance?.period || 'Last 30 days'}</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {(analyticsData.item_performance?.top_selling || []).slice(0, 5).map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-semibold">{item.name}</h4>
                      <p className="text-sm text-gray-600">{item.category}</p>
                      <p className="text-sm">{item.total_orders} orders • {item.total_quantity} units</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{formatINR(item.total_revenue)}</p>
                      <Badge className={getSuggestionBadge(item.suggestion)}>
                        {item.suggestion}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Low Selling Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingDown className="h-5 w-5 mr-2 text-red-600" />
                Low Selling Items
              </CardTitle>
              <p className="text-sm text-gray-600">{analyticsData.item_performance?.period || 'Last 30 days'}</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {(analyticsData.item_performance?.low_selling || []).slice(0, 5).map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-semibold">{item.name}</h4>
                      <p className="text-sm text-gray-600">{item.category}</p>
                      <p className="text-sm">{item.total_orders} orders • {item.total_quantity} units</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{formatINR(item.total_revenue)}</p>
                      <Badge className={getSuggestionBadge(item.suggestion)}>
                        {item.suggestion}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Revenue Trends */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Revenue Trends</h2>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Revenue Analysis</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Total Revenue</p>
                    <p className="text-xl font-bold">{formatINR(analyticsData.revenue_trends?.daily?.summary?.total_revenue || 0)}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Total Orders</p>
                    <p className="text-xl font-bold">{analyticsData.revenue_trends?.daily?.summary?.total_orders || 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Avg Revenue/Day</p>
                    <p className="text-xl font-bold">{formatINR(analyticsData.revenue_trends?.daily?.summary?.avg_revenue_per_period || 0)}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Growth Rate</p>
                    <p className="text-xl font-bold">{formatPercent(analyticsData.revenue_trends?.daily?.summary?.growth_rate || 0)}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Trend Data */}
              <div className="space-y-2">
                {/* Separate active days from zero days */}
                {(() => {
                  const trendData = analyticsData.revenue_trends?.daily?.data || [];
                  const activeDays = trendData.filter(trend => trend.orders > 0 || trend.revenue > 0);
                  const zeroDays = trendData.filter(trend => trend.orders === 0 && trend.revenue === 0);

                  return (
                    <>
                      {/* Active Days - Show prominently */}
                      {activeDays.length > 0 && (
                        <>
                          <div className="text-sm font-medium text-gray-700 mt-4 mb-2 flex items-center justify-between">
                            <span>📈 Active Days ({activeDays.length})</span>
                            <span className="text-xs text-gray-500 font-normal italic">
                              {formatISTDate(activeDays[0]?.period)} - {formatISTDate(activeDays[activeDays.length - 1]?.period)}
                            </span>
                          </div>
                          {activeDays.slice(-10).map((trend, index) => (
                            <div key={`active-${index}`} className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                              <div className="flex-1">
                                <h4 className="font-semibold text-green-800">{formatISTDate(trend.period)}</h4>
                                <p className="text-sm text-green-700">
                                  {trend.orders} orders • {trend.customers} customers
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="font-bold text-green-800">{formatINR(trend.revenue)}</p>
                                <div className="flex items-center space-x-2">
                                  <span className={`text-sm ${getGrowthColor(trend.revenue_growth)}`}>
                                    {formatPercent(trend.revenue_growth)}
                                  </span>
                                  <span className="text-sm text-gray-600">
                                    Target: {trend.target_achieved.toFixed(1)}%
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </>
                      )}

                      {/* Zero Days - Show collapsed by default */}
                      {zeroDays.length > 0 && (
                        <details className="mt-4">
                          <summary className="cursor-pointer text-sm font-medium text-gray-500 hover:text-gray-700 mb-2 flex items-center justify-between">
                            <span>📊 Inactive Days ({zeroDays.length}) - Click to expand</span>
                            {zeroDays.length > 0 && (
                              <span className="text-xs font-normal italic">
                                {formatISTDate(zeroDays[0]?.period)} - {formatISTDate(zeroDays[zeroDays.length - 1]?.period)}
                              </span>
                            )}
                          </summary>
                          <div className="space-y-1 mt-2">
                            {zeroDays.slice(-10).map((trend, index) => (
                              <div key={`zero-${index}`} className="flex items-center justify-between p-2 bg-gray-50 rounded opacity-60">
                                <div className="flex-1">
                                  <h4 className="font-medium text-gray-600 text-sm">{formatISTDate(trend.period)}</h4>
                                  <p className="text-xs text-gray-500">
                                    No activity
                                  </p>
                                </div>
                                <div className="text-right">
                                  <p className="font-medium text-gray-500 text-sm">{formatINR(trend.revenue)}</p>
                                  <span className="text-xs text-gray-400">
                                    {formatPercent(trend.revenue_growth)}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </details>
                      )}

                      {/* No data message */}
                      {activeDays.length === 0 && zeroDays.length === 0 && (
                        <div className="text-center py-8 text-gray-500">
                          <p className="font-medium">No revenue data available</p>
                          <p className="text-sm">Try adjusting the date range</p>
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default HistoricalAnalyticsDashboard;
