import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, TrendingDown, BarChart3, LineChart } from 'lucide-react';

interface ChartDataPoint {
  date: string;
  revenue: number;
  orders: number;
  customers: number;
  avg_order_value?: number;
}

interface DynamicAnalyticsChartProps {
  title: string;
  data: ChartDataPoint[];
  type: 'revenue' | 'orders' | 'customers' | 'avg_order_value';
  color?: string;
  height?: number;
}

const DynamicAnalyticsChart: React.FC<DynamicAnalyticsChartProps> = ({ 
  title, 
  data, 
  type, 
  color = '#3b82f6',
  height = 300
}) => {
  const [chartType, setChartType] = useState<'bar' | 'line'>('bar');
  const [hoveredBar, setHoveredBar] = useState<number | null>(null);

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
        return value.toString();
      case 'avg_order_value':
        return new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0,
        }).format(value);
      default:
        return value.toString();
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

  const maxValue = Math.max(...data.map(getValue));
  const minValue = Math.min(...data.map(getValue));
  const avgValue = data.reduce((sum, point) => sum + getValue(point), 0) / data.length;

  // Calculate trend
  const calculateTrend = () => {
    if (data.length < 2) return { trend: 'neutral', change: 0 };
    const firstValue = getValue(data[0]);
    const lastValue = getValue(data[data.length - 1]);
    const change = ((lastValue - firstValue) / firstValue) * 100;
    return {
      trend: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral',
      change
    };
  };

  const trend = calculateTrend();

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            {chartType === 'bar' ? <BarChart3 className="h-5 w-5" /> : <LineChart className="h-5 w-5" />}
            {title}
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Badge 
              variant={trend.trend === 'up' ? 'default' : trend.trend === 'down' ? 'destructive' : 'secondary'}
              className="flex items-center space-x-1"
            >
              {trend.trend === 'up' && <TrendingUp className="h-3 w-3" />}
              {trend.trend === 'down' && <TrendingDown className="h-3 w-3" />}
              {trend.change.toFixed(1)}%
            </Badge>
            <Select value={chartType} onValueChange={(value: 'bar' | 'line') => setChartType(value)}>
              <SelectTrigger className="w-24">
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
      <CardContent>
        <div className="space-y-4">
          {/* Chart Container */}
          <div className="relative overflow-x-auto" style={{ height: `${height}px` }}>
            {chartType === 'bar' ? (
              <div className="flex items-end justify-between space-x-1 px-2 min-w-max" style={{ height: `${height - 40}px`, minHeight: '200px' }}>
                {data.map((point, index) => {
                  const value = getValue(point);
                  const barHeight = maxValue > 0 ? (value / maxValue) * (height - 40) : 0;
                  const isHovered = hoveredBar === index;
                  const barWidth = Math.max(40, Math.min(80, 800 / data.length)); // Dynamic bar width
                  
                  return (
                    <div
                      key={index}
                      className="relative group cursor-pointer flex-shrink-0"
                      style={{ width: `${barWidth}px` }}
                      onMouseEnter={() => setHoveredBar(index)}
                      onMouseLeave={() => setHoveredBar(null)}
                    >
                      <div
                        className="w-full bg-gradient-to-t from-blue-600 to-blue-400 hover:from-blue-700 hover:to-blue-500 transition-all duration-200 rounded-t relative"
                        style={{ 
                          height: `${barHeight}px`,
                          backgroundColor: isHovered ? color : undefined,
                          transform: isHovered ? 'scale(1.05)' : 'scale(1)'
                        }}
                      >
                        {/* Value tooltip */}
                        <div className={`absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap transition-opacity z-10 ${
                          isHovered ? 'opacity-100' : 'opacity-0'
                        }`}>
                          {formatValue(value)}
                        </div>
                      </div>
                      
                      {/* Date label */}
                      <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap">
                        {new Date(point.date).toLocaleDateString('en-IN', { 
                          month: 'short', 
                          day: 'numeric' 
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <svg 
                  className="min-w-max" 
                  viewBox={`0 0 ${data.length * 80} ${height}`}
                  style={{ width: `${data.length * 80}px`, height: `${height - 40}px` }}
                >
                  {/* Grid lines */}
                  {[0, 0.25, 0.5, 0.75, 1].map((fraction) => (
                    <line
                      key={fraction}
                      x1="0"
                      y1={height - (fraction * (height - 40)) - 20}
                      x2={data.length * 80}
                      y2={height - (fraction * (height - 40)) - 20}
                      stroke="#e5e7eb"
                      strokeWidth="1"
                    />
                  ))}
                  
                  {/* Line chart */}
                  <polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    points={data.map((point, index) => {
                      const value = getValue(point);
                      const y = height - ((value / maxValue) * (height - 40)) - 20;
                      return `${index * 80 + 40},${y}`;
                    }).join(' ')}
                  />
                  
                  {/* Data points */}
                  {data.map((point, index) => {
                    const value = getValue(point);
                    const y = height - ((value / maxValue) * (height - 40)) - 20;
                    
                    return (
                      <g key={index}>
                        <circle
                          cx={index * 80 + 40}
                          cy={y}
                          r="4"
                          fill={color}
                          className="cursor-pointer hover:r-6 transition-all"
                          onMouseEnter={() => setHoveredBar(index)}
                          onMouseLeave={() => setHoveredBar(null)}
                        />
                        {hoveredBar === index && (
                          <text
                            x={index * 80 + 40}
                            y={y - 10}
                            textAnchor="middle"
                            className="text-xs fill-gray-700"
                          >
                            {formatValue(value)}
                          </text>
                        )}
                        <text
                          x={index * 80 + 40}
                          y={height - 5}
                          textAnchor="middle"
                          className="text-xs fill-gray-600"
                        >
                          {new Date(point.date).toLocaleDateString('en-IN', { 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>
            )}
            
            {/* Y-axis labels */}
            <div className="absolute left-0 top-0 bottom-6 w-12 flex flex-col justify-between text-xs text-gray-600 -ml-14">
              <span>{formatValue(maxValue)}</span>
              <span>{formatValue(avgValue)}</span>
              <span>{formatValue(minValue)}</span>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-4 pt-4 border-t">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total</p>
              <p className="font-semibold text-sm">
                {formatValue(data.reduce((sum, point) => sum + getValue(point), 0))}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Average</p>
              <p className="font-semibold text-sm">
                {formatValue(avgValue)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Peak</p>
              <p className="font-semibold text-sm">
                {formatValue(maxValue)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Data Points</p>
              <p className="font-semibold text-sm">
                {data.length}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DynamicAnalyticsChart;
