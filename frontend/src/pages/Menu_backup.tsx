import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useOrders } from '@/contexts/OrderContext';
import { MenuItem } from '@/contexts/OrderContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  UtensilsCrossed,
  ShoppingCart,
  Search,
  Clock,
  Flame,
  Plus,
  Minus,
  LogOut,
  User,
  Timer,
  Package,
  Star
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { ProfileButton } from '@/components/ui/Profile';
import { AIRecommendations } from '@/components/ai/AIRecommendations';
import { AIRecommendationProvider } from '@/contexts/AIRecommendationContext';
import OrderBilling from '@/components/billing/OrderBilling';
import { buildApiUrl } from '@/utils/api';

// Sample combo data - in production, this would come from the API
const sampleCombos = [
  {
    id: 'combo-1',
    name: 'Biryani Combo',
    description: 'Complete meal with biryani, raita, and dessert',
    price: 180,
    prepTime: 20,
    calories: 850,
    image: '/api/placeholder/300/200',
    available: true,
    items: [
      {
        id: '1',
        name: 'Chicken Biryani',
        description: 'Aromatic chicken biryani with basmati rice',
        price: 120,
        prepTime: 15,
        calories: 450,
        category: 'Main Course',
        image: '/api/placeholder/100/100',
        available: true
      },
      {
        id: '2',
        name: 'Raita',
        description: 'Fresh yogurt raita with spices',
        price: 30,
        prepTime: 5,
        calories: 80,
        category: 'Side Dish',
        image: '/api/placeholder/100/100',
        available: true
      },
      {
        id: '3',
        name: 'Gulab Jamun',
        description: 'Sweet Indian dessert',
        price: 40,
        prepTime: 5,
        calories: 320,
        category: 'Dessert',
        image: '/api/placeholder/100/100',
        available: true
      }
    ]
  },
  {
    id: 'combo-2',
    name: 'Thali Special',
    description: 'Traditional Indian thali with multiple dishes',
    price: 150,
    prepTime: 25,
    calories: 750,
    image: '/api/placeholder/300/200',
    available: true,
    items: [
      {
        id: '4',
        name: 'Dal Tadka',
        description: 'Yellow lentils with tempering',
        price: 60,
        prepTime: 10,
        calories: 200,
        category: 'Main Course',
        image: '/api/placeholder/100/100',
        available: true
      },
      {
        id: '5',
        name: 'Rice',
        description: 'Steamed basmati rice',
        price: 40,
        prepTime: 5,
        calories: 200,
        category: 'Main Course',
        image: '/api/placeholder/100/100',
        available: true
      },
      {
        id: '6',
        name: 'Roti',
        description: 'Indian flatbread',
        price: 20,
        prepTime: 8,
        calories: 150,
        category: 'Bread',
        image: '/api/placeholder/100/100',
        available: true
      },
      {
        id: '7',
        name: 'Mixed Vegetable',
        description: 'Seasonal vegetables curry',
        price: 50,
        prepTime: 12,
        calories: 200,
        category: 'Side Dish',
        image: '/api/placeholder/100/100',
        available: true
      }
    ]
  }
];

export default function Menu() {
  const { user, logout } = useAuth();
  const { cart, addToCart, removeFromCart, updateQuantity, getCartTotal, getCartItemQuantity, placeOrder, clearCart, fetchOrders } = useOrders();
  const navigate = useNavigate();

  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [timeConstraint, setTimeConstraint] = useState<number | null>(null);
  const [showCart, setShowCart] = useState(false);
  
  // Billing state
  const [showBilling, setShowBilling] = useState(false);
  const [placedOrder, setPlacedOrder] = useState<any>(null);

  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('canteen_token');
        if (!token) {
          throw new Error('Authentication token not found');
        }

        const response = await fetch(buildApiUrl('/api/menu'), {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setMenuItems(data);
        
        // Extract unique categories
        const uniqueCategories = ['All', ...new Set(data.map((item: MenuItem) => item.category))] as string[];
        setCategories(uniqueCategories);
      } catch (err) {
        console.error('Error fetching menu:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch menu');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMenu();
  }, []);

  const cartItemCount = cart.reduce((total, item) => total + item.quantity, 0);

  const filteredItems = menuItems.filter(item => {
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTime = !timeConstraint || item.prepTime <= timeConstraint;
    return matchesCategory && matchesSearch && matchesTime && item.available;
  });

  const handleAddComboToCart = (combo: any) => {
    // Add all combo items to cart as individual items
    combo.items.forEach((item: MenuItem) => {
      addToCart(item);
    });
    toast.success(`${combo.name} added to cart with all ${combo.items.length} items!`);
  };

  const handleUpdateComboQuantity = (comboId: string, quantity: number) => {
    // Find the combo and update all its items
    const combo = sampleCombos.find(c => c.id === comboId);
    if (combo && quantity === 0) {
      // Remove all combo items from cart
      combo.items.forEach((item: MenuItem) => {
        removeFromCart(item.id);
      });
    } else if (combo && quantity > 0) {
      // Calculate current quantity and add/remove difference
      const currentQuantities = combo.items.map((item: MenuItem) => getCartItemQuantity(item.id));
      const currentTotal = currentQuantities.reduce((sum, qty) => sum + qty, 0);
      const difference = quantity - currentTotal;
      
      if (difference > 0) {
        // Add items
        for (let i = 0; i < difference; i++) {
          combo.items.forEach((item: MenuItem) => {
            addToCart(item);
          });
        }
      } else if (difference < 0) {
        // Remove items
        const itemsToRemove = Math.abs(difference);
        for (let i = 0; i < itemsToRemove; i++) {
          combo.items.forEach((item: MenuItem) => {
            if (getCartItemQuantity(item.id) > 0) {
              removeFromCart(item.id);
            }
          });
        }
      }
    }
  };

  const getComboQuantity = (comboId: string) => {
    const combo = sampleCombos.find(c => c.id === comboId);
    if (!combo) return 0;
    
    const quantities = combo.items.map((item: MenuItem) => getCartItemQuantity(item.id));
    const minQuantity = Math.min(...quantities);
    return minQuantity > 0 ? minQuantity : 0;
  };

  const handlePlaceOrder = async () => {
    const cartTotal = getCartTotal();
    if (!user) {
      toast.error('Please login to place an order');
      navigate('/login');
      return;
    }

    try {
      await placeOrder(user.id, user.fullname);
      setPlacedOrder({
        items: [...cart],
        total: cartTotal,
        timestamp: new Date()
      });
      setShowBilling(true);
      clearCart();
      toast.success('Order placed successfully!');
    } catch (error) {
      console.error('Error placing order:', error);
      toast.error('Failed to place order');
    }
  };

  return (
  <AIRecommendationProvider>
    <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-card border-b sticky top-0 z-50 backdrop-blur-lg bg-card/95">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 gradient-primary rounded-xl">
                  <UtensilsCrossed className="h-6 w-6 text-primary-foreground" />
                </div>
                <div>
                  <h1 className="font-bold text-lg text-foreground">Smart Canteen</h1>
                  <p className="text-xs text-muted-foreground">Hi, {user?.fullname}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="icon"
                  className="relative"
                  onClick={() => setShowCart(!showCart)}
                >
                  <ShoppingCart className="h-5 w-5" />
                  {cartItemCount > 0 && (
                    <span className="absolute -top-2 -right-2 h-5 w-5 rounded-full gradient-secondary text-xs text-primary-foreground flex items-center justify-center font-bold">
                      {cartItemCount}
                    </span>
                  )}
                </Button>

                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => navigate('/orders')}
                >
                  <Package className="h-5 w-5" />
                </Button>

                <ProfileButton />
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col gap-4">
            {/* AI Recommendations Section */}
            <AIRecommendations 
              onAddToCart={(item) => {
                const menuItem = menuItems.find(mi => mi.id === item.menu_item_id.toString());
                if (menuItem) {
                  addToCart(menuItem);
                }
              }}
              maxItems={6}
            />
            
            {/* Main Content - Full Width */}
            <div className="w-full">
              {/* Search and Filter */}
              <div className="space-y-4 mb-6">
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                    <Input
                      placeholder="Search menu and combos..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 h-12"
                    />
                  </div>
                  <div className="flex items-center gap-2 bg-card border rounded-lg px-3">
                    <Timer className="h-5 w-5 text-primary" />
                    <Input
                      type="number"
                      placeholder="Time limit (min)"
                      value={timeConstraint || ''}
                      onChange={(e) => setTimeConstraint(e.target.value ? parseInt(e.target.value) : null)}
                      className="w-32 border-0 focus-visible:ring-0"
                    />
                  </div>
                </div>

                {/* Categories */}
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                  {categories.map((category) => (
                    <Button
                      key={category}
                      variant={selectedCategory === category ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedCategory(category)}
                      className={cn(
                        "whitespace-nowrap transition-all",
                        selectedCategory === category && "gradient-primary text-primary-foreground"
                      )}
                    >
                      {category}
                    </Button>
                  ))}
                </div>

                {timeConstraint && (
                  <div className="flex items-center gap-2 p-3 bg-accent rounded-lg">
                    <Clock className="h-4 w-4 text-accent-foreground" />
                    <span className="text-sm text-accent-foreground">
                      Showing items ready in {timeConstraint} minutes or less
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setTimeConstraint(null)}
                      className="ml-auto text-xs"
                    >
                      Clear
                    </Button>
                  </div>
                )}
              </div>

              {/* Regular Menu Items */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <div className="p-2 bg-primary rounded-lg">
                    <UtensilsCrossed className="h-5 w-5 text-primary-foreground" />
                  </div>
                  <h2 className="text-xl font-bold text-foreground">Menu Items</h2>
                </div>

                {/* Menu Grid */}
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    <p className="mt-4 text-muted-foreground">Loading menu...</p>
                  </div>
                ) : error ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <p className="text-destructive mb-4">{error}</p>
                    <Button onClick={() => window.location.reload()}>Retry</Button>
                  </div>
                ) : filteredItems.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <UtensilsCrossed className="h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No items available. Please check back later.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
                    {filteredItems.map((item, index) => {
                      const quantity = getCartItemQuantity(item.id);

                      return (
                        <motion.div
                          key={item.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="bg-card rounded-2xl overflow-hidden border shadow-soft hover:shadow-card transition-all duration-300 group"
                        >
                          <div className="relative h-40 overflow-hidden">
                            <img
                              src={item.image}
                              alt={item.name}
                              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                            />
                            <div className="absolute top-3 right-3 flex gap-2">
                              <Badge
                                variant="secondary"
                                className="bg-muted/90 text-foreground border border-border/60 shadow-sm transition-colors group-hover:bg-secondary group-hover:text-secondary-foreground"
                              >
                                <Clock className="h-3 w-3 mr-1" />
                                {item.prepTime} min
                              </Badge>
                            </div>
                          </div>

                          <div className="p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h3 className="font-semibold text-foreground">{item.name}</h3>
                              <span className="font-bold text-primary">₹{item.price.toFixed(2)}</span>
                            </div>

                            <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                              {item.description}
                            </p>

                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                                <Flame className="h-4 w-4 text-secondary" />
                                {item.calories} cal
                              </div>
                              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                                <Star className="h-4 w-4 text-secondary" />
                                {item.rating || 0} stars
                              </div>
                              {quantity === 0 ? (
                                <Button
                                  size="sm"
                                  onClick={() => addToCart(item)}
                                  className="w-full"
                                >
                                  <Plus className="h-4 w-4 mr-1" />
                                  Add
                                </Button>
                              ) : (
                              <div className="flex items-center gap-2">
                                <Button
                                  size="icon"
                                  variant="outline"
                                  className="h-8 w-8"
                                  onClick={() => updateQuantity(item.id, quantity - 1)}
                                >
                                  <Minus className="h-4 w-4" />
                                </Button>
                                <span className="font-semibold w-6 text-center">{quantity}</span>
                                <Button
                                  size="icon"
                                  variant="outline"
                                  className="h-8 w-8"
                                  onClick={() => updateQuantity(item.id, quantity + 1)}
                                >
                                  <Plus className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Cart Sidebar */}
        {showCart && (
          <div className="fixed inset-0 z-50 flex">
            <div 
              className="fixed inset-0 bg-black/50" 
              onClick={() => setShowCart(false)}
            />
            <div className="fixed right-0 top-0 h-full w-full max-w-md bg-card shadow-xl">
              <div className="p-4 border-b">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Cart ({cartItemCount} items)</h2>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowCart(false)}
                  >
                    ×
                  </Button>
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4">
                {cart.length === 0 ? (
                  <div className="text-center py-8">
                    <ShoppingCart className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Your cart is empty</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {cart.map((item) => (
                      <div key={item.menuItem.id} className="flex items-center gap-4 p-3 bg-muted/30 rounded-lg">
                        <img
                          src={item.menuItem.image}
                          alt={item.menuItem.name}
                          className="w-16 h-16 rounded-lg object-cover"
                        />
                        <div className="flex-1">
                          <h4 className="font-medium">{item.menuItem.name}</h4>
                          <p className="text-sm text-muted-foreground">₹{item.menuItem.price.toFixed(2)}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="icon"
                            variant="outline"
                            className="h-8 w-8"
                            onClick={() => updateQuantity(item.menuItem.id, item.quantity - 1)}
                          >
                            <Minus className="h-4 w-4" />
                          </Button>
                          <span className="font-semibold w-6 text-center">{item.quantity}</span>
                          <Button
                            size="icon"
                            variant="outline"
                            className="h-8 w-8"
                            onClick={() => updateQuantity(item.menuItem.id, item.quantity + 1)}
                          >
                            <Plus className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {cart.length > 0 && (
                <div className="border-t p-4">
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between">
                      <span>Subtotal:</span>
                      <span>₹{getCartTotal().price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-semibold text-lg">
                      <span>Total:</span>
                      <span>₹{getCartTotal().price.toFixed(2)}</span>
                    </div>
                  </div>
                  <Button
                    onClick={handlePlaceOrder}
                    className="w-full gradient-primary text-primary-foreground"
                  >
                    Place Order
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Billing Modal */}
        {showBilling && placedOrder && (
          <OrderBilling
            order={placedOrder}
            cartItems={placedOrder.items}
            totalAmount={placedOrder.total.price}
            onPaymentComplete={(paymentMethod) => {
              console.log('Payment completed with:', paymentMethod);
              setShowBilling(false);
              navigate('/orders');
            }}
            onClose={() => setShowBilling(false)}
          />
        )}
      </div>
    </AIRecommendationProvider>
);  
}
