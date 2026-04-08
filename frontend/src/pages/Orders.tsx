import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useOrders, OrderStatus } from '@/contexts/OrderContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  Clock,
  CheckCircle2,
  PlayCircle,
  Package,
  UtensilsCrossed,
  Flame,
  RefreshCw,
  Timer,
  Calendar,
  Trash2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProfileButton } from '@/components/ui/Profile';
import { 
  formatISTTime, 
  formatDateOnly, 
  calculateDynamicEstimatedTime,
  getOrderTimeDisplay 
} from '@/utils/istTime';

const statusConfig: Record<OrderStatus, { label: string; color: string; bgColor: string; icon: typeof Clock }> = {
  pending: { label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100', icon: Clock },
  preparing: { label: 'Preparing', color: 'text-blue-600', bgColor: 'bg-blue-100', icon: PlayCircle },
  ready: { label: 'Ready for Pickup', color: 'text-primary', bgColor: 'bg-accent', icon: Package },
  completed: { label: 'Completed', color: 'text-muted-foreground', bgColor: 'bg-muted', icon: CheckCircle2 },
};

// Helper function to get time display based on status
const getTimeDisplay = (order: any, currentTime: Date) => {
  const { status, estimatedTime, createdAt, startedPreparationAt, readyAt, completedAt } = order;
  
  if (status === 'completed') {
    return {
      icon: CheckCircle2,
      text: 'Completed',
      subtext: completedAt ? `at ${formatISTTime(completedAt)}` : '',
      color: 'text-green-600'
    };
  }
  
  if (status === 'ready') {
    return {
      icon: Package,
      text: 'Ready for Pickup',
      subtext: readyAt ? `since ${formatISTTime(readyAt)}` : '',
      color: 'text-primary'
    };
  }
  
  if (status === 'preparing') {
    return {
      icon: PlayCircle,
      text: calculateDynamicEstimatedTime(order, currentTime),
      subtext: startedPreparationAt ? `started ${formatISTTime(startedPreparationAt)}` : '',
      color: 'text-blue-600'
    };
  }
  
  if (status === 'pending') {
    return {
      icon: Clock,
      text: calculateDynamicEstimatedTime(order, currentTime),
      subtext: `Ordered at ${formatISTTime(createdAt)}`,
      color: 'text-yellow-600'
    };
  }
  
  return {
    icon: Clock,
    text: 'Unknown',
    subtext: '',
    color: 'text-gray-600'
  };
};

export default function Orders() {
  const { user } = useAuth();
  const { orders, fetchOrders, deleteOrder } = useOrders();
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update current time every minute for dynamic time calculations
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 30000); // Update every 30 seconds for more accurate time estimates

    return () => clearInterval(timer);
  }, []);

  // Fetch orders when component mounts
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const userOrders = orders.filter(o => o.userId === user?.id);
  const activeOrders = userOrders.filter(o => o.status !== 'completed');
  const pastOrders = userOrders.filter(o => o.status === 'completed');

  const handleDeleteOrder = async (orderId: string) => {
    if (window.confirm('Are you sure you want to delete this order? This action cannot be undone.')) {
      try {
        await deleteOrder(orderId);
        // Show success message (you can use a toast notification here)
        console.log('Order deleted successfully');
      } catch (error) {
        console.error('Failed to delete order:', error);
        // Show error message (you can use a toast notification here)
        alert('Failed to delete order. Please try again.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-md border-b shadow-soft">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/menu')}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex-1">
              <h1 className="font-bold text-lg text-foreground">My Orders</h1>
              <p className="text-xs text-muted-foreground">Track your order status</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => fetchOrders()}
              title="Refresh orders"
            >
              <RefreshCw className="h-5 w-5" />
            </Button>
            <ProfileButton />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 max-w-2xl">
        {/* Active Orders */}
        {activeOrders.length > 0 && (
          <div className="mb-8">
            <h2 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              Active Orders
            </h2>
            <div className="space-y-4">
              {activeOrders.map((order, index) => {
                const config = statusConfig[order.status];
                return (
                  <motion.div
                    key={order.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-card rounded-2xl border shadow-soft overflow-hidden"
                  >
                    <div className="p-4 border-b">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-bold text-xl text-foreground">₹{order.totalPrice.toFixed(2)}</p>
                        </div>
                        <Badge className={cn(config.bgColor, config.color, "gap-1")}>
                          <config.icon className="h-3 w-3" />
                          {config.label}
                        </Badge>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="px-4 py-3 bg-muted/30">
                      <div className="flex justify-between mb-2">
                        {Object.entries(statusConfig).map(([key, value], i) => (
                          <div
                            key={key}
                            className={cn(
                              "flex flex-col items-center",
                              Object.keys(statusConfig).indexOf(order.status) >= i
                                ? "text-primary"
                                : "text-muted-foreground"
                            )}
                          >
                            <value.icon className="h-5 w-5 mb-1" />
                            <span className="text-xs hidden sm:block">{value.label.split(' ')[0]}</span>
                          </div>
                        ))}
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          className="h-full gradient-primary"
                          initial={{ width: 0 }}
                          animate={{
                            width: `${((Object.keys(statusConfig).indexOf(order.status) + 1) / 4) * 100}%`
                          }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>

                    <div className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">
                            {formatDateOnly(order.createdAt)}
                          </span>
                          <span className="text-sm text-muted-foreground mx-2">•</span>
                          <span className="text-sm text-muted-foreground">
                            {formatISTTime(order.createdAt)}
                          </span>
                        </div>
                        {order.queuePosition && order.status === 'pending' && (
                          <Badge variant="outline" className="text-xs">
                            Queue :{order.queuePosition}
                          </Badge>
                        )}
                      </div>

                      <div className="flex items-center gap-3 mb-4 p-3 bg-muted/30 rounded-lg">
                        {(() => {
                          const timeDisplay = getTimeDisplay(order, currentTime);
                          const TimeIcon = timeDisplay.icon;
                          return (
                            <>
                              <div className={cn("p-2 rounded-full bg-background", timeDisplay.color)}>
                                <TimeIcon className="h-5 w-5" />
                              </div>
                              <div className="flex-1">
                                <p className={cn("font-medium", timeDisplay.color)}>
                                  {timeDisplay.text}
                                </p>
                                {timeDisplay.subtext && (
                                  <p className="text-xs text-muted-foreground">
                                    {timeDisplay.subtext}
                                  </p>
                                )}
                              </div>
                            </>
                          );
                        })()}
                      </div>

                      <div className="space-y-2">
                        {order.items.map((item) => (
                          <div key={item.menuItem.id} className="flex items-center gap-3">
                            <img
                              src={item.menuItem.image}
                              alt={item.menuItem.name}
                              className="w-12 h-12 rounded-lg object-cover"
                            />
                            <div className="flex-1">
                              <p className="font-medium text-sm">{item.menuItem.name}</p>
                              <p className="text-xs text-muted-foreground">
                                Qty: {item.quantity}
                              </p>
                            </div>
                            <span className="font-medium text-sm">
                              ₹{(item.menuItem.price * item.quantity).toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Past Orders */}
        {pastOrders.length > 0 && (
          <div>
            <h2 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-primary" />
              Past Orders
            </h2>
            <div className="space-y-3">
              {pastOrders.map((order) => (
                <div
                  key={order.id}
                  className="bg-card rounded-xl border p-4 flex items-center gap-4"
                >
                  <div className="flex-1">
                    <p className="font-medium text-sm text-foreground">
                      {order.items.map(i => i.menuItem.name).join(', ')}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {order.items.reduce((acc, i) => acc + i.quantity, 0)} items • ₹{order.totalPrice.toFixed(2)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Completed
                    </Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteOrder(order.id)}
                      className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                      title="Delete order"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {userOrders.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <UtensilsCrossed className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-xl text-foreground mb-2">No Orders Yet</h3>
            <p className="text-muted-foreground mb-6">Start ordering delicious food from our menu</p>
            <Button
              onClick={() => navigate('/menu')}
              className="gradient-primary text-primary-foreground"
            >
              Browse Menu
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
