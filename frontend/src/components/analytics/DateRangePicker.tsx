import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Calendar, CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react';
import { getBusinessDayForAPI } from '@/utils/istTime';

interface DateRangePickerProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onApply: () => void;
}

const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onApply
}) => {
  const [showCalendar, setShowCalendar] = useState(false);

  const getToday = () => {
    // Use business day logic for consistency with billing
    return getBusinessDayForAPI();
  };
  const getLastWeek = () => {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    date.setHours(date.getHours() + 5, date.getMinutes() + 30);
    return date.toISOString().split('T')[0];
  };
  const getLastMonth = () => {
    const date = new Date();
    date.setMonth(date.getMonth() - 1);
    date.setHours(date.getHours() + 5, date.getMinutes() + 30);
    return date.toISOString().split('T')[0];
  };
  const getLast3Months = () => {
    const date = new Date();
    date.setMonth(date.getMonth() - 3);
    date.setHours(date.getHours() + 5, date.getMinutes() + 30);
    return date.toISOString().split('T')[0];
  };

  const quickRanges = [
    { label: 'Today', start: getToday(), end: getToday() },
    { label: 'Last 7 Days', start: getLastWeek(), end: getToday() },
    { label: 'Last 30 Days', start: getLastMonth(), end: getToday() },
    { label: 'Last 90 Days', start: getLast3Months(), end: getToday() },
  ];

  const applyQuickRange = (start: string, end: string) => {
    // Validate dates
    const startDate = new Date(start);
    const endDate = new Date(end);
    const today = new Date();
    
    // Don't allow future dates
    if (startDate > today || endDate > today) {
      console.warn('Cannot select future dates');
      return;
    }
    
    // Validate date range
    if (startDate > endDate) {
      console.warn('Start date cannot be after end date');
      return;
    }
    
    onStartDateChange(start);
    onEndDateChange(end);
    onApply();
  };

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="space-y-4">
          {/* Quick Range Buttons */}
          <div className="flex flex-wrap gap-2">
            {quickRanges.map((range) => (
              <Button
                key={range.label}
                variant="outline"
                size="sm"
                onClick={() => applyQuickRange(range.start, range.end)}
                className="text-xs"
              >
                {range.label}
              </Button>
            ))}
          </div>

          {/* Custom Date Range */}
          <div className="flex items-center space-x-2">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => onStartDateChange(e.target.value)}
                max={endDate || getToday()}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center pb-6">
              <CalendarDays className="h-4 w-4 text-gray-400" />
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => onEndDateChange(e.target.value)}
                min={startDate}
                max={getToday()}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Apply Button */}
          <div className="flex justify-end">
            <Button onClick={onApply} className="w-full sm:w-auto">
              Apply Date Range
            </Button>
          </div>

          {/* Current Selection Display */}
          {startDate && endDate && (
            <div className="bg-blue-50 p-3 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Selected Range:</strong> {new Date(startDate).toLocaleDateString('en-IN')} - {new Date(endDate).toLocaleDateString('en-IN')}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default DateRangePicker;
