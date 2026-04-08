import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useOrders, OrderStatus } from '@/contexts/OrderContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { KitchenAnalyticsMinimal as KitchenAnalytics } from '@/components/kitchen/KitchenAnalyticsMinimal';
import { ProfileButton } from '@/components/ui/Profile';
import {
  ChefHat,
  Clock,
  CheckCircle2,
  PlayCircle,
  Package,
  LogOut,
  RefreshCcw,
  User,
  Loader2,
  Trash2,
  BarChart3,
  Eye,
  EyeOff
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { 
  formatISTTime, 
  formatISTDate, 
  getCurrentISTTime, 
  getCurrentISTDate,
  getOrderTimeDisplay 
} from '@/utils/istTime';

const statusConfig: Record<OrderStatus, { label: string; color: string; icon: typeof Clock }> = {
  pending: { label: 'Pending', color: 'bg-yellow-500', icon: Clock },
  preparing: { label: 'Preparing', color: 'bg-blue-500', icon: PlayCircle },
  ready: { label: 'Ready', color: 'bg-primary', icon: Package },
  completed: { label: 'Completed', color: 'bg-muted', icon: CheckCircle2 },
};

const statusFlow: OrderStatus[] = ['pending', 'preparing', 'ready', 'completed'];

export default function Kitchen() {
  const { user, logout } = useAuth();
  const { orders, updateOrderStatus, fetchAllOrders, deleteOrder } = useOrders();
  const navigate = useNavigate();
  const [updatingOrders, setUpdatingOrders] = useState<Set<string>>(new Set());
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showAnalytics, setShowAnalytics] = useState(false);

  const activeOrders = orders.filter(o => o.status !== 'completed');
  
  // State for toggle between today's orders and last 30 days
  const [showTodayOnly, setShowTodayOnly] = useState(true);
  
  // Get today's date in IST for comparison using utility functions
  const todayDateString = getCurrentISTDate();
  console.log('📅 Today\'s date (IST):', todayDateString);
  
  // Filter completed orders based on toggle
  const completedOrders = orders.filter(o => o.status === 'completed');
  const todayCompletedOrders = completedOrders.filter(order => {
    // Get current date in IST (YYYY-MM-DD format for comparison)
    const now = new Date();
    const utcTime = now.getTime();
    const istOffset = 5.5 * 60 * 60 * 1000;
    const istNow = new Date(utcTime + istOffset);
    const todayISTString = istNow.toISOString().split('T')[0];
    
    // Convert order date to IST and get YYYY-MM-DD format
    const orderUtcTime = order.createdAt.getTime();
    const orderIstTime = new Date(orderUtcTime + istOffset);
    const orderISTString = orderIstTime.toISOString().split('T')[0];
    
    console.log('🔍 Date comparison (fixed):', {
      orderId: order.id,
      orderCreatedAt: order.createdAt,
      orderISTString: orderISTString,
      todayISTString: todayISTString,
      isToday: orderISTString === todayISTString,
      displayDate: formatISTDate(order.createdAt)
    });
    
    return orderISTString === todayISTString;
  });
  
  // Get orders from last 30 days
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const last30DaysOrders = completedOrders
    .filter(o => new Date(o.createdAt) >= thirtyDaysAgo)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  
  // Use appropriate orders based on toggle
  const displayOrders = showTodayOnly ? todayCompletedOrders.slice(0, 5) : last30DaysOrders;
  
  console.log('📊 Order counts:', {
    totalOrders: orders.length,
    activeOrders: activeOrders.length,
    completedOrders: completedOrders.length,
    todayCompletedOrders: todayCompletedOrders.length,
    last30DaysOrders: last30DaysOrders.length,
    showTodayOnly: showTodayOnly,
    displayOrders: displayOrders.length
  });

  // Update current time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Update every minute

    return () => clearInterval(timer);
  }, []);

  const handleStatusUpdate = async (orderId: string, currentStatus: OrderStatus) => {
    const currentIndex = statusFlow.indexOf(currentStatus);
    if (currentIndex < statusFlow.length - 1) {
      const nextStatus = statusFlow[currentIndex + 1];
      
      // Add to updating set to show loading state
      setUpdatingOrders(prev => new Set(prev).add(orderId));
      
      try {
        await updateOrderStatus(orderId, nextStatus);
        toast.success(`Order updated to ${statusConfig[nextStatus].label}`);
      } catch (error) {
        console.error('Failed to update order status:', error);
        toast.error('Failed to update order status. Please try again.');
      } finally {
        // Remove from updating set
        setUpdatingOrders(prev => {
          const newSet = new Set(prev);
          newSet.delete(orderId);
          return newSet;
        });
      }
    }
  };

  const handleRefresh = async () => {
    try {
      await fetchAllOrders();
      toast.success('Orders refreshed successfully');
    } catch (error) {
      console.error('Failed to refresh orders:', error);
      toast.error('Failed to refresh orders');
    }
  };

  const handleDeleteOrder = async (orderId: string) => {
    if (window.confirm('Are you sure you want to delete this completed order? This action cannot be undone.')) {
      try {
        await deleteOrder(orderId);
        toast.success('Order deleted successfully');
      } catch (error) {
        console.error('Failed to delete order:', error);
        toast.error('Failed to delete order. Please try again.');
      }
    }
  };

  // Fetch all orders on component mount
  useEffect(() => {
    console.log('🍳 Kitchen page mounting, fetching all orders...');
    fetchAllOrders();
  }, []);

  // Update derived state when orders change
  useEffect(() => {
    console.log('📋 Orders updated:', orders.length);
    console.log('📋 Order details:', orders.map(o => ({
      id: o.id,
      status: o.status,
      userName: o.userName,
      createdAt: o.createdAt,
      items: o.items.length
    })));
  }, [orders]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Debug function for analytics button
  const handleToggleAnalytics = () => {
    const newState = !showAnalytics;
    console.log('🔍 Analytics button clicked:', {
      newState,
      currentState: showAnalytics,
      timestamp: new Date().toISOString(),
      ordersCount: orders.length,
      activeOrdersCount: activeOrders.length
    });
    setShowAnalytics(newState);
  };

  // Add debug logging for showAnalytics changes
  useEffect(() => {
    console.log('📊 showAnalytics state changed:', {
      showAnalytics,
      timestamp: new Date().toISOString()
    });
  }, [showAnalytics]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-md border-b shadow-soft">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 gradient-secondary rounded-xl">
                <ChefHat className="h-6 w-6 text-secondary-foreground" />
              </div>
              <div>
                <h1 className="font-bold text-lg text-foreground">Kitchen Dashboard</h1>
                <p className="text-xs text-muted-foreground">Welcome, {user?.fullname}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant={showAnalytics ? "default" : "outline"}
                size="sm"
                onClick={handleToggleAnalytics}
                className="h-8"
              >
                {showAnalytics ? <EyeOff className="h-3 w-3 mr-1" /> : <Eye className="h-3 w-3 mr-1" />}
                {showAnalytics ? 'Hide Analytics' : 'Show Analytics'}
              </Button>
              
              <Badge variant="secondary" className="h-8">
                <RefreshCcw className="h-3 w-3 mr-1" />
                {activeOrders.length} Active Orders
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="h-8"
              >
                <RefreshCcw className="h-3 w-3 mr-1" />
                Refresh
              </Button>
              
              <ProfileButton />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Kitchen Analytics Section */}
        {showAnalytics && (
          <div className="mb-8">
            <KitchenAnalytics />
          </div>
        )}

        {/* Status Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {statusFlow.slice(0, 3).map((status) => {
            const config = statusConfig[status];
            const statusOrders = orders.filter(o => o.status === status);

            return (
              <div key={status} className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className={cn("w-3 h-3 rounded-full", config.color)} />
                  <h2 className="font-semibold text-foreground">{config.label}</h2>
                  <Badge variant="outline" className="ml-auto">
                    {statusOrders.length}
                  </Badge>
                </div>

                <div className="space-y-3 min-h-[200px]">
                  {statusOrders.map((order, index) => (
                    <motion.div
                      key={order.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="bg-card rounded-xl border p-4 shadow-soft hover:shadow-card transition-all"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="p-1.5 bg-muted rounded-lg">
                            <User className="h-4 w-4 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="font-medium text-sm">
                              {order.userName || `User ${order.userId}`}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              #{order.id.slice(-4)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant="secondary" className="text-xs mb-1">
                            <Clock className="h-3 w-3 mr-1" />
                            {getOrderTimeDisplay(order, currentTime).estimatedTime || `${order.estimatedTime} min`}
                          </Badge>
                          <div className="text-xs text-muted-foreground">
                            {getOrderTimeDisplay(order, currentTime).time}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-1 mb-3">
                        {order.items.map((item) => (
                          <div key={item.menuItem.id} className="flex justify-between text-sm">
                            <span className="text-muted-foreground">
                              {item.quantity}x {item.menuItem.name}
                            </span>
                          </div>
                        ))}
                      </div>

                      <Button
                        size="sm"
                        className={cn(
                          "w-full",
                          status === 'pending' && "gradient-secondary text-secondary-foreground",
                          status === 'preparing' && "gradient-primary text-primary-foreground",
                          status === 'ready' && "bg-primary text-primary-foreground"
                        )}
                        onClick={() => handleStatusUpdate(order.id, status)}
                        disabled={updatingOrders.has(order.id)}
                      >
                        {updatingOrders.has(order.id) ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Updating...
                          </>
                        ) : (
                          <>
                            {status === 'pending' && 'Start Preparing'}
                            {status === 'preparing' && 'Mark Ready'}
                            {status === 'ready' && 'Complete Order'}
                          </>
                        )}
                      </Button>
                    </motion.div>
                  ))}

                  {statusOrders.length === 0 && (
                    <div className="flex items-center justify-center h-32 border-2 border-dashed rounded-xl">
                      <p className="text-sm text-muted-foreground">No orders</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Completed Orders with Toggle */}
        {completedOrders.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-foreground flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-primary" />
                {showTodayOnly ? 'Today\'s Completed Orders' : 'Last 30 Days Orders'}
              </h2>
              <div className="flex items-center gap-2">
                <Button
                  variant={showTodayOnly ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowTodayOnly(true)}
                  className="h-8"
                >
                  Today
                </Button>
                <Button
                  variant={!showTodayOnly ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowTodayOnly(false)}
                  className="h-8"
                >
                  Last 30 Days
                </Button>
              </div>
            </div>
            
            {showTodayOnly ? (
              // Today's completed orders - grid layout
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {displayOrders.map((order) => (
                  <div
                    key={order.id}
                    className="bg-muted/50 rounded-lg p-3 flex items-center gap-3"
                  >
                    <CheckCircle2 className="h-5 w-5 text-primary" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">{order.userName}</p>
                      <p className="text-xs text-muted-foreground">
                        {order.items.length} items • ₹{order.totalPrice.toFixed(2)}
                      </p>
                      <p className="text-xs text-primary font-medium">
                        {formatISTDate(order.createdAt)}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteOrder(order.id)}
                      className="h-6 w-6 text-red-500 hover:text-red-700 hover:bg-red-50"
                      title="Delete order"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              // Last 30 days orders - list layout
              <div className="bg-card rounded-xl border p-4">
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {displayOrders.map((order) => (
                    <div
                      key={order.id}
                      className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="h-4 w-4 text-primary" />
                        <div>
                          <p className="font-medium text-sm">{order.userName}</p>
                          <p className="text-xs text-muted-foreground">
                            #{order.id.slice(-4)} • {order.items.length} items • ₹{order.totalPrice.toFixed(2)}
                          </p>
                          <p className="text-xs text-primary font-medium">
                            {formatISTDate(order.createdAt)} • {formatISTTime(order.createdAt)}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteOrder(order.id)}
                        className="h-6 w-6 text-red-500 hover:text-red-700 hover:bg-red-50"
                        title="Delete order"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {displayOrders.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="font-medium">
                  {showTodayOnly ? 'No orders completed today' : 'No orders in the last 30 days'}
                </p>
                <p className="text-sm">
                  {showTodayOnly 
                    ? 'Completed orders will appear here throughout the day' 
                    : 'Completed orders from the past month will appear here'
                  }
                </p>
              </div>
            )}
          </div>
        )}

        {orders.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <ChefHat className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-xl text-foreground mb-2">No Orders Yet</h3>
            <p className="text-muted-foreground">Orders will appear here when customers place them</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
