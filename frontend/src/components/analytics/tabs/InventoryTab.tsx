import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { 
  Package, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  AlertCircle,
  Clock,
  Eye,
  Plus,
} from 'lucide-react';
import { InventoryItem, InventoryKPIs } from '@/utils/inventoryCalculations';

// Use the proper interfaces from inventoryCalculations.ts
interface InventoryTabProps {
  kpis: InventoryKPIs;
  items: InventoryItem[];
  isReadOnly: boolean;
  onStockUpdate?: () => void; // Callback to refresh data after update
}

interface StockUpdate {
  quantity: number;
  reason: 'restock' | 'correction' | 'wastage';
}

const InventoryTab: React.FC<InventoryTabProps> = ({ kpis, items, isReadOnly, onStockUpdate }) => {
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [stockUpdate, setStockUpdate] = useState<StockUpdate>({ quantity: 0, reason: 'restock' });
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const getRiskColor = (riskLevel: 'Low' | 'Medium' | 'High' | 'Unknown') => {
    switch (riskLevel) {
      case 'Low': return 'text-green-600 bg-green-50';
      case 'Medium': return 'text-yellow-600 bg-yellow-50';
      case 'High': return 'text-red-600 bg-red-50';
      case 'Unknown': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (riskLevel: 'Low' | 'Medium' | 'High' | 'Unknown') => {
    switch (riskLevel) {
      case 'Low': return <CheckCircle className="h-4 w-4" />;
      case 'Medium': return <AlertCircle className="h-4 w-4" />;
      case 'High': return <AlertTriangle className="h-4 w-4" />;
      case 'Unknown': return <AlertCircle className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: 'Out of Stock' | 'Needs Restocking' | 'Well Stocked' | 'No Forecast') => {
    switch (status) {
      case 'Well Stocked': return 'bg-green-100 text-green-800 border-green-200';
      case 'Needs Restocking': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Out of Stock': return 'bg-red-100 text-red-800 border-red-200';
      case 'No Forecast': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: 'Out of Stock' | 'Needs Restocking' | 'Well Stocked' | 'No Forecast') => {
    switch (status) {
      case 'Well Stocked': return <CheckCircle className="h-3 w-3" />;
      case 'Needs Restocking': return <AlertTriangle className="h-3 w-3" />;
      case 'Out of Stock': return <XCircle className="h-3 w-3" />;
      case 'No Forecast': return <AlertCircle className="h-3 w-3" />;
      default: return <AlertCircle className="h-3 w-3" />;
    }
  };

  // Group items by status and sort by stock level ascending
  const groupedItems = {
    needsRestocking: items
      .filter(item => item.inventory_status === 'Needs Restocking')
      .sort((a, b) => a.remaining_stock - b.remaining_stock),
    wellStocked: items
      .filter(item => item.inventory_status === 'Well Stocked')
      .sort((a, b) => a.remaining_stock - b.remaining_stock),
    outOfStock: items
      .filter(item => item.inventory_status === 'Out of Stock')
      .sort((a, b) => a.remaining_stock - b.remaining_stock),
    noForecast: items
      .filter(item => item.inventory_status === 'No Forecast')
      .sort((a, b) => a.remaining_stock - b.remaining_stock)
  };

  const handleViewItem = (item: InventoryItem) => {
    setSelectedItem(item);
    setIsViewModalOpen(true);
    setStockUpdate({ quantity: 0, reason: 'restock' });
  };

  const requestStockUpdate = () => {
    if (!selectedItem || stockUpdate.quantity === 0) return;
    setIsConfirmOpen(true);
  };

  const applyStockUpdate = async () => {
    if (!selectedItem || stockUpdate.quantity === 0) return;

    setIsApplying(true);
    setUpdateError(null);
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const response = await fetch(`${API_URL}/api/inventory/stock-update`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          menu_item_id: selectedItem.item_id,
          set_stock_quantity: stockUpdate.quantity,
          reason: stockUpdate.reason,
          confirmed: true
        })
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || 'Failed to apply stock update');
      }

      const result = await response.json();
      console.log('✅ Stock update successful:', result);

      // Show success message
      alert(`Stock updated successfully!\n\nItem: ${result.item_name}\nPrevious: ${result.previous_stock}\nNew: ${result.new_stock}\nChange: ${result.quantity_delta > 0 ? '+' : ''}${result.quantity_delta}\nReason: ${result.reason}`);

      // Reset after successful apply
      setIsConfirmOpen(false);
      setStockUpdate({ quantity: 0, reason: 'restock' });
      setIsViewModalOpen(false);

      // Trigger parent component to refresh data
      if (onStockUpdate) {
        onStockUpdate();
      } else {
        // Fallback to reload if no callback provided
        window.location.reload();
      }
    } catch (error) {
      console.error('❌ Stock update failed:', error);
      setUpdateError(error instanceof Error ? error.message : 'Failed to update stock');
      alert(`Error updating stock: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsApplying(false);
    }
  };

  const syncInventoryFromOrders = async () => {
    setIsSyncing(true);
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('Authentication token not found. Please login again.');
      }

      console.log('🔄 Starting inventory sync...');
      const response = await fetch(`${API_URL}/api/inventory/sync-inventory`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Sync response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Sync failed response:', errorText);
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (response.status === 403) {
          throw new Error('You do not have permission to sync inventory. Admin access required.');
        } else if (response.status === 500) {
          throw new Error('Server error occurred. Please check the backend logs or try again later.');
        } else {
          throw new Error(`Sync failed (${response.status}): ${errorText || 'Unknown error'}`);
        }
      }

      const result = await response.json();
      console.log('✅ Inventory sync successful:', result);

      // Show success message
      alert(`Inventory sync completed successfully!\n\nSynced at: ${new Date(result.synced_at).toLocaleString()}`);

      // Refresh the data
      if (onStockUpdate) {
        onStockUpdate();
      } else {
        console.log('🔄 No callback provided, reloading page...');
        window.location.reload();
      }
    } catch (error) {
      console.error('❌ Inventory sync failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Error syncing inventory:\n\n${errorMessage}\n\nPlease check:\n1. You are logged in as admin/superadmin\n2. Backend server is running\n3. Network connection is stable`);
    } finally {
      setIsSyncing(false);
    }
  };

  const getRecommendedAction = (item: InventoryItem) => {
    if (item.inventory_status === 'Out of Stock') {
      return 'Immediate restocking required';
    } else if (item.inventory_status === 'Needs Restocking') {
      return 'Restock before peak hours';
    } else {
      return 'No action required';
    }
  };

  const suggestedToAdd = selectedItem?.suggested_stock_to_add || 0;

  return (
    <div className="space-y-6">
      {/* Compact KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <Card className="shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Items</p>
                <p className="text-2xl font-bold text-gray-900">{kpis.total_items}</p>
              </div>
              <Package className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Needs Restocking</p>
                <p className="text-2xl font-bold text-yellow-600">{kpis.needs_restocking}</p>
              </div>
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Out of Stock</p>
                <p className="text-2xl font-bold text-red-600">{kpis.out_of_stock}</p>
              </div>
              <XCircle className="h-5 w-5 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">No Forecast</p>
                <p className="text-2xl font-bold text-gray-600">{kpis.no_forecast || 0}</p>
              </div>
              <AlertCircle className="h-5 w-5 text-gray-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Avg Days Supply</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis.avg_days_of_supply !== null ? kpis.avg_days_of_supply.toFixed(1) : '—'}
                </p>
              </div>
              <Clock className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sync Controls */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          <p>Inventory data is automatically updated when orders are completed.</p>
          <p className="text-xs mt-1">Last sync: {new Date().toLocaleString()}</p>
        </div>
        <Button 
          onClick={syncInventoryFromOrders}
          disabled={isSyncing || isReadOnly}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <Clock className="h-4 w-4" />
          {isSyncing ? 'Syncing...' : 'Sync Inventory'}
        </Button>
      </div>

      {/* Grouped Inventory Items */}
      <div className="space-y-6">
        {/* Needs Restocking - Highest Priority */}
        {groupedItems.needsRestocking.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <h3 className="text-sm font-semibold text-yellow-800 uppercase tracking-wide">Needs Restocking</h3>
              <Badge variant="outline" className="text-xs">{groupedItems.needsRestocking.length}</Badge>
            </div>
            <div className="space-y-2">
              {groupedItems.needsRestocking.map((item, index) => (
                <InventoryItemCard 
                  key={`needs-${item.item_id}`} 
                  item={item} 
                  onView={() => handleViewItem(item)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Well Stocked */}
        {groupedItems.wellStocked.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <h3 className="text-sm font-semibold text-green-800 uppercase tracking-wide">Well Stocked</h3>
              <Badge variant="outline" className="text-xs">{groupedItems.wellStocked.length}</Badge>
            </div>
            <div className="space-y-2">
              {groupedItems.wellStocked.map((item, index) => (
                <InventoryItemCard 
                  key={`well-${item.item_id}`} 
                  item={item} 
                  onView={() => handleViewItem(item)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Out of Stock */}
        {groupedItems.outOfStock.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <XCircle className="h-4 w-4 text-red-600" />
              <h3 className="text-sm font-semibold text-red-800 uppercase tracking-wide">Out of Stock</h3>
              <Badge variant="outline" className="text-xs">{groupedItems.outOfStock.length}</Badge>
            </div>
            <div className="space-y-2">
              {groupedItems.outOfStock.map((item, index) => (
                <InventoryItemCard 
                  key={`out-${item.item_id}`} 
                  item={item} 
                  onView={() => handleViewItem(item)}
                />
              ))}
            </div>
          </div>
        )}

        {/* No Forecast */}
        {groupedItems.noForecast.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="h-4 w-4 text-gray-600" />
              <h3 className="text-sm font-semibold text-gray-800 uppercase tracking-wide">No Forecast</h3>
              <Badge variant="outline" className="text-xs">{groupedItems.noForecast.length}</Badge>
            </div>
            <div className="space-y-2">
              {groupedItems.noForecast.map((item, index) => (
                <InventoryItemCard 
                  key={`no-forecast-${item.item_id}`} 
                  item={item} 
                  onView={() => handleViewItem(item)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* View Modal */}
      <Dialog open={isViewModalOpen} onOpenChange={setIsViewModalOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold">Inventory Details</DialogTitle>
          </DialogHeader>
          
          {selectedItem && (
            <div className="space-y-8 mt-6">
              {/* Item Overview */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Item Overview</h3>
                <div className="flex items-center gap-4 mb-6">
                  <div className="flex-1">
                    <h4 className="text-2xl font-bold text-gray-900 mb-2">{selectedItem.item_name}</h4>
                    <Badge variant="outline" className="text-sm px-3 py-1">{selectedItem.category}</Badge>
                  </div>
                  <Badge className={`${getStatusColor(selectedItem.inventory_status)} px-4 py-2 text-sm`}>
                    {getStatusIcon(selectedItem.inventory_status)}
                    <span className="ml-2 font-medium">{selectedItem.inventory_status}</span>
                  </Badge>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="text-center p-6 bg-gray-50 rounded-xl border border-gray-200">
                    <p className="text-4xl font-bold text-gray-900 mb-2">{selectedItem.remaining_stock}</p>
                    <p className="text-base font-medium text-gray-600">Remaining Stock</p>
                  </div>
                  <div className="text-center p-6 bg-gray-50 rounded-xl border border-gray-200">
                    <p className="text-4xl font-bold text-gray-900 mb-2">
                      {selectedItem.days_of_supply !== null ? selectedItem.days_of_supply.toFixed(1) : '—'}
                    </p>
                    <p className="text-base font-medium text-gray-600">Days of Supply</p>
                  </div>
                </div>
              </div>

              {/* Stock Breakdown */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Stock Breakdown</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <span className="text-base font-medium text-gray-700">Opening Stock (Start of Day)</span>
                    <span className="text-lg font-semibold text-gray-900">{selectedItem.opening_stock}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <span className="text-base font-medium text-blue-700">Completed Orders (Today)</span>
                    <span className="text-lg font-semibold text-blue-600">{selectedItem.completed_orders_today}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg border border-green-200">
                    <span className="text-base font-medium text-green-700">Remaining Stock</span>
                    <span className="text-lg font-semibold text-green-600">{selectedItem.remaining_stock}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <span className="text-base font-medium text-orange-700">Predicted Future Demand</span>
                    <span className="text-lg font-semibold text-orange-600">
                      {selectedItem.predicted_future_demand !== null ? selectedItem.predicted_future_demand : 'No forecast'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <span className="text-base font-medium text-purple-700">Projected Stock (After Predictions)</span>
                    <span className="text-lg font-semibold text-purple-600">
                      {selectedItem.projected_stock !== null ? selectedItem.projected_stock : '—'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Update Stock */}
              {!isReadOnly && (
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-gray-900">Update Stock</h3>
                  <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                    {updateError && (
                      <div className="mb-4 p-4 rounded-lg border border-red-200 bg-red-50">
                        <p className="text-sm font-medium text-red-900">Error: {updateError}</p>
                      </div>
                    )}
                    {suggestedToAdd > 0 && (
                      <div className="mb-6 p-4 rounded-lg border border-yellow-200 bg-yellow-50">
                        <p className="text-sm font-medium text-yellow-900">Recommended based on predicted demand</p>
                        <p className="text-sm text-yellow-800 mt-1">Suggested stock to add: <span className="font-semibold">+{suggestedToAdd}</span></p>
                      </div>
                    )}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Label htmlFor="quantity" className="text-base font-medium text-gray-700">Set Stock Quantity</Label>
                        <Input
                          id="quantity"
                          type="number"
                          value={stockUpdate.quantity || ''}
                          onChange={(e) => setStockUpdate(prev => ({ ...prev, quantity: parseInt(e.target.value) || 0 }))}
                          placeholder="Enter new stock quantity"
                          className="mt-2 h-11 text-base"
                          disabled={isApplying}
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="reason" className="text-base font-medium text-gray-700">Reason</Label>
                        <Select value={stockUpdate.reason} onValueChange={(value: 'restock' | 'correction' | 'wastage') => setStockUpdate(prev => ({ ...prev, reason: value }))} disabled={isApplying}>
                          <SelectTrigger className="mt-2 h-11 text-base">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="restock">Restock</SelectItem>
                            <SelectItem value="correction">Correction</SelectItem>
                            <SelectItem value="wastage">Wastage</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    
                    <Button 
                      onClick={requestStockUpdate}
                      disabled={stockUpdate.quantity === 0 || isApplying}
                      className="w-full mt-6 h-12 text-base font-medium"
                      size="lg"
                    >
                      {isApplying ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Updating...
                        </>
                      ) : (
                        <>
                          <Plus className="h-5 w-5 mr-2" />
                          Apply Update
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}

              {/* Predictive Insights */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Predictive Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-base font-medium text-blue-800 mb-2">Peak Demand Window</p>
                    <p className="text-sm text-blue-600">Expected high demand between 12:00-14:00</p>
                  </div>
                  <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <p className="text-base font-medium text-yellow-800 mb-2">Risk Analysis</p>
                    <p className="text-sm text-yellow-600">Current stock levels may not cover peak hours</p>
                  </div>
                </div>
              </div>

              {/* Recommended Action */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Recommended Action</h3>
                <div className={`p-6 rounded-xl border-l-4 ${
                  selectedItem.inventory_status === 'Out of Stock' ? 'bg-red-50 border-red-400' :
                  selectedItem.inventory_status === 'Needs Restocking' ? 'bg-yellow-50 border-yellow-400' :
                  'bg-green-50 border-green-400'
                }`}>
                  <p className="text-lg font-medium">{getRecommendedAction(selectedItem)}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Confirmation (required) */}
      <AlertDialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm stock update</AlertDialogTitle>
            <AlertDialogDescription>
              This will create a new stock snapshot for this item. Historical data will be preserved.
              <br /><br />
              <strong>Item:</strong> {selectedItem?.item_name}<br />
              <strong>Current Stock:</strong> {selectedItem?.remaining_stock}<br />
              <strong>New Stock:</strong> {stockUpdate.quantity}<br />
              <strong>Change:</strong> {stockUpdate.quantity > selectedItem?.remaining_stock ? '+' : ''}{stockUpdate.quantity - (selectedItem?.remaining_stock || 0)}<br />
              <strong>Reason:</strong> {stockUpdate.reason}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isApplying}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={applyStockUpdate} disabled={isApplying}>
              {isApplying ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Applying...
                </>
              ) : (
                'Confirm & Apply'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

// Compact Inventory Item Card Component
const InventoryItemCard: React.FC<{ item: InventoryItem; onView: () => void }> = ({ item, onView }) => {
  const getStatusColor = (status: 'Out of Stock' | 'Needs Restocking' | 'Well Stocked' | 'No Forecast') => {
    switch (status) {
      case 'Well Stocked': return 'bg-green-100 text-green-800 border-green-200';
      case 'Needs Restocking': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Out of Stock': return 'bg-red-100 text-red-800 border-red-200';
      case 'No Forecast': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: 'Out of Stock' | 'Needs Restocking' | 'Well Stocked' | 'No Forecast') => {
    switch (status) {
      case 'Well Stocked': return <CheckCircle className="h-3 w-3" />;
      case 'Needs Restocking': return <AlertTriangle className="h-3 w-3" />;
      case 'Out of Stock': return <XCircle className="h-3 w-3" />;
      case 'No Forecast': return <AlertCircle className="h-3 w-3" />;
      default: return <AlertCircle className="h-3 w-3" />;
    }
  };

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          {/* LEFT: Item Info */}
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900">{item.item_name}</h4>
            <Badge variant="outline" className="text-xs mt-1">{item.category}</Badge>
          </div>

          {/* CENTER: Stock Info */}
          <div className="flex-1 text-center">
            <p className="text-2xl font-bold text-gray-900">{item.remaining_stock}</p>
            <p className="text-xs text-gray-500 mb-2">Remaining</p>
            <div className="w-full max-w-[100px] mx-auto">
              <Progress 
                value={item.days_of_supply !== null ? Math.min(100, (item.days_of_supply / 10) * 100) : 0} 
                className="h-2" 
              />
              <p className="text-xs text-gray-500 mt-1">
                {item.days_of_supply !== null ? `${item.days_of_supply.toFixed(1)} days` : '—'}
              </p>
            </div>
          </div>

          {/* RIGHT: Status & Actions */}
          <div className="flex-1 text-right">
            <div className="mb-2">
              <p className="text-xs text-gray-500">Predicted Demand</p>
              <p className="text-sm font-medium text-gray-700">
                {item.predicted_future_demand !== null ? item.predicted_future_demand : 'No forecast'}
              </p>
            </div>
            <div className="mb-3">
              <Badge className={getStatusColor(item.inventory_status)}>
                {getStatusIcon(item.inventory_status)}
                <span className="ml-1 text-xs">{item.inventory_status}</span>
              </Badge>
            </div>
            <Button size="sm" onClick={onView} className="text-xs">
              <Eye className="h-3 w-3 mr-1" />
              View
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default InventoryTab;
