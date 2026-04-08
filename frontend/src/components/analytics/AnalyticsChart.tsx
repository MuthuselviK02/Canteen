import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ChartDataPoint {
  date: string;
  revenue: number;
  orders: number;
  customers: number;
}

interface AnalyticsChartProps {
  title: string;
  data: ChartDataPoint[];
  type: 'revenue' | 'orders' | 'customers';
  color?: string;
}

const AnalyticsChart: React.FC<AnalyticsChartProps> = ({ 
  title, 
  data, 
  type, 
  color = '#3b82f6' 
}) => {
  const getValue = (point: ChartDataPoint) => {
    switch (type) {
      case 'revenue': return point.revenue;
      case 'orders': return point.orders;
      case 'customers': return point.customers;
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
      default:
        return value.toString();
    }
  };

  const maxValue = Math.max(...data.map(getValue));
  const minValue = Math.min(...data.map(getValue));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {title}
          <Badge variant="outline">
            {data.length} data points
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Simple Bar Chart */}
          <div className="relative h-64">
            <div className="absolute inset-0 flex items-end justify-between space-x-1">
              {data.map((point, index) => {
                const value = getValue(point);
                const height = maxValue > 0 ? (value / maxValue) * 100 : 0;
                
                return (
                  <div
                    key={index}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 transition-colors rounded-t relative group"
                    style={{ height: `${height}%`, backgroundColor: color }}
                  >
                    <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                      {formatValue(value)}
                    </div>
                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full text-xs text-gray-600 mt-1 whitespace-nowrap">
                      {new Date(point.date).toLocaleDateString('en-IN', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Y-axis labels */}
            <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-gray-600 -ml-14">
              <span>{formatValue(maxValue)}</span>
              <span>{formatValue((maxValue + minValue) / 2)}</span>
              <span>{formatValue(minValue)}</span>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total</p>
              <p className="font-semibold">
                {formatValue(data.reduce((sum, point) => sum + getValue(point), 0))}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Average</p>
              <p className="font-semibold">
                {formatValue(data.reduce((sum, point) => sum + getValue(point), 0) / data.length)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Peak</p>
              <p className="font-semibold">
                {formatValue(maxValue)}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalyticsChart;
