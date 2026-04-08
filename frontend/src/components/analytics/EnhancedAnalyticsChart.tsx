import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, TrendingDown, BarChart3, LineChart, Calendar, Users, ShoppingCart, DollarSign } from 'lucide-react';

interface ChartDataPoint {
  date: string;
  revenue: number;
  orders: number;
  customers: number;
  avg_order_value?: number;
  revenue_growth?: number;
  orders_growth?: number;
  customers_growth?: number;
  avg_order_growth?: number;
}

interface EnhancedAnalyticsChartProps {
  title: string;
  data: ChartDataPoint[];
  type: 'revenue' | 'orders' | 'customers' | 'avg_order_value';
  color?: string;
  height?: number;
}

const EnhancedAnalyticsChart: React.FC<EnhancedAnalyticsChartProps> = ({
  title,
  data,
  type,
  color = '#3b82f6',
  height = 350
}) => {
  const [chartType, setChartType] = useState<'bar' | 'line'>('bar');
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [isMobile, setIsMobile] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);

  // Detect if data is hourly based on date format
  const isHourlyData = data.length > 0 && data[0].date.includes(':');

  // Format X-axis label based on bucket type
  const formatLabel = (dateStr: string) => {
    if (dateStr.includes(':')) {
      // Hourly format: "2026-02-05 10:00" -> "10 AM"
      const hour = parseInt(dateStr.split(' ')[1].split(':')[0]);
      return `${hour % 12 || 12} ${hour >= 12 ? 'PM' : 'AM'}`;
    }
    // Daily format: "2026-02-05" -> "5 Feb"
    return new Date(dateStr).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric'
    });
  };
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const getValue = (point: ChartDataPoint) => {
    switch (type) {
      case 'revenue': return point.revenue;
      case 'orders': return point.orders;
      case 'customers': return point.customers;
      case 'avg_order_value': return point.avg_order_value || 0;
      default: return point.revenue;
    }
  };

  const formatValue = (value: number) => {
    switch (type) {
      case 'revenue':
        return new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0,
        }).format(value);
      case 'orders':
      case 'customers':
        return value.toLocaleString('en-IN');
      case 'avg_order_value':
        return new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0,
        }).format(value);
      default:
        return value.toLocaleString('en-IN');
    }
  };

  const getUnit = () => {
    switch (type) {
      case 'revenue': return 'Revenue';
      case 'orders': return 'Orders';
      case 'customers': return 'Customers';
      case 'avg_order_value': return 'Avg Order Value';
      default: return 'Value';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'revenue': return <DollarSign className="h-4 w-4" />;
      case 'orders': return <ShoppingCart className="h-4 w-4" />;
      case 'customers': return <Users className="h-4 w-4" />;
      case 'avg_order_value': return <TrendingUp className="h-4 w-4" />;
      default: return <BarChart3 className="h-4 w-4" />;
    }
  };

  const maxValue = data.length > 0 ? Math.max(...data.map(getValue)) : 0;
  const minValue = data.length > 0 ? Math.min(...data.map(getValue)) : 0;
  const avgValue = data.length > 0 ? data.reduce((sum, point) => sum + getValue(point), 0) / data.length : 0;

  const calculateTrend = () => {
    if (!data || data.length === 0) return { trend: 'neutral', change: 0 };

    const latestData = data[data.length - 1];

    let growthValue = 0;
    switch (type) {
      case 'revenue':
        growthValue = (latestData as any).revenue_growth || 0;
        break;
      case 'orders':
        growthValue = (latestData as any).orders_growth || 0;
        break;
      case 'customers':
        growthValue = (latestData as any).customers_growth || 0;
        break;
      case 'avg_order_value':
        growthValue = latestData.avg_order_growth || 0;
        break;
    }

    return {
      trend: growthValue > 0 ? 'up' : growthValue < 0 ? 'down' : 'neutral',
      change: growthValue
    };
  };

  const trend = calculateTrend();

  const getTooltipData = (point: ChartDataPoint, index: number) => {
    const value = getValue(point);

    let change = 0;
    switch (type) {
      case 'revenue': change = point.revenue_growth || 0; break;
      case 'orders': change = point.orders_growth || 0; break;
      case 'customers': change = point.customers_growth || 0; break;
      case 'avg_order_value': change = point.avg_order_growth || 0; break;
    }

    return {
      date: new Date(point.date).toLocaleDateString('en-IN', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }),
      value: formatValue(value),
      change: change.toFixed(1),
      orders: point.orders.toLocaleString('en-IN'),
      revenue: formatValue(point.revenue),
      customers: point.customers.toLocaleString('en-IN'),
      avgOrder: formatValue(point.avg_order_value || 0)
    };
  };

  const handleMouseMove = (e: React.MouseEvent, index: number) => {
    if (!chartRef.current) return;

    const chartRect = chartRef.current.getBoundingClientRect();
    const value = getValue(data[index]);
    const barHeight = maxValue > 0 ? (value / maxValue) * (height - 60) : 0;

    const mouseX = e.clientX - chartRect.left;
    const mouseY = e.clientY - chartRect.top;

    const tooltipWidth = 260;
    const tooltipHeight = 200;

    let tooltipX = mouseX + 15;
    let tooltipY = mouseY - tooltipHeight / 2;

    if (tooltipX + tooltipWidth > chartRect.width) {
      tooltipX = mouseX - tooltipWidth - 15;
    }

    if (tooltipY < 0) {
      tooltipY = 10;
    }

    if (tooltipY + tooltipHeight > height) {
      tooltipY = height - tooltipHeight - 10;
    }

    setTooltipPosition({ x: tooltipX, y: tooltipY });
    setHoveredIndex(index);
  };

  const handleMouseLeave = () => {
    setHoveredIndex(null);
  };

  const getBarWidth = () => {
    if (isMobile) return Math.max(30, Math.min(60, 600 / data.length));
    return Math.max(40, Math.min(80, 800 / data.length));
  };

  const getSpacing = () => {
    if (isMobile) return 60;
    return 80;
  };

  return (
    <Card className="w-full shadow-lg hover:shadow-xl transition-shadow duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <CardTitle className="flex items-center space-x-2 text-lg">
            {getIcon()}
            {title}
          </CardTitle>
          <div className="flex items-center space-x-2 flex-wrap">
            <Badge
              variant={trend.trend === 'up' ? 'default' : trend.trend === 'down' ? 'destructive' : 'secondary'}
              className="flex items-center space-x-1 px-3 py-1"
            >
              {trend.trend === 'up' && <TrendingUp className="h-3 w-3" />}
              {trend.trend === 'down' && <TrendingDown className="h-3 w-3" />}
              {trend.change >= 0 ? '+' : ''}{trend.change.toFixed(1)}%
            </Badge>
            <Select value={chartType} onValueChange={(value: 'bar' | 'line') => setChartType(value)}>
              <SelectTrigger className="w-24 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bar">Bar</SelectItem>
                <SelectItem value="line">Line</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-4">
          {!data || data === null || data === undefined ? (
            <div className="flex items-center justify-center" style={{ height: `${height}px` }}>
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500 text-sm">No data available for selected date range</p>
              </div>
            </div>
          ) : (
            <>
              <div
                className="relative overflow-x-auto overflow-y-visible"
                style={{ height: `${height}px` }}
              >
                <div
                  ref={chartRef}
                  className="relative min-w-max"
                  style={{ height: `${height}px` }}
                >
                  {chartType === 'bar' ? (
                    <div className="relative">
                      <div
                        className="flex items-end justify-between space-x-1 px-2"
                        style={{ height: `${height - 60}px`, minHeight: '200px' }}
                      >
                        {data.map((point, index) => {
                          const value = getValue(point);
                          const barHeight = maxValue > 0 ? (value / maxValue) * (height - 60) : 0;
                          const isHovered = hoveredIndex === index;
                          const barWidth = getBarWidth();

                          return (
                            <div
                              key={index}
                              className="relative group cursor-pointer flex-shrink-0 transition-all duration-200"
                              style={{ width: `${barWidth}px` }}
                              onMouseEnter={(e) => handleMouseMove(e, index)}
                              onMouseMove={(e) => handleMouseMove(e, index)}
                              onMouseLeave={handleMouseLeave}
                            >
                              <div
                                className={`w-full rounded-t relative transition-all duration-300 ${isHovered
                                    ? 'bg-gradient-to-t from-blue-700 to-blue-500 shadow-lg transform scale-105'
                                    : 'bg-gradient-to-t from-blue-600 to-blue-400 hover:from-blue-700 hover:to-blue-500'
                                  }`}
                                style={{
                                  height: `${barHeight}px`,
                                  backgroundColor: isHovered ? color : undefined,
                                  boxShadow: isHovered ? '0 4px 20px rgba(0,0,0,0.2)' : 'none'
                                }}
                              >
                                {/* Enhanced value indicator */}
                                {isHovered && (
                                  <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
                                )}
                              </div>

                              {/* Bucket label */}
                              <div className={`absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs transition-colors ${isHovered ? 'text-blue-600 font-semibold' : 'text-gray-600'
                                } whitespace-nowrap`}>
                                {formatLabel(point.date)}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <svg
                        className="min-w-max transition-all duration-300"
                        viewBox={`0 0 ${data.length * getSpacing()} ${height}`}
                        style={{ width: `${data.length * getSpacing()}px`, height: `${height - 60}px` }}
                      >
                        {/* Grid lines */}
                        {[0, 0.25, 0.5, 0.75, 1].map((fraction) => (
                          <line
                            key={fraction}
                            x1="0"
                            y1={height - (fraction * (height - 60)) - 30}
                            x2={data.length * getSpacing()}
                            y2={height - (fraction * (height - 60)) - 30}
                            stroke="#e5e7eb"
                            strokeWidth="1"
                            strokeDasharray="2,2"
                          />
                        ))}

                        {/* Line chart */}
                        <polyline
                          fill="none"
                          stroke={color}
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          points={data.map((point, index) => {
                            const value = getValue(point);
                            const y = height - ((value / maxValue) * (height - 60)) - 30;
                            return `${index * getSpacing() + getSpacing() / 2},${y}`;
                          }).join(' ')}
                        />

                        {/* Data points */}
                        {data.map((point, index) => {
                          const value = getValue(point);
                          const y = height - ((value / maxValue) * (height - 60)) - 30;
                          const isHovered = hoveredIndex === index;

                          return (
                            <g key={index}>
                              <circle
                                cx={index * getSpacing() + getSpacing() / 2}
                                cy={y}
                                r={isHovered ? 6 : 4}
                                fill={color}
                                className="cursor-pointer transition-all duration-200"
                                stroke="white"
                                strokeWidth="2"
                                onMouseEnter={(e) => handleMouseMove(e, index)}
                                onMouseLeave={handleMouseLeave}
                              />
                              {isHovered && (
                                <circle
                                  cx={index * getSpacing() + getSpacing() / 2}
                                  cy={y}
                                  r={10}
                                  fill={color}
                                  fillOpacity="0.2"
                                  className="animate-pulse"
                                />
                              )}
                              <text
                                x={index * getSpacing() + getSpacing() / 2}
                                y={height - 10}
                                textAnchor="middle"
                                className={`text-xs transition-colors ${isHovered ? 'fill-blue-600 font-semibold' : 'fill-gray-600'
                                  }`}
                              >
                                {formatLabel(point.date)}
                              </text>
                            </g>
                          );
                        })}
                      </svg>
                    </div>
                  )}

                  {hoveredIndex !== null && (
                    <div
                      className="absolute z-50 bg-gray-900 text-white p-3 rounded-lg shadow-2xl pointer-events-none transition-all duration-200"
                      style={{
                        left: `${tooltipPosition.x}px`,
                        top: `${tooltipPosition.y}px`,
                        maxWidth: '260px',
                        fontSize: '11px'
                      }}
                    >
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 border-b border-gray-700 pb-2">
                          <Calendar className="h-4 w-4 text-blue-400" />
                          <span className="font-semibold text-sm">
                            {getTooltipData(data[hoveredIndex], hoveredIndex).date}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-xs">
                          <div>
                            <span className="text-gray-400">{getUnit()}:</span>
                            <div className="font-bold text-white">
                              {getTooltipData(data[hoveredIndex], hoveredIndex).value}
                            </div>
                          </div>

                          <div>
                            <span className="text-gray-400">Change:</span>
                            <div className={`font-bold ${parseFloat(getTooltipData(data[hoveredIndex], hoveredIndex).change) >= 0
                                ? 'text-green-400' : 'text-red-400'
                              }`}>
                              {parseFloat(getTooltipData(data[hoveredIndex], hoveredIndex).change) >= 0 ? '+' : ''}
                              {getTooltipData(data[hoveredIndex], hoveredIndex).change}%
                            </div>
                          </div>

                          {type !== 'revenue' && (
                            <div>
                              <span className="text-gray-400">Revenue:</span>
                              <div className="font-semibold">
                                {getTooltipData(data[hoveredIndex], hoveredIndex).revenue}
                              </div>
                            </div>
                          )}

                          {type !== 'orders' && (
                            <div>
                              <span className="text-gray-400">Orders:</span>
                              <div className="font-semibold">
                                {getTooltipData(data[hoveredIndex], hoveredIndex).orders}
                              </div>
                            </div>
                          )}

                          {type !== 'customers' && (
                            <div>
                              <span className="text-gray-400">Customers:</span>
                              <div className="font-semibold">
                                {getTooltipData(data[hoveredIndex], hoveredIndex).customers}
                              </div>
                            </div>
                          )}

                          {type !== 'avg_order_value' && (
                            <div>
                              <span className="text-gray-400">Avg Order:</span>
                              <div className="font-semibold">
                                {getTooltipData(data[hoveredIndex], hoveredIndex).avgOrder}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Tooltip arrow - pointing left or right based on position */}
                      <div
                        className="absolute top-1/2 transform -translate-y-1/2 w-0 h-0"
                        style={{
                          left: tooltipPosition.x > 300 ? 'auto' : '-8px',
                          right: tooltipPosition.x > 300 ? '-8px' : 'auto',
                          borderTop: '8px solid transparent',
                          borderBottom: '8px solid transparent',
                          borderRight: tooltipPosition.x > 300 ? 'none' : '8px solid #111827',
                          borderLeft: tooltipPosition.x > 300 ? '8px solid #111827' : 'none'
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Enhanced Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-4 border-t">
                <div className="text-center p-2 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
                  <p className="text-xs text-blue-600 font-medium">Total</p>
                  <p className="font-bold text-blue-900 text-sm">
                    {formatValue(data.reduce((sum, point) => sum + getValue(point), 0))}
                  </p>
                </div>
                <div className="text-center p-2 rounded-lg bg-green-50 hover:bg-green-100 transition-colors">
                  <p className="text-xs text-green-600 font-medium">Average</p>
                  <p className="font-bold text-green-900 text-sm">
                    {formatValue(avgValue)}
                  </p>
                </div>
                <div className="text-center p-2 rounded-lg bg-purple-50 hover:bg-purple-100 transition-colors">
                  <p className="text-xs text-purple-600 font-medium">Peak</p>
                  <p className="font-bold text-purple-900 text-sm">
                    {formatValue(maxValue)}
                  </p>
                </div>
                <div className="text-center p-2 rounded-lg bg-orange-50 hover:bg-orange-100 transition-colors">
                  <p className="text-xs text-orange-600 font-medium">{isHourlyData ? 'Hours' : 'Days'}</p>
                  <p className="font-bold text-orange-900 text-sm">
                    {data.length}
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedAnalyticsChart;