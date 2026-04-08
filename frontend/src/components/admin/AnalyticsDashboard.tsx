import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  DollarSign,
  Clock,
  ShoppingCart,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  Calendar,
  Target,
  Star,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useOrders } from '@/contexts/OrderContext';

interface AnalyticsDashboardProps {
  className?: string;
}

interface KPIMetrics {
  totalOrders: number;
  totalRevenue: number;
  avgWaitTime: number;
  activeOrders: number;
  yesterdayOrders: number;
  yesterdayRevenue: number;
  yesterdayAvgWaitTime: number;
  ordersChange: number;
  revenueChange: number;
  waitTimeChange: number;
}

export default function AnalyticsDashboard({ className = "" }: AnalyticsDashboardProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [kpiMetrics, setKpiMetrics] = useState<KPIMetrics | null>(null);
  const { orders, fetchAllOrders } = useOrders();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-IN').format(num);
  };

  // Helper function to get date range for a specific day in IST
  const getDateRange = (date: Date) => {
    // Create a copy in IST timezone
    const istDate = new Date(date.toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
    
    // Get start of day (00:00:00 IST)
    const startOfDay = new Date(istDate);
    startOfDay.setHours(0, 0, 0, 0);
    
    // Get end of day (23:59:59 IST)
    const endOfDay = new Date(istDate);
    endOfDay.setHours(23, 59, 59, 999);
    
    return {
      start: startOfDay,
      end: endOfDay,
      startUTC: new Date(startOfDay.toUTCString()), // Convert to UTC for comparison
      endUTC: new Date(endOfDay.toUTCString())
    };
  };

  // Filter orders by date range
  const filterOrdersByDate = (orderList: any[], startDate: Date, endDate: Date) => {
    return orderList.filter(order => {
      const orderDate = new Date(order.createdAt);
      return orderDate >= startDate && orderDate <= endDate;
    });
  };

  // Calculate KPI metrics for a specific day
  const calculateDayMetrics = (orderList: any[], date: Date) => {
    const dateRange = getDateRange(date);
    const dayOrders = filterOrdersByDate(orderList, dateRange.startUTC, dateRange.endUTC);
    
    const totalOrders = dayOrders.length;
    const totalRevenue = dayOrders.reduce((sum, order) => sum + (order.totalPrice || 0), 0);
    
    // Calculate average wait time (from creation to ready or completion)
    const completedOrders = dayOrders.filter(order => 
      order.readyAt || order.completedAt
    );
    
    const avgWaitTime = completedOrders.length > 0 
      ? completedOrders.reduce((sum, order) => {
          const endTime = new Date(order.readyAt || order.completedAt);
          const startTime = new Date(order.createdAt);
          return sum + (endTime.getTime() - startTime.getTime()) / (1000 * 60); // Convert to minutes
        }, 0) / completedOrders.length
      : 0;
    
    const activeOrders = dayOrders.filter(order => 
      ['pending', 'preparing'].includes(order.status)
    ).length;
    
    return {
      totalOrders,
      totalRevenue,
      avgWaitTime: Math.round(avgWaitTime),
      activeOrders
    };
  };

  // Calculate KPI metrics
  const calculateKPIs = () => {
    try {
      const now = new Date();
      const today = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      // Get today's metrics
      const todayMetrics = calculateDayMetrics(orders, today);
      
      // Get yesterday's metrics
      const yesterdayMetrics = calculateDayMetrics(orders, yesterday);
      
      // Calculate percentage changes
      const ordersChange = yesterdayMetrics.totalOrders > 0 
        ? ((todayMetrics.totalOrders - yesterdayMetrics.totalOrders) / yesterdayMetrics.totalOrders) * 100 
        : 0;
      
      const revenueChange = yesterdayMetrics.totalRevenue > 0 
        ? ((todayMetrics.totalRevenue - yesterdayMetrics.totalRevenue) / yesterdayMetrics.totalRevenue) * 100 
        : 0;
      
      const waitTimeChange = yesterdayMetrics.avgWaitTime > 0 
        ? ((todayMetrics.avgWaitTime - yesterdayMetrics.avgWaitTime) / yesterdayMetrics.avgWaitTime) * 100 
        : 0;
      
      setKpiMetrics({
        ...todayMetrics,
        yesterdayOrders: yesterdayMetrics.totalOrders,
        yesterdayRevenue: yesterdayMetrics.totalRevenue,
        yesterdayAvgWaitTime: yesterdayMetrics.avgWaitTime,
        ordersChange,
        revenueChange,
        waitTimeChange
      });
      
    } catch (error) {
      console.error('Error calculating KPIs:', error);
      setError('Failed to calculate metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch all orders for comprehensive analysis
        await fetchAllOrders();
      } catch (error) {
        console.error('Error fetching orders:', error);
        setError('Failed to load order data');
        setLoading(false);
      }
    };
    
    loadDashboardData();
  }, []);

  // Calculate KPIs when orders are loaded
  useEffect(() => {
    if (orders.length > 0) {
      calculateKPIs();
    } else if (!loading) {
      // No orders available
      setKpiMetrics({
        totalOrders: 0,
        totalRevenue: 0,
        avgWaitTime: 0,
        activeOrders: 0,
        yesterdayOrders: 0,
        yesterdayRevenue: 0,
        yesterdayAvgWaitTime: 0,
        ordersChange: 0,
        revenueChange: 0,
        waitTimeChange: 0
      });
      setLoading(false);
    }
  }, [orders, loading]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!kpiMetrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <p>No data available</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            <span>Error loading analytics: {error}</span>
          </div>
          <Button onClick={() => setError(null)} className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h2>
          <p className="text-muted-foreground">
            Administrative Analytics (Business Dashboard)
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm">
            <Activity className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Revenue & Sales - Business Dashboard */}
      <div className="space-y-6">
        {/* Revenue Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-600">Total Revenue</p>
                    <p className="text-3xl font-bold text-green-900">
                      ₹12,450
                    </p>
                    <p className="text-xs text-green-700 mt-1">This month</p>
                  </div>
                  <div className="bg-green-200 p-3 rounded-full">
                    <DollarSign className="h-6 w-6 text-green-700" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm text-green-700">
                  <ArrowUp className="h-4 w-4 mr-1" />
                  +15.3% from last month
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-600">Average Order Value</p>
                    <p className="text-3xl font-bold text-blue-900">
                      ₹285
                    </p>
                    <p className="text-xs text-blue-700 mt-1">Per order</p>
                  </div>
                  <div className="bg-blue-200 p-3 rounded-full">
                    <Target className="h-6 w-6 text-blue-700" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm text-blue-700">
                  <ArrowUp className="h-4 w-4 mr-1" />
                  +8.2% increase
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-600">Daily Orders</p>
                    <p className="text-3xl font-bold text-purple-900">
                      47
                    </p>
                    <p className="text-xs text-purple-700 mt-1">Today</p>
                  </div>
                  <div className="bg-purple-200 p-3 rounded-full">
                    <ShoppingCart className="h-6 w-6 text-purple-700" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm text-purple-700">
                  <ArrowUp className="h-4 w-4 mr-1" />
                  +12 orders from yesterday
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-600">Weekly Revenue</p>
                    <p className="text-3xl font-bold text-orange-900">
                      ₹87,150
                    </p>
                    <p className="text-xs text-orange-700 mt-1">This week</p>
                  </div>
                  <div className="bg-orange-200 p-3 rounded-full">
                    <Calendar className="h-6 w-6 text-orange-700" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm text-orange-700">
                  <ArrowUp className="h-4 w-4 mr-1" />
                  On track to target
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Revenue by Time Slot */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="h-5 w-5 mr-2" />
                Revenue by Time Slot
              </div>
              <Badge variant="outline" className="text-xs">
                Today's Performance
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { time: "Breakfast", hours: "8AM - 11AM", revenue: "₹2,450", orders: 18, percentage: 19.7 },
                { time: "Lunch", hours: "11AM - 3PM", revenue: "₹6,820", orders: 42, percentage: 54.8 },
                { time: "Snacks", hours: "3PM - 6PM", revenue: "₹1,890", orders: 15, percentage: 15.2 },
                { time: "Dinner", hours: "6PM - 9PM", revenue: "₹1,290", orders: 8, percentage: 10.3 },
              ].map((slot, index) => (
                <motion.div
                  key={slot.time}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{slot.time}</h4>
                    <Badge variant={slot.percentage > 30 ? "default" : "secondary"}>
                      {slot.percentage}%
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-500 mb-2">{slot.hours}</p>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Revenue:</span>
                      <span className="font-medium">{slot.revenue}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Orders:</span>
                      <span className="font-medium">{slot.orders}</span>
                    </div>
                  </div>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${slot.percentage}%` }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top-Selling & Low-Selling Items */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top-Selling Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Star className="h-5 w-5 mr-2" />
                Top-Selling Items
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "Biryani Combo", orders: 156, revenue: "₹7,800", growth: "+12%" },
                  { name: "Thali Special", orders: 134, revenue: "₹6,030", growth: "+8%" },
                  { name: "Noodles & Manchurian", orders: 98, revenue: "₹2,940", growth: "+15%" },
                  { name: "South Indian Meals", orders: 87, revenue: "₹2,175", growth: "+5%" },
                  { name: "Chinese Rice", orders: 76, revenue: "₹1,520", growth: "+3%" },
                ].map((item, index) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium">{item.name}</h4>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        <span>{item.orders} orders</span>
                        <span className="mx-2">•</span>
                        <span>{item.revenue}</span>
                      </div>
                    </div>
                    <div className="flex items-center text-green-600 font-medium">
                      <ArrowUp className="h-4 w-4 mr-1" />
                      {item.growth}
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Low-Selling Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2" />
                Low-Selling Items
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "Pasta", orders: 12, revenue: "₹360", status: "Critical", action: "Consider removing" },
                  { name: "Sandwich", orders: 18, revenue: "₹540", status: "Low", action: "Promote more" },
                  { name: "Salad", orders: 22, revenue: "₹660", status: "Low", action: "Add to combos" },
                  { name: "Soup", orders: 25, revenue: "₹500", status: "Medium", action: "Improve recipe" },
                  { name: "Juice", orders: 28, revenue: "₹840", status: "Medium", action: "Better placement" },
                ].map((item, index) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h4 className="font-medium">{item.name}</h4>
                        <Badge 
                          variant={item.status === "Critical" ? "destructive" : item.status === "Low" ? "default" : "secondary"}
                          className="ml-2"
                        >
                          {item.status}
                        </Badge>
                      </div>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        <span>{item.orders} orders</span>
                        <span className="mx-2">•</span>
                        <span>{item.revenue}</span>
                      </div>
                      <p className="text-xs text-blue-600 mt-1">{item.action}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Revenue Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Revenue Trends
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">Daily</Button>
                <Button variant="outline" size="sm">Weekly</Button>
                <Button variant="default" size="sm">Monthly</Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="text-3xl font-bold text-green-900">+18.5%</div>
                <p className="text-sm text-green-700 mt-2">Monthly Growth</p>
                <p className="text-xs text-green-600 mt-1">Compared to last month</p>
              </div>
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <div className="text-3xl font-bold text-blue-900">₹3.2L</div>
                <p className="text-sm text-blue-700 mt-2">Monthly Target</p>
                <p className="text-xs text-blue-600 mt-1">78% achieved</p>
              </div>
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <div className="text-3xl font-bold text-purple-900">92%</div>
                <p className="text-sm text-purple-700 mt-2">Customer Satisfaction</p>
                <p className="text-xs text-purple-600 mt-1">Based on feedback</p>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-3">Revenue Insights</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Lunch hours generate 55% of daily revenue</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm">Weekend revenue 35% higher than weekdays</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-sm">Combo meals increase order value by 25%</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="text-sm">Peak hour: 12:30 PM - 1:30 PM</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
