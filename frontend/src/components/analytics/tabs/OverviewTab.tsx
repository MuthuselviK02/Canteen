import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  Target,
  Brain,
  AlertTriangle,
  CheckCircle,
  Clock,
  Info,
  ArrowUp,
  ArrowDown,
  Minus,
  RefreshCw
} from 'lucide-react';
import { formatISTTime, formatISTDate, formatLocalTimeAsIST } from '@/utils/istTime';

interface KPIMetrics {
  average_daily_demand: number;
  highest_daily_demand: number;
  lowest_daily_demand: number;
  forecast_period: string;
  accuracy: number | null;
  total_items_analyzed: number;
  confidence_score: number;
}

interface GlobalFilters {
  dateOption: string;
  forecastType: string;
  foodCategory: string;
  sortBy: string;
}

interface OverviewTabProps {
  kpis: KPIMetrics;
  isReadOnly: boolean;
  globalFilters: GlobalFilters;
  isRefreshing: boolean;
  lastUpdated: Date;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ kpis, isReadOnly, globalFilters, isRefreshing, lastUpdated }) => {
  // Generate context string for cards
  const getContextString = useMemo(() => {
    const parts = [];
    const forecastTypeLabel = globalFilters.forecastType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    parts.push(forecastTypeLabel);
    
    if (globalFilters.foodCategory !== 'all') {
      parts.push(globalFilters.foodCategory);
    }
    
    const dateLabel = globalFilters.dateOption.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    parts.push(dateLabel);
    
    return parts.join(' · ');
  }, [globalFilters]);

  // Calculate demand range and trend based on global filters
  const demandRange = useMemo(() => {
    const min = kpis.lowest_daily_demand || 0;
    const max = kpis.highest_daily_demand || 0;
    const expected = kpis.average_daily_demand || 0;
    const variance = max - min;
    const isFlatRange = variance === 0;
    
    return {
      min,
      max,
      expected,
      variance,
      isFlatRange,
      variancePercent: expected > 0 ? (variance / expected) * 100 : 0
    };
  }, [kpis]);

  // Adjust expected demand based on forecast type
  const getExpectedDemand = () => {
    return Math.round(demandRange.expected);
  };

  // Determine demand trend with proper computation
  const demandTrend = useMemo(() => {
    const variancePercent = demandRange.variancePercent;
    
    if (variancePercent < 10) {
      return { label: 'Stable', icon: Minus, color: 'text-blue-600', bg: 'bg-blue-50' };
    }
    if (kpis.highest_daily_demand > kpis.average_daily_demand * 1.2) {
      return { label: 'Increasing', icon: ArrowUp, color: 'text-green-600', bg: 'bg-green-50' };
    }
    return { label: 'Decreasing', icon: ArrowDown, color: 'text-orange-600', bg: 'bg-orange-50' };
  }, [kpis, demandRange.variancePercent]);

  // Get confidence level interpretation with validation
  const confidenceLevel = useMemo(() => {
    const score = Math.max(0, Math.min(1, kpis.confidence_score || 0));
    if (score >= 0.8) return { label: 'High', color: 'text-green-600', badge: 'default' };
    if (score >= 0.6) return { label: 'Medium', color: 'text-yellow-600', badge: 'secondary' };
    return { label: 'Low', color: 'text-red-600', badge: 'destructive' };
  }, [kpis.confidence_score]);

  // Generate AI Insight based on global filters context
  const aiInsight = useMemo(() => {
    const { dateOption, forecastType, foodCategory } = globalFilters;
    const forecastTypeLabel = forecastType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    
    // Dynamic insight generation based on context
    if (demandTrend.label === 'Stable') {
      const categoryContext = foodCategory !== 'all' ? `${foodCategory} demand` : 'Overall demand';
      return {
        icon: CheckCircle,
        color: 'text-green-600',
        bg: 'bg-green-50',
        border: 'border-green-200',
        message: `${categoryContext} is stable for ${forecastTypeLabel.toLowerCase()}. No unusual spikes detected across ${kpis.total_items_analyzed} items.`,
        action: 'Maintain current inventory levels.'
      };
    }
    
    if (demandTrend.label === 'Increasing' && (kpis.confidence_score || 0) > 0.7) {
      const categoryContext = foodCategory !== 'all' ? `${foodCategory} demand` : 'Overall demand';
      return {
        icon: AlertTriangle,
        color: 'text-orange-600',
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        message: `⚠️ ${categoryContext} spike expected for ${forecastTypeLabel.toLowerCase()}. ${getExpectedDemand().toLocaleString()} units forecasted.`,
        action: 'Prepare additional stock for peak demand.'
      };
    }
    
    // High demand spike for specific time periods
    if (forecastType === 'peak_hour_demand' && demandTrend.label === 'Increasing') {
      return {
        icon: AlertTriangle,
        color: 'text-red-600',
        bg: 'bg-red-50',
        border: 'border-red-200',
        message: `High demand spike expected between 7–9 PM for ${forecastTypeLabel.toLowerCase()}. Analyzing ${kpis.total_items_analyzed} items.`,
        action: 'Schedule additional staff for peak hours.'
      };
    }
    
    // Category-specific insights
    if (foodCategory !== 'all' && forecastType === 'category_level_demand') {
      return {
        icon: Info,
        color: 'text-blue-600',
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        message: `${foodCategory} category analysis shows ${demandTrend.label.toLowerCase()} trend for ${forecastTypeLabel.toLowerCase()}. ${kpis.total_items_analyzed} items analyzed.`,
        action: demandTrend.label === 'Increasing' ? 'Monitor stock levels closely' : 'Continue current inventory strategy'
      };
    }
    
    // Default insight with context
    return {
      icon: Info,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      message: `Demand patterns show normal variation for ${forecastTypeLabel.toLowerCase()}. ${kpis.total_items_analyzed} items analyzed with ${demandTrend.label.toLowerCase()} trend.`,
      action: 'Monitor trends throughout the day.'
    };
  }, [globalFilters, demandTrend, kpis, getExpectedDemand]);
  
  const InsightIcon = aiInsight.icon;
  const TrendIcon = demandTrend.icon;

  // Get forecast window text
  const getForecastWindow = () => {
    const today = new Date();
    switch (kpis.forecast_period) {
      case 'today':
        return `Today (00:00 – 23:59 IST)`;
      case 'tomorrow':
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        return `Tomorrow (${formatISTDate(tomorrow)})`;
      case 'this_week':
        return `This Week (${formatISTDate(today)} - ${formatISTDate(new Date(today.getTime() + 6 * 24 * 60 * 60 * 1000))})`;
      case 'last_week':
        return `Last Week`;
      case 'last_30_days':
        return `Last 30 Days`;
      default:
        return kpis.forecast_period;
    }
  };

  // Get recommended usage with dynamic logic
  const recommendedUsage = useMemo(() => {
    const score = Math.max(0, Math.min(1, kpis.confidence_score || 0));
    if (score >= 0.8) return 'Operational planning';
    if (score >= 0.6) return 'Advisory only';
    return 'Use with caution';
  }, [kpis.confidence_score]);

  // Get data freshness based on last update
  const dataFreshness = useMemo(() => {
    const hoursSinceUpdate = (new Date().getTime() - lastUpdated.getTime()) / (1000 * 60 * 60);
    if (hoursSinceUpdate < 1) {
      return { label: 'Fresh', explanation: 'Updated within the last hour', variant: 'default' as const };
    }
    if (hoursSinceUpdate < 24) {
      return { label: 'Recent', explanation: `Updated ${Math.floor(hoursSinceUpdate)} hours ago`, variant: 'secondary' as const };
    }
    return { label: 'Stale', explanation: `Updated ${Math.floor(hoursSinceUpdate / 24)} days ago`, variant: 'destructive' as const };
  }, [lastUpdated]);

  // Get prediction quality based on confidence and data volume
  const predictionQuality = useMemo(() => {
    const score = Math.max(0, Math.min(1, kpis.confidence_score || 0));
    const itemCount = kpis.total_items_analyzed || 0;
    
    if (score >= 0.8 && itemCount > 50) {
      return { label: 'High', explanation: 'Strong patterns with sufficient data', variant: 'default' as const };
    }
    if (score >= 0.6 && itemCount > 20) {
      return { label: 'Medium', explanation: 'Moderate confidence with adequate data', variant: 'secondary' as const };
    }
    return { label: 'Low', explanation: 'Limited data or weak patterns', variant: 'destructive' as const };
  }, [kpis.confidence_score, kpis.total_items_analyzed]);

  return (
    <div className="space-y-6">
      {/* 1) DEMAND SNAPSHOT (PRIMARY KPI SECTION) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-600" />
              Demand Snapshot
              {isRefreshing && <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />}
            </CardTitle>
            <p className="text-sm text-gray-500">{getContextString}</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-2">Expected Demand</p>
                {isRefreshing ? (
                  <Skeleton className="h-8 w-20 mx-auto mb-2" />
                ) : (
                  <p className="text-3xl font-bold text-blue-600">
                    {getExpectedDemand().toLocaleString()}
                  </p>
                )}
                <p className="text-xs text-gray-500">Units for {kpis.forecast_period}</p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-2">Demand Range</p>
                {isRefreshing ? (
                  <Skeleton className="h-7 w-16 mx-auto mb-2" />
                ) : (
                  <>
                    <p className="text-2xl font-semibold text-gray-700">
                      {Math.round(demandRange.min)} – {Math.round(demandRange.max)}
                    </p>
                    {demandRange.isFlatRange && (
                      <p className="text-xs text-orange-600">Low variance detected</p>
                    )}
                  </>
                )}
                <p className="text-xs text-gray-500">Min – Max units</p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-2">Demand Trend</p>
                {isRefreshing ? (
                  <Skeleton className="h-6 w-16 mx-auto mb-2" />
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <div className={`p-2 ${demandTrend.bg} rounded-full`}>
                      <TrendIcon className={`h-5 w-5 ${demandTrend.color}`} />
                    </div>
                    <span className={`text-lg font-semibold ${demandTrend.color}`}>
                      {demandTrend.label}
                    </span>
                  </div>
                )}
                <p className="text-xs text-gray-500">Pattern analysis</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 2) FORECAST CONFIDENCE (TRUST INDICATOR) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-indigo-600" />
              Forecast Confidence
              {isRefreshing && <RefreshCw className="h-4 w-4 animate-spin text-indigo-500" />}
            </CardTitle>
            <p className="text-sm text-gray-500">{getContextString}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Confidence Score</p>
              <div className="flex items-center justify-center gap-3">
                {isRefreshing ? (
                  <Skeleton className="h-2 w-24 rounded-full" />
                ) : (
                  <Progress value={Math.max(0, Math.min(100, (kpis.confidence_score || 0) * 100))} className="w-24" />
                )}
                {isRefreshing ? (
                  <Skeleton className="h-6 w-10" />
                ) : (
                  <span className={`text-2xl font-bold ${confidenceLevel.color}`}>
                    {Math.max(0, Math.min(100, (kpis.confidence_score || 0) * 100)).toFixed(0)}%
                  </span>
                )}
              </div>
              {isRefreshing ? (
                <Skeleton className="h-5 w-16 mx-auto mt-2" />
              ) : (
                <Badge variant={confidenceLevel.badge as any} className="mt-2">
                  {confidenceLevel.label}
                </Badge>
              )}
            </div>
            
            <div className="border-t pt-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Accuracy</span>
                <span className="font-semibold">
                  {isReadOnly && kpis.accuracy !== null 
                    ? `${kpis.accuracy.toFixed(1)}%` 
                    : 'N/A'
                  }
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {isReadOnly ? 'Historical accuracy' : 'Future forecast - not yet measurable'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 3) AI INSIGHT CARD (MANDATORY) */}
      <Card className={`border-2 ${aiInsight.border}`}>
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className={`p-3 ${aiInsight.bg} rounded-full flex-shrink-0`}>
              {isRefreshing ? (
                <RefreshCw className="h-6 w-6 animate-spin text-gray-500" />
              ) : (
                <InsightIcon className={`h-6 w-6 ${aiInsight.color}`} />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-gray-600" />
                <span className="font-semibold text-gray-900">AI Insight</span>
                {isRefreshing && <RefreshCw className="h-3 w-3 animate-spin text-blue-500" />}
              </div>
              {isRefreshing ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              ) : (
                <>
                  <p className="text-gray-800 mb-2">{aiInsight.message}</p>
                  <p className="text-sm font-medium text-gray-700">
                    Recommended action: {aiInsight.action}
                  </p>
                </>
              )}
              <p className="text-xs text-gray-500 mt-2">{getContextString}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OverviewTab;