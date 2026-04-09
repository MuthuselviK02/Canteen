// IST Time Utility - Centralized Indian Standard Time formatting
// Use this throughout the application for consistent IST display

export const IST_OFFSET = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds

export interface ISTTimeDisplay {
  time: string;
  date: string;
  fullDateTime: string;
}

/**
 * Format date/time to Indian Standard Time (IST)
 * @param date - Date object or ISO string
 * @returns Formatted IST time string (e.g., "08:26 AM")
 */
export const formatISTTime = (date: Date | string): string => {
  if (!date) return '--:--';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    // Check if the input is already in IST (local time) or UTC
    // If it's a current date object, it's already in local time (IST for Indian users)
    // If it's an ISO string from backend, it's UTC and needs conversion
    let istTime: Date;

    const isoWithoutTimezone = typeof date === 'string' && date.includes('T') && !date.includes('Z') && !/[+-]\d{2}:\d{2}$/.test(date);
    let useUTCForDisplay = false;

    if (typeof date === 'string' && date.includes('T')) {
      const hasExplicitTimezone = /[+-]\d{2}:\d{2}$/.test(date);
      const isUTCString = date.includes('Z') || /[+-]00:00$/.test(date);

      if (isUTCString) {
        // UTC timestamps from the backend need conversion to IST.
        const utcTime = dateObj.getTime();
        const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
        istTime = new Date(utcTime + istOffset);
      } else if (hasExplicitTimezone) {
        // Timestamps with an explicit non-UTC offset (for example +05:30) are already localized.
        istTime = dateObj;
      } else if (isoWithoutTimezone) {
        // Backend returned a naive ISO string representing IST time.
        const [datePart, timePart] = date.split('T');
        const [year, month, day] = datePart.split('-').map(Number);
        const [hour, minute, second] = timePart.split(/[:.]/).map(Number);
        istTime = new Date(Date.UTC(year, month - 1, day, hour, minute, second || 0));
        useUTCForDisplay = true;
      } else {
        istTime = dateObj;
      }
    } else {
      // Local Date object - already in IST, use as-is
      istTime = dateObj;
    }

    // Use reliable formatting
    const hours = useUTCForDisplay ? istTime.getUTCHours() : istTime.getHours();
    const minutes = useUTCForDisplay ? istTime.getUTCMinutes() : istTime.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12; // Convert 0 to 12
    const displayMinutes = minutes.toString().padStart(2, '0');

    const result = `${displayHours}:${displayMinutes} ${ampm}`;

    console.log('IST Time Conversion:', {
      input: date,
      inputType: typeof date,
      inputDateObj: dateObj,
      istTime: istTime,
      result: result,
      hours: hours,
      minutes: minutes,
      ampm: ampm
    });

    return result;
  } catch (error) {
    console.error('Error formatting IST time:', error);
    // Fallback to simple formatting
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const hours = dateObj.getHours();
    const minutes = dateObj.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    return `${displayHours}:${displayMinutes} ${ampm}`;
  }
};

/**
 * Format date to Indian Standard Time (IST)
 * @param date - Date object or ISO string
 * @returns Formatted IST date string (e.g., "27 Jan 2026")
 */
export const formatISTDate = (date: Date | string): string => {
  if (!date) return 'No Date';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    // Check if the input is already in IST (local time) or UTC
    // If it's a current date object, it's already in local time (IST for Indian users)
    // If it's an ISO string from backend, it's UTC and needs conversion
    let istTime: Date;

    const isoWithoutTimezone = typeof date === 'string' && date.includes('T') && !date.includes('Z') && !/[+-]\d{2}:\d{2}$/.test(date);
    let useUTCForDisplay = false;

    if (typeof date === 'string' && date.includes('T')) {
      const hasExplicitTimezone = /[+-]\d{2}:\d{2}$/.test(date);
      const isUTCString = date.includes('Z') || /[+-]00:00$/.test(date);

      if (isUTCString) {
        // UTC timestamps from the backend need conversion to IST.
        const utcTime = dateObj.getTime();
        const istOffset = 5.5 * 60 * 60 * 1000;
        istTime = new Date(utcTime + istOffset);
      } else if (hasExplicitTimezone) {
        // Explicit non-UTC offsets are already localized.
        istTime = dateObj;
      } else if (isoWithoutTimezone) {
        const [datePart, timePart] = date.split('T');
        const [year, month, day] = datePart.split('-').map(Number);
        const [hour, minute, second] = timePart.split(/[:.]/).map(Number);
        istTime = new Date(Date.UTC(year, month - 1, day, hour, minute, second || 0));
        useUTCForDisplay = true;
      } else {
        istTime = dateObj;
      }
    } else {
      // Local Date object - already in IST, use as-is
      istTime = dateObj;
    }

    // Use reliable formatting instead of toLocaleDateString
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = useUTCForDisplay ? istTime.getUTCDate() : istTime.getDate();
    const month = months[useUTCForDisplay ? istTime.getUTCMonth() : istTime.getMonth()];
    const year = useUTCForDisplay ? istTime.getUTCFullYear() : istTime.getFullYear();

    const result = `${day} ${month} ${year}`;

    console.log('IST Date Conversion:', {
      input: date,
      inputType: typeof date,
      result: result,
      day: day,
      month: month,
      year: year
    });

    return result;
  } catch (error) {
    console.error('Error formatting IST date:', error);
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = dateObj.getDate();
    const month = months[dateObj.getMonth()];
    const year = dateObj.getFullYear();
    return `${day} ${month} ${year}`;
  }
};

/**
 * Format date that is already in IST (no timezone conversion)
 * @param date - Date object or ISO string (already in IST)
 * @returns Formatted date string (e.g., "27 Jan 2026")
 */
export const formatDateOnly = (date: Date | string): string => {
  if (!date) return 'No Date';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    // Use reliable formatting without timezone conversion
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = dateObj.getDate();
    const month = months[dateObj.getMonth()];
    const year = dateObj.getFullYear();

    const result = `${day} ${month} ${year}`;

    console.log('Date Only Conversion:', {
      input: date,
      result: result,
      day: day,
      month: month,
      year: year
    });

    return result;
  } catch (error) {
    console.error('Error formatting date only:', error);
    // Fallback to simple formatting
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }
};

/**
 * Get complete IST time display object
 * @param date - Date object or ISO string
 * @returns ISTTimeDisplay object with time, date, and full datetime
 */
export const getISTDisplay = (date: Date | string): ISTTimeDisplay => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  // Check if the input is already in IST (local time) or UTC
  let istTime: Date;
  let useUTCForDisplay = false;
  const isoWithoutTimezone = typeof date === 'string' && date.includes('T') && !date.includes('Z') && !/[+-]\d{2}:\d{2}$/.test(date);

  if (typeof date === 'string' && date.includes('T')) {
    const hasExplicitTimezone = /[+-]\d{2}:\d{2}$/.test(date);
    const isUTCString = date.includes('Z') || /[+-]00:00$/.test(date);

    if (isUTCString) {
      // UTC timestamps from the backend need conversion to IST.
      const utcTime = dateObj.getTime();
      const istOffset = 5.5 * 60 * 60 * 1000;
      istTime = new Date(utcTime + istOffset);
    } else if (hasExplicitTimezone) {
      // Explicit non-UTC offsets are already localized.
      istTime = dateObj;
    } else if (isoWithoutTimezone) {
      const [datePart, timePart] = date.split('T');
      const [year, month, day] = datePart.split('-').map(Number);
      const [hour, minute, second] = timePart.split(/[:.]/).map(Number);
      istTime = new Date(Date.UTC(year, month - 1, day, hour, minute, second || 0));
      useUTCForDisplay = true;
    } else {
      istTime = dateObj;
    }
  } else {
    // Local Date object - already in IST, use as-is
    istTime = dateObj;
  }

  // Use reliable formatting
  const hours = useUTCForDisplay ? istTime.getUTCHours() : istTime.getHours();
  const minutes = useUTCForDisplay ? istTime.getUTCMinutes() : istTime.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  const displayMinutes = minutes.toString().padStart(2, '0');

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const day = istTime.getDate();
  const month = months[istTime.getMonth()];
  const year = istTime.getFullYear();

  return {
    time: `${displayHours}:${displayMinutes} ${ampm}`,
    date: `${day} ${month} ${year}`,
    fullDateTime: `${day} ${month} ${year}, ${displayHours}:${displayMinutes} ${ampm}`
  };
};

/**
 * Format local time to IST display (for timestamps that are already local)
 * @param date - Date object (local time)
 * @returns Formatted time string in IST format (e.g., "12:53 PM")
 */
export const formatLocalTimeAsIST = (date: Date): string => {
  try {
    // For local timestamps, convert to IST properly
    const localTime = date.getTime();
    const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
    const istTime = new Date(localTime + istOffset);

    // Use reliable formatting
    const hours = istTime.getHours();
    const minutes = istTime.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');

    const result = `${displayHours}:${displayMinutes} ${ampm}`;

    console.log('Local to IST Time Conversion:', {
      localTime: date,
      istTime: istTime,
      result: result
    });

    return result;
  } catch (error) {
    console.error('Error formatting local time as IST:', error);
    // Fallback to simple formatting
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    return `${displayHours}:${displayMinutes} ${ampm}`;
  }
};

/**
 * Get current IST time
 * @returns Current IST time string
 */
export const getCurrentISTTime = (): string => {
  return formatISTTime(new Date());
};

/**
 * Get current IST date in YYYY-MM-DD format (for API calls)
 * @returns Current IST date string in YYYY-MM-DD format
 */
export const getCurrentISTDateForAPI = (): string => {
  const now = new Date();
  const utcTime = now.getTime();
  const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
  const istNow = new Date(utcTime + istOffset);

  const year = istNow.getFullYear();
  const month = String(istNow.getMonth() + 1).padStart(2, '0');
  const day = String(istNow.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
};

/**
 * Get current business day in IST for billing purposes
 * Business day runs from 6:00 AM to next day 5:59 AM IST
 * @returns Business day string in YYYY-MM-DD format
 */
export const getBusinessDayForAPI = (): string => {
  const now = new Date();

  // Use proper IST calculation by creating a new date with the offset
  const utcTime = now.getTime();
  const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
  const istNow = new Date(utcTime + istOffset);

  // Get the correct IST hour
  const istHour = istNow.getUTCHours(); // Use UTC hours after offset

  console.log('🕐 getBusinessDayForAPI Debug:', {
    utcTime: now.toISOString(),
    istTime: istNow.toISOString(),
    istHour: istHour,
    istDate: istNow.toISOString().split('T')[0]
  });

  // If it's before 6 AM IST, it's still previous business day
  if (istHour < 6) {
    // Go back to previous day
    istNow.setUTCDate(istNow.getUTCDate() - 1);
    console.log('🕐 Before 6 AM IST, using previous business day:', istNow.toISOString().split('T')[0]);
  }

  const year = istNow.getUTCFullYear();
  const month = String(istNow.getUTCMonth() + 1).padStart(2, '0');
  const day = String(istNow.getUTCDate()).padStart(2, '0');

  const result = `${year}-${month}-${day}`;
  console.log('🕐 Final business day result:', result);
  return result;
};

/**
 * Get IST date range for a given number of days back
 * @param daysBack - Number of days to go back from today
 * @returns Object with start and end dates in YYYY-MM-DD format
 */
export const getISTDateRange = (daysBack: number = 0): { start: string; end: string } => {
  // Get current IST date first
  const now = new Date();
  const utcTime = now.getTime();
  const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
  const istNow = new Date(utcTime + istOffset);

  // Use IST date for calculations
  const endYear = istNow.getFullYear();
  const endMonth = String(istNow.getMonth() + 1).padStart(2, '0');
  const endDay = String(istNow.getDate()).padStart(2, '0');
  const endStr = `${endYear}-${endMonth}-${endDay}`;

  // Calculate start date by going back daysBack days from IST now
  const startDate = new Date(istNow.getTime() - daysBack * 24 * 60 * 60 * 1000);
  const startYear = startDate.getFullYear();
  const startMonth = String(startDate.getMonth() + 1).padStart(2, '0');
  const startDay = String(startDate.getDate()).padStart(2, '0');
  const startStr = `${startYear}-${startMonth}-${startDay}`;

  console.log('📅 IST Date Range Calculation:', {
    localNow: now,
    istNow: istNow,
    daysBack,
    start: startStr,
    end: endStr
  });

  return { start: startStr, end: endStr };
};

/**
 * Get current IST date
 * @returns Current IST date string
 */
export const getCurrentISTDate = (): string => {
  return formatISTDate(new Date());
};

/**
 * Get current IST date and time
 * @returns Current IST date and time string
 */
export const getCurrentISTDateTime = (): string => {
  const now = new Date();
  const utcTime = now.getTime();
  const istOffset = 5.5 * 60 * 60 * 1000;
  const istTime = new Date(utcTime + istOffset);

  // Use reliable formatting
  const hours = istTime.getHours();
  const minutes = istTime.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  const displayMinutes = minutes.toString().padStart(2, '0');

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const day = istTime.getDate();
  const month = months[istTime.getMonth()];
  const year = istTime.getFullYear();

  return `${day} ${month} ${year}, ${displayHours}:${displayMinutes} ${ampm}`;
};

/**
 * Calculate dynamic estimated time based on order status
 * @param order - Order object with status and timestamps
 * @param currentTime - Current time for calculations
 * @returns Dynamic estimated time string
 */
export const calculateDynamicEstimatedTime = (order: any, currentTime: Date): string => {
  const createdAt = new Date(order.createdAt);

  if (order.status === 'completed') {
    return 'Completed';
  }

  if (order.status === 'ready') {
    return 'Ready for pickup';
  }

  if (order.status === 'preparing') {
    // For preparing orders, calculate remaining time
    const startedAt = order.startedPreparationAt ? new Date(order.startedPreparationAt) : createdAt;
    const elapsedMinutes = Math.floor((currentTime.getTime() - startedAt.getTime()) / (1000 * 60));
    const basePrepTime = order.estimatedTime || 15; // Default 15 minutes
    const remainingMinutes = Math.max(0, basePrepTime - elapsedMinutes);

    if (remainingMinutes <= 0) {
      return 'Almost ready';
    } else if (remainingMinutes <= 2) {
      return `${remainingMinutes} min`;
    } else {
      return `~${remainingMinutes} min`;
    }
  }

  if (order.status === 'pending') {
    // For pending orders, calculate wait time including queue
    const baseWaitTime = order.estimatedTime || 20; // Default 20 minutes
    const queueDelay = (order.queuePosition || 1) * 5; // 5 minutes per position in queue
    const totalWaitTime = baseWaitTime + queueDelay;

    return `~${totalWaitTime} min`;
  }

  return 'Calculating...';
};

/**
 * Get time display based on order status with IST formatting
 * @param order - Order object
 * @param currentTime - Current time
 * @returns Time display object with IST formatted times
 */
export const getOrderTimeDisplay = (order: any, currentTime: Date) => {
  const { status, createdAt, startedPreparationAt, readyAt, completedAt } = order;

  let timeToUse: Date;
  let label: string;

  if (status === 'completed') {
    timeToUse = completedAt ? new Date(completedAt) : new Date(createdAt);
    label = 'Completed';
  } else if (status === 'ready') {
    timeToUse = readyAt ? new Date(readyAt) : new Date(createdAt);
    label = 'Ready';
  } else if (status === 'preparing') {
    timeToUse = startedPreparationAt ? new Date(startedPreparationAt) : new Date(createdAt);
    label = 'Started';
  } else {
    timeToUse = new Date(createdAt);
    label = 'Ordered';
  }

  return {
    time: formatISTTime(timeToUse),
    date: formatISTDate(timeToUse),
    label: label,
    estimatedTime: calculateDynamicEstimatedTime(order, currentTime),
    rawTime: timeToUse.toISOString()
  };
};
