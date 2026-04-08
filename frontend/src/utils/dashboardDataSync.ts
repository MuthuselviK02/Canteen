import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
/**
 * Dashboard Data Synchronization Utility
 * Ensures consistent data across all dashboards
 */

export interface SharedMetrics {
  today_revenue: number;
  today_orders: number;
  avg_order_value: number;
  completion_rate: number;
  last_updated: string;
}

export interface DashboardRoles {
  predictive: {
    focus: string;
    metrics: string[];
    exclusives: string[];
  };
  analytics: {
    focus: string;
    metrics: string[];
    exclusives: string[];
  };
  billing: {
    focus: string;
    metrics: string[];
    exclusives: string[];
  };
}

export const DASHBOARD_ROLES: DashboardRoles = {
  predictive: {
    focus: "ML-powered predictions & forecasting",
    metrics: [
      "demand_forecast",
      "queue_predictions", 
      "churn_risk_analysis",
      "revenue_forecast",
      "optimal_staffing",
      "inventory_predictions"
    ],
    exclusives: [
      "preparation_time_predictions",
      "customer_behavior_patterns",
      "peak_hour_forecasts",
      "ml_model_performance"
    ]
  },
  analytics: {
    focus: "Historical performance & business insights",
    metrics: [
      "revenue_trends",
      "order_analytics", 
      "customer_analytics",
      "menu_performance",
      "operational_efficiency"
    ],
    exclusives: [
      "hourly_breakdown",
      "weekly_comparisons",
      "growth_metrics",
      "food_cost_analysis"
    ]
  },
  billing: {
    focus: "Invoice management & payment processing",
    metrics: [
      "invoice_management",
      "payment_tracking",
      "revenue_collection",
      "billing_analytics"
    ],
    exclusives: [
      "invoice_crud_operations",
      "payment_method_analysis",
      "outstanding_payments",
      "billing_reports"
    ]
  }
};

// Shared metrics that should be consistent across dashboards
export const SHARED_METRICS = [
  "today_revenue",
  "today_orders", 
  "avg_order_value",
  "completion_rate"
];

// API endpoints for shared data
export const SHARED_DATA_ENDPOINTS = {
  primary: buildApiUrl("/api/analytics/shared-metrics"),
  fallback: buildApiUrl("/api/analytics/dashboard")
};

/**
 * Fetch shared metrics to ensure consistency
 */
export const fetchSharedMetrics = async (): Promise<SharedMetrics | null> => {
  try {
    const token = localStorage.getItem('canteen_token');
    if (!token) return null;

    const response = await fetch(SHARED_DATA_ENDPOINTS.primary, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      return await response.json();
    } else {
      // Fallback to analytics dashboard
      const fallbackResponse = await fetch(SHARED_DATA_ENDPOINTS.fallback, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json();
        return {
          today_revenue: data.today?.revenue || 0,
          today_orders: data.today?.orders || 0,
          avg_order_value: data.today?.avg_order_value || 0,
          completion_rate: data.today?.completion_rate || 0,
          last_updated: new Date().toISOString()
        };
      }
    }
  } catch (error) {
    console.error('Failed to fetch shared metrics:', error);
  }
  
  return null;
};

/**
 * Validate dashboard data consistency
 */
export const validateDataConsistency = (
  dashboardName: string,
  metrics: Partial<SharedMetrics>,
  sharedMetrics: SharedMetrics
): boolean => {
  const tolerance = 0.05; // 5% tolerance
  
  for (const metric of SHARED_METRICS) {
    const dashboardValue = (metrics[metric as keyof SharedMetrics] as number) || 0;
    const sharedValue = sharedMetrics[metric as keyof SharedMetrics] || 0;
    
    if (typeof sharedValue === 'number' && sharedValue > 0) {
      const difference = Math.abs(dashboardValue - sharedValue) / sharedValue;
      if (difference > tolerance) {
        console.warn(`Data inconsistency in ${dashboardName}: ${metric} differs by ${(difference * 100).toFixed(1)}%`);
        return false;
      }
    }
  }
  
  return true;
};
