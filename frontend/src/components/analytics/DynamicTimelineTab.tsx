import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  Clock,
  Target,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';
import { formatISTTime, getCurrentISTDateForAPI } from '@/utils/istTime';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';

interface HourlyData {
  hour: number;
  time: string;
  actual_orders: number;
  predicted_orders: number;
  confidence: number;
  is_past: boolean;
  is_current: boolean;
  is_future: boolean;
  risk_level: 'low' | 'medium' | 'high';
  factors: string[];
}

interface DynamicTimelineTabProps {
  dateOption: string;
  onRefresh?: () => void;
}

const DynamicTimelineTab: React.FC<DynamicTimelineTabProps> = ({ dateOption, onRefresh }) => {
  const [timelineData, setTimelineData] = useState<HourlyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Helper function to get current IST hour
  const getCurrentISTHour = (): number => {
    const now = new Date();
    // Use the same logic as formatISTTime utility
    const utcTime = now.getTime();
    const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
    const istNow = new Date(utcTime + istOffset);
    return istNow.getUTCHours(); // Use getUTCHours() after offset to avoid timezone issues
  };

  // Fetch real hourly data from database
  const fetchHourlyData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Calculate target date based on dateOption
      let targetDate = getCurrentISTDateForAPI();
      const isTomorrow = dateOption === 'tomorrow';

      if (isTomorrow) {
        const now = new Date();
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        // Correctly handle IST for tomorrow
        const utcTime = tomorrow.getTime();
        const istOffset = 5.5 * 60 * 60 * 1000;
        const istTomorrow = new Date(utcTime + istOffset);

        const year = istTomorrow.getUTCFullYear();
        const month = String(istTomorrow.getUTCMonth() + 1).padStart(2, '0');
        const day = String(istTomorrow.getUTCDate()).padStart(2, '0');
        targetDate = `${year}-${month}-${day}`;
      }

      console.log(`🕐 Time Debug - Local: ${new Date().toISOString()}, Option: ${dateOption}, Target Date: ${targetDate}`);
      console.log(`🕐 Fetching hourly data for date: ${targetDate}`);

      // Fetch today's completed orders using the new working endpoint
      console.log('🔍 Starting direct database orders fetch...');

      // Use the new analytics orders endpoint that works correctly
      const todayIST = getCurrentISTDateForAPI();
      console.log('🔍 Today IST date for direct query:', todayIST);

      const ordersResponse = await fetch(`${API_URL}/api/analytics/orders-by-date?date=${todayIST}&status=completed`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      let ordersData = [];
      if (ordersResponse.ok) {
        const response = await ordersResponse.json();
        ordersData = response.orders || [];
        console.log('📊 Direct completed orders response:', response);
        console.log('📊 Number of completed orders fetched:', ordersData.length);
        console.log('📊 Orders with IST times:', ordersData.map(o => ({ id: o.id, created_at: o.created_at, created_at_ist: o.created_at_ist })));
      } else {
        console.error('❌ Failed to fetch orders:', ordersResponse.status);
        const errorText = await ordersResponse.text();
        console.error('❌ Error response:', errorText);
      }

      // Fetch analytics data for predictions
      const analyticsResponse = await fetch(`${API_URL}/api/analytics/dashboard?start_date=${targetDate}&end_date=${targetDate}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      let analyticsData = null;
      if (analyticsResponse.ok) {
        analyticsData = await analyticsResponse.json();
        console.log('📈 Analytics data:', analyticsData);
      }

      // Fetch historical data for better predictions
      const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
      const yesterdayStr = yesterday.toISOString().split('T')[0];

      const historicalResponse = await fetch(`${API_URL}/api/analytics/dashboard?start_date=${yesterdayStr}&end_date=${yesterdayStr}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      let historicalData = null;
      if (historicalResponse.ok) {
        historicalData = await historicalResponse.json();
        console.log('📚 Historical data:', historicalData);
      }

      // Process the data into hourly timeline
      const timeline = processHourlyData(ordersData, analyticsData, historicalData);
      setTimelineData(timeline);

    } catch (error) {
      console.error('Error fetching hourly data:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  // Process actual completed orders into hourly timeline
  const processHourlyData = (
    orders: any[],
    analytics: any,
    historical: any
  ): HourlyData[] => {
    const currentHour = getCurrentISTHour();
    const timeline: HourlyData[] = [];

    console.log('🔍 Processing actual completed orders from database...');
    console.log('📊 Number of completed orders to process:', orders.length);

    // Create hourly breakdown from actual orders
    const hourlyOrders: { [hour: number]: number } = {};

    orders.forEach((order, index) => {
      try {
        console.log(`🔍 Processing completed order ${index + 1}/${orders.length}:`, order);

        // Use the IST time provided by the backend (already converted correctly)
        const istTimeString = order.created_at_ist ? formatISTTime(order.created_at_ist) : formatISTTime(order.created_at);
        console.log(`🔍 Order ${order.id} IST time: ${istTimeString}`);

        // Extract hour from the formatted IST time
        // formatISTTime returns format like "12:28 AM"
        const timeMatch = istTimeString.match(/(\d+):(\d+)\s*(AM|PM)/);
        if (timeMatch) {
          let hour = parseInt(timeMatch[1]);
          const ampm = timeMatch[3];

          // Convert 12-hour format to 24-hour format
          if (ampm === 'PM' && hour !== 12) {
            hour += 12;
          } else if (ampm === 'AM' && hour === 12) {
            hour = 0;
          }

          console.log(`🕐 Order ${order.id} Time Debug - Original: ${order.created_at}, IST: ${order.created_at_ist}, Formatted: ${istTimeString}, Hour: ${hour}`);

          // This should correctly identify 12:xx AM as hour 0
          if (hour === 0) {
            console.log(`✅ Order ${order.id} correctly identified as 12:00 AM slot (LateNight)`);
          } else if (hour === 1) {
            console.log(`✅ Order ${order.id} correctly identified as 1:00 AM slot (LateNight)`);
          }

          hourlyOrders[hour] = (hourlyOrders[hour] || 0) + 1;
          console.log(`🕐 Updated hourlyOrders[${hour}] = ${hourlyOrders[hour]}`);
        } else {
          console.error(`⚠️ Could not parse time from: ${istTimeString} for order ${order.id}`);
        }
      } catch (error) {
        console.error(`❌ Error processing order ${order.id}:`, error);
      }
    });

    console.log('🕐 Final hourly order breakdown from actual orders:', hourlyOrders);
    console.log('🕐 Hourly breakdown details:', Object.entries(hourlyOrders).map(([hour, count]) => `${hour}:00 - ${count} orders`));

    // Check specifically for the 12:00 AM slot (hour 0)
    const midnightOrders = hourlyOrders[0] || 0;
    console.log(`🎯 IMPORTANT: 12:00 AM slot (hour 0) has ${midnightOrders} orders`);

    if (midnightOrders > 0) {
      console.log(`✅ SUCCESS: Found ${midnightOrders} orders in 12:00 AM slot as expected!`);
    } else {
      console.log(`❌ ISSUE: No orders found in 12:00 AM slot, but database shows 3 orders`);
    }

    // Calculate base metrics for predictions
    const totalTodayOrders = Object.values(hourlyOrders).reduce((sum, count) => sum + count, 0);
    const totalYesterdayOrders = historical?.kpi_metrics?.current_period?.orders || 0;
    const avgHourlyRate = totalTodayOrders / Math.max(1, currentHour + 1); // +1 because current hour is included

    console.log(`📊 Metrics - Today: ${totalTodayOrders}, Yesterday: ${totalYesterdayOrders}, Avg Rate: ${avgHourlyRate.toFixed(2)}/hour`);

    // Create IST date object for timeline generation
    const now = new Date();
    const utcTime = now.getTime();
    const istOffset = 5.5 * 60 * 60 * 1000;
    const currentIST = new Date(utcTime + istOffset);
    if (dateOption === 'tomorrow') {
      currentIST.setDate(currentIST.getDate() + 1);
    }

    const isToday = dateOption === 'today';

    // Generate timeline window
    if (isToday) {
      // Past 2 hours
      for (let i = 2; i >= 1; i--) {
        const pastHour = (currentHour - i + 24) % 24;
        const actualOrders = hourlyOrders[pastHour] || 0;
        const time = formatISTTime(new Date(currentIST.getFullYear(), currentIST.getMonth(), currentIST.getDate(), pastHour, 0, 0, 0));

        timeline.push({
          hour: pastHour,
          time,
          actual_orders: actualOrders,
          predicted_orders: actualOrders,
          confidence: 0.95,
          is_past: true,
          is_current: false,
          is_future: false,
          risk_level: actualOrders > 0 ? 'low' : 'medium',
          factors: ['Historical database record', 'Actual orders']
        });
      }

      // Current hour
      const currentActualOrders = hourlyOrders[currentHour] || 0;
      const currentTime = formatISTTime(new Date(currentIST.getFullYear(), currentIST.getMonth(), currentIST.getDate(), currentHour, 0, 0, 0));

      timeline.push({
        hour: currentHour,
        time: currentTime,
        actual_orders: currentActualOrders,
        predicted_orders: currentActualOrders,
        confidence: 0.95,
        is_past: false,
        is_current: true,
        is_future: false,
        risk_level: 'low',
        factors: ['Live database tracking', 'Current hour data']
      });

      // Future 4 hours
      for (let i = 1; i <= 4; i++) {
        const futureHour = (currentHour + i) % 24;
        const predictedDemand = predictOrdersForHour(futureHour, currentHour, totalTodayOrders, avgHourlyRate, hourlyOrders);
        const time = formatISTTime(new Date(currentIST.getFullYear(), currentIST.getMonth(), currentIST.getDate(), futureHour, 0, 0, 0));

        timeline.push({
          hour: futureHour,
          time,
          actual_orders: 0,
          predicted_orders: predictedDemand,
          confidence: Math.max(0.5, 0.9 - (i * 0.1)),
          is_past: false,
          is_current: false,
          is_future: true,
          risk_level: predictedDemand > avgHourlyRate * 1.5 ? 'high' : 'medium',
          factors: ['DB-driven scaling', 'Trend-based prediction']
        });
      }
    } else {
      // Tomorrow: Show representative busy hours (8am - 10pm)
      const tomorrowHours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22];
      tomorrowHours.forEach(hour => {
        // Use a baseline from yesterday if available, or today
        const baseline = totalYesterdayOrders > 0 ? totalYesterdayOrders / 12 : totalTodayOrders / 12 || 5;
        const predictedDemand = predictOrdersForHour(hour, 0, baseline * 12, baseline, {});
        const time = formatISTTime(new Date(currentIST.getFullYear(), currentIST.getMonth(), currentIST.getDate(), hour, 0, 0, 0));

        timeline.push({
          hour: hour,
          time,
          actual_orders: 0,
          predicted_orders: predictedDemand,
          confidence: 0.7,
          is_past: false,
          is_current: false,
          is_future: true,
          risk_level: predictedDemand > baseline * 1.5 ? 'high' : 'low',
          factors: ['Historical pattern scaling', 'Next-day forecast']
        });
      });
    }

    console.log('📊 Generated timeline:', timeline);
    return timeline;
  };

  // Advanced prediction system for production-scale order volumes
  const predictOrdersForHour = (
    hour: number,
    currentHour: number,
    totalTodayOrders: number,
    avgHourlyRate: number,
    hourlyOrders: { [hour: number]: number }
  ): number => {
    // 1. Calculate base rate
    const activeHours = Object.keys(hourlyOrders).length || 1;
    const baseRate = Math.max(2.5, totalTodayOrders / Math.max(1, activeHours));

    // 2. Time-based demand patterns (Production-scale multipliers)
    const demandPatterns = {
      earlyMorning: { hours: [2, 3, 4, 5], multiplier: 0.2, confidence: 0.4 },
      preBreakfast: { hours: [6, 7], multiplier: 0.8, confidence: 0.5 },
      breakfast: { hours: [8, 9, 10], multiplier: 4.2, confidence: 0.8 },
      midMorning: { hours: [11], multiplier: 2.8, confidence: 0.7 },
      lunch: { hours: [12, 13, 14], multiplier: 6.5, confidence: 0.9 },
      afternoonLull: { hours: [15, 16], multiplier: 2.2, confidence: 0.6 },
      eveningSnacks: { hours: [17, 18], multiplier: 3.5, confidence: 0.7 },
      dinner: { hours: [19, 20, 21], multiplier: 5.2, confidence: 0.8 },
      lateNight: { hours: [22, 23], multiplier: 2.5, confidence: 0.6 },
      midnight: { hours: [0, 1], multiplier: 0.8, confidence: 0.5 }
    };

    // 3. Find the appropriate demand pattern
    let patternMultiplier = 1.0;
    let patternConfidence = 0.5;

    Object.values(demandPatterns).forEach(pattern => {
      if (pattern.hours.includes(hour)) {
        patternMultiplier = pattern.multiplier;
        patternConfidence = pattern.confidence;
      }
    });

    // 4. Production volume scaling
    let volumeScaler = 1.0;
    if (totalTodayOrders >= 100) {
      volumeScaler = 1.8;
    } else if (totalTodayOrders >= 50) {
      volumeScaler = 1.4;
    } else {
      volumeScaler = 1.15;
    }

    // 5. Pattern boost from same-day trends
    const similarHourData = hourlyOrders[hour] || 0;
    const patternBoost = similarHourData > 0 ? 1.6 : 1.1;

    // 6. Distance-based confidence
    let hoursFromNow = hour - currentHour;
    if (hoursFromNow < 0) hoursFromNow += 24;
    const distanceConfidence = Math.max(0.3, 1 - (hoursFromNow * 0.08));

    // 7. Calculate raw prediction
    const rawPrediction = baseRate * patternMultiplier * volumeScaler * patternBoost;

    // 8. Apply realistic production floors
    let finalPrediction = Math.round(rawPrediction);

    const minOrders = hour >= 12 && hour <= 14 ? 15 : // Lunch rush floor
      hour >= 19 && hour <= 21 ? 10 :  // Dinner rush floor
        hour >= 8 && hour <= 10 ? 8 :   // Breakfast floor
          2; // General production floor

    const maxOrders = Math.max(40, Math.round(totalTodayOrders * 0.7));

    finalPrediction = Math.max(minOrders, Math.min(maxOrders, finalPrediction));

    // 9. No more conservative capping for low volume

    console.log(`🔮 Prediction for ${hour}:00 - Final: ${finalPrediction}, BaseRate: ${baseRate.toFixed(2)}`);

    return Math.max(0, finalPrediction);
  };

  // Get risk level styling
  const getRiskStyling = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return {
          bg: 'bg-green-50',
          text: 'text-green-600',
          border: 'border-green-200',
          icon: <CheckCircle className="h-4 w-4 text-green-600" />
        };
      case 'medium':
        return {
          bg: 'bg-yellow-50',
          text: 'text-yellow-600',
          border: 'border-yellow-200',
          icon: <AlertCircle className="h-4 w-4 text-yellow-600" />
        };
      case 'high':
        return {
          bg: 'bg-red-50',
          text: 'text-red-600',
          border: 'border-red-200',
          icon: <AlertTriangle className="h-4 w-4 text-red-600" />
        };
      default:
        return {
          bg: 'bg-gray-50',
          text: 'text-gray-600',
          border: 'border-gray-200',
          icon: <Activity className="h-4 w-4 text-gray-600" />
        };
    }
  };

  // Handle refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchHourlyData();
    onRefresh?.();
  };

  useEffect(() => {
    fetchHourlyData();
  }, [dateOption]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Dynamic Order Timeline</h3>
          <Button variant="outline" size="sm" disabled>
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            Loading...
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(7)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4">
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Timeline</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Dynamic Order Timeline</h3>
          <p className="text-sm text-gray-600 flex items-center gap-2">
            Real-time order tracking with data-driven predictions
            <Badge variant="outline" className="text-[10px] font-normal border-blue-200 text-blue-600">
              BASED ON DB HISTORY
            </Badge>
          </p>
        </div>
        <Button
          onClick={handleRefresh}
          variant="outline"
          size="sm"
          disabled={isRefreshing}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Timeline Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {timelineData.map((hour, index) => {
          const riskStyle = getRiskStyling(hour.risk_level);
          const isCurrent = hour.is_current;

          return (
            <motion.div
              key={hour.hour}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className={`
                ${riskStyle.bg} ${riskStyle.border} border-2 
                ${isCurrent ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
                hover:shadow-lg transition-all duration-200
              `}>
                <CardContent className="p-4">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {riskStyle.icon}
                      <span className="font-semibold text-sm">{hour.time}</span>
                      {isCurrent && (
                        <Badge variant="default" className="text-xs">
                          CURRENT
                        </Badge>
                      )}
                    </div>
                    <Badge
                      variant="outline"
                      className={`${riskStyle.text} ${riskStyle.border} text-xs`}
                    >
                      {hour.risk_level.toUpperCase()}
                    </Badge>
                  </div>

                  {/* Orders Display */}
                  <div className="space-y-2">
                    {hour.is_past || hour.is_current ? (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">What Actually Happened</span>
                        <span className="font-bold text-lg">
                          {hour.actual_orders}
                          <span className="text-xs text-gray-500 ml-1">orders</span>
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">What We Expect</span>
                        <span className="font-bold text-lg">
                          {hour.predicted_orders}
                          <span className="text-xs text-gray-500 ml-1">orders</span>
                        </span>
                      </div>
                    )}

                    {/* Current hour special display */}
                    {hour.is_current && (
                      <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                        <span className="text-xs text-gray-600">So Far Today</span>
                        <span className="font-semibold text-blue-600">
                          {hour.actual_orders}
                          <span className="text-xs ml-1">orders</span>
                        </span>
                      </div>
                    )}

                    {/* Future hour prediction display */}
                    {hour.is_future && (
                      <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                        <span className="text-xs text-gray-600">Confidence</span>
                        <div className="flex items-center space-x-2">
                          <Progress value={hour.confidence * 100} className="w-16 h-2" />
                          <span className="text-xs font-medium">
                            {Math.round(hour.confidence * 100)}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Factors */}
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="text-xs text-gray-600 mb-1">Contributing Factors</div>
                    <div className="flex flex-wrap gap-1">
                      {hour.factors.slice(0, 2).map((factor, i) => (
                        <span
                          key={i}
                          className="text-xs bg-white px-2 py-1 rounded border border-gray-200"
                        >
                          {factor}
                        </span>
                      ))}
                      {hour.factors.length > 2 && (
                        <span className="text-xs text-gray-500">+{hour.factors.length - 2} more</span>
                      )}
                    </div>
                  </div>

                  {/* Status indicator */}
                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      {hour.actual_orders > 0 || hour.predicted_orders > 0 ? (
                        <>
                          <Activity className="h-3 w-3 text-green-600" />
                          <span className="text-xs text-green-600">
                            {hour.is_past || hour.is_current ? 'Orders served' : 'Orders expected'}
                          </span>
                        </>
                      ) : (
                        <>
                          <Minus className="h-3 w-3 text-gray-400" />
                          <span className="text-xs text-gray-400">
                            {hour.is_past || hour.is_current ? 'No orders' : 'Quiet period'}
                          </span>
                        </>
                      )}
                    </div>

                    {hour.is_future && (
                      <span className="text-xs text-gray-500">
                        {hour.predicted_orders} expected
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {timelineData.find(h => h.is_current)?.actual_orders || 0}
              </div>
              <div className="text-xs text-gray-600">Current Hour</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {timelineData.filter(h => h.is_past).reduce((sum, h) => sum + h.actual_orders, 0)}
              </div>
              <div className="text-xs text-gray-600">Already Served</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {timelineData.filter(h => h.is_future).reduce((sum, h) => sum + h.predicted_orders, 0)}
              </div>
              <div className="text-xs text-gray-600">Remaining Expected</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {Math.max(...timelineData.filter(h => h.is_future).map(h => h.predicted_orders), 0)}
              </div>
              <div className="text-xs text-gray-600">Peak Expected</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DynamicTimelineTab;
