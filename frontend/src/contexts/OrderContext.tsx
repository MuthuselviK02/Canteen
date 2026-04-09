import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';


// Debounce function to prevent rapid API calls
const debounce = (func: Function, wait: number) => {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  prepTime: number; // in minutes
  calories: number;
  category: string;
  image: string;
  available: boolean;
  isVegetarian?: boolean; // Optional field for vegetarian filter
  rating?: number; // Optional rating field (0-5 stars)
}

export type OrderStatus = 'pending' | 'preparing' | 'ready' | 'completed';

export interface OrderItem {
  menuItem: MenuItem;
  quantity: number;
}

export interface Order {
  id: string;
  userId: number;
  userName: string;
  items: OrderItem[];
  totalPrice: number;
  totalCalories: number;
  estimatedTime: number;
  status: OrderStatus;
  queuePosition: number;
  createdAt: Date;
  startedPreparationAt?: Date;
  readyAt?: Date;
  completedAt?: Date;
}

interface OrderContextType {
  cart: OrderItem[];
  orders: Order[];
  addToCart: (item: MenuItem) => void;
  removeFromCart: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  placeOrder: (userId: number, userName: string) => Promise<Order>;
  updateOrderStatus: (orderId: string, status: OrderStatus) => void;
  deleteOrder: (orderId: string) => Promise<void>;
  getCartTotal: () => { price: number; calories: number; time: number };
  getCartItemQuantity: (itemId: string) => number;
  fetchOrders: () => Promise<void>;
  fetchAllOrders: () => Promise<void>;
}

const OrderContext = createContext<OrderContextType | undefined>(undefined);

export function OrderProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<OrderItem[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);

  const addToCart = (item: MenuItem) => {
    setCart(prev => {
      const existing = prev.find(i => i.menuItem.id === item.id);
      if (existing) {
        return prev.map(i =>
          i.menuItem.id === item.id
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }
      return [...prev, { menuItem: item, quantity: 1 }];
    });
  };

  const removeFromCart = (itemId: string) => {
    setCart(prev => prev.filter(i => i.menuItem.id !== itemId));
  };

  const updateQuantity = (itemId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
      return;
    }
    setCart(prev => prev.map(i =>
      i.menuItem.id === itemId
        ? { ...i, quantity }
        : i
    ));
  };

  const clearCart = () => {
    setCart([]);
  };

  const getCartTotal = () => {
    return cart.reduce((acc, item) => ({
      price: acc.price + (item.menuItem.price * item.quantity),
      calories: acc.calories + (item.menuItem.calories * item.quantity),
      time: Math.max(acc.time, item.menuItem.prepTime)
    }), { price: 0, calories: 0, time: 0 });
  };

  const getCartItemQuantity = (itemId: string) => {
    const cartItem = cart.find(item => item.menuItem.id === itemId);
    return cartItem ? cartItem.quantity : 0;
  };

  const placeOrder = async (userId: number, userName: string) => {
    if (cart.length === 0) {
      throw new Error('Your cart is empty');
    }

    const totals = getCartTotal();
    const pendingOrders = orders.filter(o => o.status !== 'completed').length;

    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Prepare order data for backend
      const orderData = {
        items: cart.map(item => ({
          menu_item_id: parseInt(item.menuItem.id),
          quantity: item.quantity
        })),
        available_time: 15 // Available in 15 minutes (can be adjusted based on requirements)
      };

      // Send order to backend
      const response = await fetch(`${API_URL}/api/orders/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
      });

      if (response.ok) {
        const backendOrder = await response.json();
        console.log('Order placed successfully on backend:', backendOrder);
        
        // Transform backend response to frontend format
        const newOrder: Order = {
          id: backendOrder.id.toString(),
          userId,
          userName,
          items: [...cart],
          totalPrice: totals.price,
          totalCalories: totals.calories,
          estimatedTime: backendOrder.predicted_wait_time || totals.time + (pendingOrders * 2),
          status: 'pending',
          queuePosition: backendOrder.queue_position || pendingOrders + 1,
          createdAt: new Date(backendOrder.created_at + 'Z'), // Ensure UTC timezone
        };

        // Add to local state
        setOrders(prev => [newOrder, ...prev]);
        clearCart();
        
        return newOrder;
      } else {
        const errorData = await response.json();
        console.error('Failed to place order on backend:', errorData);
        throw new Error(errorData.detail || 'Failed to place order');
      }
    } catch (error) {
      console.error('Error placing order:', error);

      if (cart.length === 0) {
        throw error instanceof Error ? error : new Error('Your cart is empty');
      }

      // Fallback to local order creation if backend fails
      const newOrder: Order = {
        id: Date.now().toString(),
        userId,
        userName,
        items: [...cart],
        totalPrice: totals.price,
        totalCalories: totals.calories,
        estimatedTime: totals.time + (pendingOrders * 2),
        status: 'pending',
        queuePosition: pendingOrders + 1,
        createdAt: new Date()
      };

      setOrders(prev => [newOrder, ...prev]);
      clearCart();
      
      // Show warning but still create order locally
      console.warn('Order created locally due to backend error:', error);
      return newOrder;
    }
  };

  const updateOrderStatus = async (orderId: string, status: OrderStatus) => {
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        console.error('No authentication token found');
        return;
      }

      // Call backend API to update order status
      const response = await fetch(`${API_URL}/api/orders/${orderId}/status?status=${status}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Order status updated successfully:', result);
        
        // Update local state with the response data - DON'T call fetchOrders here
        setOrders(prev => prev.map(order => {
          if (order.id === orderId) {
            const updatedOrder = { 
              ...order, 
              status,
              estimatedTime: result.predicted_wait_time || order.estimatedTime,
              queuePosition: result.queue_position || order.queuePosition
            };
            
            // Set timestamps based on status
            if (status === 'preparing' && !order.startedPreparationAt) {
              updatedOrder.startedPreparationAt = new Date();
            } else if (status === 'ready' && !order.readyAt) {
              updatedOrder.readyAt = new Date();
            } else if (status === 'completed' && !order.completedAt) {
              updatedOrder.completedAt = new Date();
            }
            
            return updatedOrder;
          }
          return order;
        }));

        // Update queue positions if order is completed
        if (status === 'completed') {
          setOrders(prev => prev.map((order, index) => {
            if (order.status !== 'completed') {
              return { ...order, queuePosition: prev.filter((o, i) => i > index && o.status !== 'completed').length + 1 };
            }
            return order;
          }));
        }

        // DON'T call fetchOrders here - it causes other orders to disappear
        // The auto-refresh mechanism will handle consistency
        
      } else if (response.status === 429) {
        // Rate limited - wait and retry once
        console.warn('Rate limited, waiting to retry...');
        setTimeout(() => updateOrderStatus(orderId, status), 3000);
      } else {
        const errorData = await response.json();
        console.error('Failed to update order status:', errorData);
        throw new Error(errorData.detail || 'Failed to update order status');
      }
    } catch (error) {
      console.error('Error updating order status:', error);
      // Revert to local state update as fallback
      setOrders(prev => prev.map(order => {
        if (order.id === orderId) {
          return { ...order, status };
        }
        return order;
      }));
    }
  };

  const deleteOrder = async (orderId: string) => {
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${API_URL}/api/orders/${orderId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Order deleted successfully:', result);
        
        // Remove the order from local state
        setOrders(prev => prev.filter(order => order.id !== orderId));
        
        // Show success message (you can use a toast notification here)
        console.log('Order removed from list');
        
      } else {
        const errorData = await response.json();
        console.error('Failed to delete order:', errorData);
        throw new Error(errorData.detail || 'Failed to delete order');
      }
    } catch (error) {
      console.error('Error deleting order:', error);
      throw error;
    }
  };

  // Debounced fetch orders to prevent rapid API calls
  const debouncedFetchOrders = debounce(async () => {
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) return;

      const response = await fetch(`${API_URL}/api/orders/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const apiOrders = await response.json();
        
        // Transform API orders to frontend format
        const transformedOrders: Order[] = apiOrders.map((apiOrder: any) => ({
          id: apiOrder.id.toString(),
          userId: apiOrder.user_id,
          userName: apiOrder.user?.fullname || 'User', // Use actual username from API
          items: apiOrder.items.map((item: any) => ({
            menuItem: {
              id: item.menu_item?.id?.toString() || item.menu_item_id?.toString(),
              name: item.menu_item?.name || 'Unknown Item',
              description: item.menu_item?.description || '',
              price: item.menu_item?.price || 0,
              prepTime: item.menu_item?.base_prep_time || 10,
              calories: item.menu_item?.calories || 0,
              category: item.menu_item?.category || 'Main Course',
              image: item.menu_item?.image_url ? buildImageUrl(item.menu_item.image_url) : '/api/placeholder/300/200',
              available: item.menu_item?.is_available ?? true,
              rating: item.menu_item?.rating || 0
            },
            quantity: item.quantity
          })),
          totalPrice: apiOrder.items?.reduce((sum: number, item: any) => 
            sum + (item.menu_item?.price || 0) * item.quantity, 0) || 0,
          totalCalories: apiOrder.items?.reduce((sum: number, item: any) => 
            sum + (item.menu_item?.calories || 0) * item.quantity, 0) || 0,
          estimatedTime: apiOrder.predicted_wait_time || 15, // Dynamic time from backend
          status: (apiOrder.status?.toLowerCase() as OrderStatus) || 'pending',
          queuePosition: apiOrder.queue_position || 1,
          createdAt: apiOrder.created_at ? new Date(apiOrder.created_at + 'Z') : new Date(), // Add 'Z' to ensure UTC parsing
          startedPreparationAt: apiOrder.started_preparation_at ? new Date(apiOrder.started_preparation_at + 'Z') : undefined,
          readyAt: apiOrder.ready_at ? new Date(apiOrder.ready_at + 'Z') : undefined,
          completedAt: apiOrder.completed_at ? new Date(apiOrder.completed_at + 'Z') : undefined
        }));

        setOrders(transformedOrders);
      } else if (response.status === 429) {
        // Rate limited - wait and retry once
        console.warn('Rate limited, waiting to retry...');
        setTimeout(() => fetchOrders(), 3000);
      }
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    }
  }, 1000); // 1 second debounce

  const fetchOrders = async () => {
    return debouncedFetchOrders();
  };

  // Fetch orders on component mount
  useEffect(() => {
    fetchOrders();
  }, []);

  // Separate function for kitchen to fetch all orders
  const fetchAllOrders = async () => {
    try {
      console.log('🍳 fetchAllOrders called...');
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        console.error('❌ No token found in localStorage');
        return;
      }
      
      console.log('🔑 Token found:', token ? 'YES' : 'NO');
      console.log('🌐 Making API call to:', `${API_URL}/api/kitchen/orders`);

      const response = await fetch(`${API_URL}/api/kitchen/orders`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('📡 API Response status:', response.status);
      console.log('📡 API Response ok:', response.ok);

      if (response.ok) {
        const apiOrders = await response.json();
        console.log('📦 Raw API orders:', apiOrders);
        console.log('📦 Orders count:', apiOrders.length);
        
        // Transform API orders to frontend format
        const transformedOrders: Order[] = apiOrders.map((apiOrder: any) => ({
          id: apiOrder.id.toString(),
          userId: apiOrder.user_id,
          userName: apiOrder.user?.fullname || 'User',
          items: apiOrder.items.map((item: any) => ({
            menuItem: {
              id: item.menu_item?.id?.toString() || item.menu_item_id?.toString(),
              name: item.menu_item?.name || 'Unknown Item',
              description: item.menu_item?.description || '',
              price: item.menu_item?.price || 0,
              prepTime: item.menu_item?.base_prep_time || 10,
              calories: item.menu_item?.calories || 0,
              category: item.menu_item?.category || 'Main Course',
              image: item.menu_item?.image_url ? buildImageUrl(item.menu_item.image_url) : '/api/placeholder/300/200',
              available: item.menu_item?.is_available ?? true,
              rating: item.menu_item?.rating || 0
            },
            quantity: item.quantity
          })),
          totalPrice: apiOrder.items?.reduce((sum: number, item: any) => 
            sum + (item.menu_item?.price || 0) * item.quantity, 0) || 0,
          totalCalories: apiOrder.items?.reduce((sum: number, item: any) => 
            sum + (item.menu_item?.calories || 0) * item.quantity, 0) || 0,
          estimatedTime: apiOrder.predicted_wait_time || 15,
          status: (apiOrder.status?.toLowerCase() as OrderStatus) || 'pending',
          queuePosition: apiOrder.queue_position || 1,
          createdAt: apiOrder.created_at ? new Date(apiOrder.created_at + 'Z') : new Date(), // Add 'Z' to ensure UTC parsing
          startedPreparationAt: apiOrder.started_preparation_at ? new Date(apiOrder.started_preparation_at + 'Z') : undefined,
          readyAt: apiOrder.ready_at ? new Date(apiOrder.ready_at + 'Z') : undefined,
          completedAt: apiOrder.completed_at ? new Date(apiOrder.completed_at + 'Z') : undefined
        }));

        console.log('🔄 Transformed orders:', transformedOrders);
        console.log('🔄 Transformed orders count:', transformedOrders.length);
        setOrders(transformedOrders);
      } else {
        console.error('❌ API call failed:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('❌ Error response:', errorText);
      }
    } catch (error) {
      console.error('❌ Failed to fetch all orders:', error);
    }
  };

  // Auto-refresh for active orders (every 60 seconds to avoid interference)
  useEffect(() => {
    const interval = setInterval(() => {
      const hasActiveOrders = orders.some(order => 
        order.status === 'pending' || order.status === 'preparing' || order.status === 'ready'
      );
      
      if (hasActiveOrders) {
        // Use non-debounced fetch for auto-refresh to avoid conflicts
        const nonDebouncedFetch = async () => {
          try {
            const token = localStorage.getItem('canteen_token');
            if (!token) return;

            const response = await fetch(`${API_URL}/api/orders/`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });

            if (response.ok) {
              const apiOrders = await response.json();
              
              // Transform API orders to frontend format
              const transformedOrders: Order[] = apiOrders.map((apiOrder: any) => ({
                id: apiOrder.id.toString(),
                userId: apiOrder.user_id,
                userName: apiOrder.user?.fullname || 'User',
                items: apiOrder.items.map((item: any) => ({
                  menuItem: {
                    id: item.menu_item?.id?.toString() || item.menu_item_id?.toString(),
                    name: item.menu_item?.name || 'Unknown Item',
                    description: item.menu_item?.description || '',
                    price: item.menu_item?.price || 0,
                    prepTime: item.menu_item?.base_prep_time || 10,
                    calories: item.menu_item?.calories || 0,
                    category: item.menu_item?.category || 'Main Course',
                    image: item.menu_item?.image_url ? buildImageUrl(item.menu_item.image_url) : '/api/placeholder/300/200',
                    available: item.menu_item?.is_available ?? true,
                    rating: item.menu_item?.rating || 0
                  },
                  quantity: item.quantity
                })),
                totalPrice: apiOrder.items?.reduce((sum: number, item: any) => 
                  sum + (item.menu_item?.price || 0) * item.quantity, 0) || 0,
                totalCalories: apiOrder.items?.reduce((sum: number, item: any) => 
                  sum + (item.menu_item?.calories || 0) * item.quantity, 0) || 0,
                estimatedTime: apiOrder.predicted_wait_time || 15,
                status: (apiOrder.status?.toLowerCase() as OrderStatus) || 'pending',
                queuePosition: apiOrder.queue_position || 1,
                createdAt: apiOrder.created_at ? new Date(apiOrder.created_at + 'Z') : new Date(), // Add 'Z' to ensure UTC parsing
                startedPreparationAt: apiOrder.started_preparation_at ? new Date(apiOrder.started_preparation_at + 'Z') : undefined,
                readyAt: apiOrder.ready_at ? new Date(apiOrder.ready_at + 'Z') : undefined,
                completedAt: apiOrder.completed_at ? new Date(apiOrder.completed_at + 'Z') : undefined
              }));

              setOrders(transformedOrders);
            }
          } catch (error) {
            console.error('Failed to fetch orders (auto-refresh):', error);
          }
        };
        
        nonDebouncedFetch();
      }
    }, 60000); // 60 seconds - increased to avoid interference

    return () => clearInterval(interval);
  }, [orders]);

  return (
    <OrderContext.Provider value={{
      cart,
      orders,
      addToCart,
      removeFromCart,
      updateQuantity,
      clearCart,
      getCartTotal,
      getCartItemQuantity,
      placeOrder,
      updateOrderStatus,
      deleteOrder,
      fetchOrders,
      fetchAllOrders
    }}>
      {children}
    </OrderContext.Provider>
  );
}

export function useOrders() {
  const context = useContext(OrderContext);
  if (context === undefined) {
    throw new Error('useOrders must be used within an OrderProvider');
  }
  return context;
}
