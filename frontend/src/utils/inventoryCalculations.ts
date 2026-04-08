/**
 * Predictive Inventory System
 * 
 * CORE PRINCIPLE: Strict separation of past reality, present state, and future expectation
 * Never mix past actuals and future predictions incorrectly.
 */

export interface MenuItemData {
  id: number;
  name: string;
  category: string;
  opening_stock: number; // Set ONCE per day
  reorder_threshold?: number;
}

export interface CompletedOrder {
  menu_item_id: number;
  quantity: number;
  completed_at: Date;
}

export interface PredictionData {
  menu_item_id: number;
  hour: number; // 0-23
  predicted_units: number;
}

export interface InventoryItem {
  item_id: number;
  item_name: string;
  category: string;
  
  // PAST REALITY (Static for the day)
  opening_stock: number;
  completed_orders_today: number;
  
  // PRESENT STATE (Dynamic)
  remaining_stock: number;
  
  // FUTURE EXPECTATION (Predictive)
  predicted_future_demand: number | null; // null = no forecast available
  projected_stock: number | null; // null = cannot calculate without forecast

  // RECOMMENDATION (Guidance)
  suggested_stock_to_add?: number;
  
  // DERIVED METRICS
  days_of_supply: number | null; // null = cannot calculate without forecast
  inventory_status: 'Out of Stock' | 'Needs Restocking' | 'Well Stocked' | 'No Forecast';
  recommended_action: string;
  risk_level: 'Low' | 'Medium' | 'High' | 'Unknown';
}

export interface InventoryKPIs {
  total_items: number;
  well_stocked: number;
  needs_restocking: number;
  out_of_stock: number;
  no_forecast: number; // New: count items with no forecast data
  avg_days_of_supply: number | null; // null = cannot calculate
  stock_health_score: number | null; // null = cannot calculate
}

/**
 * Calculate inventory for a single menu item
 * Following the core principle: past reality + present state + future expectation
 * NEVER treats missing data as zero
 */
export function calculateInventoryItem(
  menuItem: MenuItemData,
  completedOrders: CompletedOrder[],
  predictions: PredictionData[],
  currentHour: number,
  averageDailyDemand: number | null = null // null = no average available
): InventoryItem {
  // 1) REMAINING STOCK (Present State)
  // opening_stock - completed_orders_quantity (so far)
  const completedOrdersToday = completedOrders
    .filter(order => order.menu_item_id === menuItem.id)
    .reduce((sum, order) => sum + order.quantity, 0);
  
  const remainingStock = menuItem.opening_stock - completedOrdersToday;

  // 2) PREDICTED FUTURE DEMAND (Future Expectation)
  // sum(predicted_units) from current hour → end of day
  const itemPredictions = predictions.filter(pred => 
    pred.menu_item_id === menuItem.id && 
    pred.hour >= currentHour // ONLY future hours, never past
  );
  
  let predictedFutureDemand: number | null = null;
  if (itemPredictions.length > 0) {
    const total = itemPredictions.reduce((sum, pred) => sum + pred.predicted_units, 0);
    // Only treat as valid if we have actual prediction data
    predictedFutureDemand = total;
  }
  // If no predictions exist, predictedFutureDemand remains null

  // 3) PROJECTED STOCK (Future expectation)
  // Only calculate if we have valid predictions
  let projectedStock: number | null = null;
  if (predictedFutureDemand !== null) {
    projectedStock = remainingStock - predictedFutureDemand;
  }

  // 4) STATUS DETERMINATION
  let inventoryStatus: 'Out of Stock' | 'Needs Restocking' | 'Well Stocked' | 'No Forecast';
  let recommendedAction: string;
  let riskLevel: 'Low' | 'Medium' | 'High' | 'Unknown';
  let daysOfSupply: number | null = null;

  // CORE LOGIC: Handle missing forecast data explicitly
  if (predictedFutureDemand === null) {
    // No forecast available - this is NOT the same as zero demand
    inventoryStatus = 'No Forecast';
    recommendedAction = 'Forecast unavailable for selected filters';
    riskLevel = 'Unknown';
    daysOfSupply = null; // Cannot calculate without forecast
  } else if (remainingStock <= 0) {
    inventoryStatus = 'Out of Stock';
    recommendedAction = 'Item unavailable. Immediate restock required.';
    riskLevel = 'High';
    daysOfSupply = 0; // No stock = 0 days
  } else if (projectedStock !== null && projectedStock <= 0) {
    inventoryStatus = 'Needs Restocking';
    recommendedAction = 'Urgent restocking required to meet expected demand.';
    riskLevel = projectedStock <= -5 ? 'High' : 'Medium';
    // Calculate days of supply only if we have valid average demand
    if (averageDailyDemand !== null && averageDailyDemand > 0) {
      daysOfSupply = remainingStock / averageDailyDemand;
    } else {
      daysOfSupply = null;
    }
  } else {
    inventoryStatus = 'Well Stocked';
    recommendedAction = 'Stock levels sufficient for predicted demand.';
    
    // Calculate days of supply only if we have valid average demand
    if (averageDailyDemand !== null && averageDailyDemand > 0) {
      daysOfSupply = remainingStock / averageDailyDemand;
      
      // Determine risk level based on buffer
      const stockBuffer = projectedStock !== null ? projectedStock / remainingStock : 0;
      if (stockBuffer > 0.5) {
        riskLevel = 'Low';
      } else if (stockBuffer > 0.2) {
        riskLevel = 'Medium';
      } else {
        riskLevel = 'High';
      }
    } else {
      riskLevel = 'Unknown';
      daysOfSupply = null;
    }
  }

  return {
    item_id: menuItem.id,
    item_name: menuItem.name,
    category: menuItem.category,
    
    // PAST REALITY
    opening_stock: menuItem.opening_stock,
    completed_orders_today: completedOrdersToday,
    
    // PRESENT STATE
    remaining_stock: remainingStock,
    
    // FUTURE EXPECTATION
    predicted_future_demand: predictedFutureDemand,
    projected_stock: projectedStock,
    
    // DERIVED METRICS
    days_of_supply: daysOfSupply,
    inventory_status: inventoryStatus,
    recommended_action: recommendedAction,
    risk_level: riskLevel,
  };
}

/**
 * Calculate inventory for all menu items
 */
export function calculateInventory(
  menuItems: MenuItemData[],
  completedOrders: CompletedOrder[],
  predictions: PredictionData[],
  currentHour: number,
  averageDailyDemands: Record<number, number> = {}
): InventoryItem[] {
  return menuItems.map(menuItem => 
    calculateInventoryItem(
      menuItem,
      completedOrders,
      predictions,
      currentHour,
      averageDailyDemands[menuItem.id] || 10
    )
  );
}

/**
 * Calculate global inventory aggregates (Inventory Summary)
 * NEVER treats missing data as zero
 */
export function calculateInventoryKPIs(inventoryItems: InventoryItem[]): InventoryKPIs {
  const totalItems = inventoryItems.length;
  
  const wellStocked = inventoryItems.filter(item => 
    item.inventory_status === 'Well Stocked'
  ).length;
  
  const needsRestocking = inventoryItems.filter(item => 
    item.inventory_status === 'Needs Restocking'
  ).length;
  
  const outOfStock = inventoryItems.filter(item => 
    item.inventory_status === 'Out of Stock'
  ).length;

  // NEW: Count items with no forecast data
  const noForecast = inventoryItems.filter(item => 
    item.inventory_status === 'No Forecast'
  ).length;

  // Average Days of Supply - calculate ONLY from items with valid days_of_supply
  const itemsWithValidDaysOfSupply = inventoryItems.filter(item => 
    item.days_of_supply !== null && item.days_of_supply >= 0
  );
  
  const avgDaysOfSupply = itemsWithValidDaysOfSupply.length > 0
    ? itemsWithValidDaysOfSupply.reduce((sum, item) => sum + item.days_of_supply!, 0) / itemsWithValidDaysOfSupply.length
    : null;

  // Overall Stock Health Score - calculate ONLY if we have meaningful data
  // Base score on percentage of items with valid status (excluding No Forecast)
  const itemsWithValidStatus = totalItems - noForecast;
  let stockHealthScore: number | null = null;
  
  if (itemsWithValidStatus > 0) {
    const wellStockedPercentage = (wellStocked / itemsWithValidStatus) * 100;
    const daysOfSupplyScore = avgDaysOfSupply !== null ? Math.min(100, avgDaysOfSupply * 10) : 0; // 10 days = 100%
    stockHealthScore = (wellStockedPercentage * 0.7) + (daysOfSupplyScore * 0.3);
  }

  return {
    total_items: totalItems,
    well_stocked: wellStocked,
    needs_restocking: needsRestocking,
    out_of_stock: outOfStock,
    no_forecast: noForecast,
    avg_days_of_supply: avgDaysOfSupply,
    stock_health_score: stockHealthScore,
  };
}

/**
 * Time-aware inventory recompute logic
 * Call this whenever:
 * - Current time changes
 * - Orders are completed
 * - Predictions update
 * - Date range changes
 */
export function recomputeInventory(
  menuItems: MenuItemData[],
  completedOrders: CompletedOrder[],
  predictions: PredictionData[],
  currentHour: number,
  averageDailyDemands: Record<number, number> = {}
): {
  inventoryItems: InventoryItem[];
  kpis: InventoryKPIs;
} {
  const inventoryItems = calculateInventory(
    menuItems,
    completedOrders,
    predictions,
    currentHour,
    averageDailyDemands
  );
  
  const kpis = calculateInventoryKPIs(inventoryItems);
  
  return { inventoryItems, kpis };
}

/**
 * Get current hour in IST (or specified timezone)
 */
export function getCurrentHour(timezoneOffset: number = 5.5): number {
  const now = new Date();
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
  const localTime = new Date(utcTime + (3600000 * timezoneOffset));
  return localTime.getHours();
}

/**
 * Filter predictions to only include future hours
 * ANTI-PATTERN: Never include past predicted hours
 */
export function filterFuturePredictions(
  predictions: PredictionData[],
  currentHour: number
): PredictionData[] {
  return predictions.filter(pred => pred.hour >= currentHour);
}

/**
 * Validate inventory calculation (for testing/debugging)
 */
export function validateInventoryCalculation(inventoryItem: InventoryItem): string[] {
  const errors: string[] = [];
  
  // Check for negative values that shouldn't be negative
  if (inventoryItem.opening_stock < 0) {
    errors.push('Opening stock cannot be negative');
  }
  
  if (inventoryItem.completed_orders_today < 0) {
    errors.push('Completed orders cannot be negative');
  }
  
  if (inventoryItem.predicted_future_demand < 0) {
    errors.push('Predicted demand cannot be negative');
  }
  
  // Check calculation consistency
  const expectedRemainingStock = inventoryItem.opening_stock - inventoryItem.completed_orders_today;
  if (Math.abs(inventoryItem.remaining_stock - expectedRemainingStock) > 0.01) {
    errors.push('Remaining stock calculation mismatch');
  }
  
  const expectedProjectedStock = inventoryItem.remaining_stock - inventoryItem.predicted_future_demand;
  if (Math.abs(inventoryItem.projected_stock - expectedProjectedStock) > 0.01) {
    errors.push('Projected stock calculation mismatch');
  }
  
  // Check status logic
  if (inventoryItem.remaining_stock <= 0 && inventoryItem.inventory_status !== 'Out of Stock') {
    errors.push('Should be Out of Stock when remaining stock <= 0');
  }
  
  if (inventoryItem.remaining_stock > 0 && 
      inventoryItem.projected_stock <= 0 && 
      inventoryItem.inventory_status !== 'Needs Restocking') {
    errors.push('Should be Needs Restocking when projected stock <= 0');
  }
  
  if (inventoryItem.remaining_stock > 0 && 
      inventoryItem.projected_stock > 0 && 
      inventoryItem.inventory_status !== 'Well Stocked') {
    errors.push('Should be Well Stocked when both stocks > 0');
  }
  
  return errors;
}
