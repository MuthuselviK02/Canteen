import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useOrders } from '@/contexts/OrderContext';
import { useFavorites } from '@/contexts/FavoritesContext';
import { MenuItem } from '@/contexts/OrderContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
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
  Heart
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { ProfileButton } from '@/components/ui/Profile';
import { AIRecommendations } from '@/components/ai/AIRecommendations';
import { AIRecommendationProvider } from '@/contexts/AIRecommendationContext';
import OrderBilling from '@/components/billing/OrderBilling';
import { Category, CATEGORIES_API, getCategoryLabel, FALLBACK_CATEGORIES } from '@/core/categories';

// Sample menu data as fallback
const sampleMenuItems: MenuItem[] = [
  {
    id: '1',
    name: 'Chicken Biryani',
    description: 'Aromatic basmati rice cooked with tender chicken pieces and exotic spices',
    price: 120,
    prepTime: 20,
    calories: 450,
    category: 'Main Course',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: false
  },
  {
    id: '2',
    name: 'Paneer Butter Masala',
    description: 'Soft cottage cheese cubes in rich, creamy tomato-based gravy',
    price: 140,
    prepTime: 15,
    calories: 380,
    category: 'Main Course',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '3',
    name: 'Veg Pulao',
    description: 'Fragrant rice cooked with mixed vegetables and aromatic spices',
    price: 90,
    prepTime: 12,
    calories: 320,
    category: 'Main Course',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '4',
    name: 'Dal Makhani',
    description: 'Creamy black lentils cooked with butter and aromatic spices',
    price: 80,
    prepTime: 18,
    calories: 280,
    category: 'Main Course',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '5',
    name: 'Mixed Veg Curry',
    description: 'Seasonal vegetables cooked in flavorful curry sauce',
    price: 70,
    prepTime: 10,
    calories: 180,
    category: 'Main Course',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '6',
    name: 'Tandoori Roti',
    description: 'Traditional Indian flatbread cooked in clay oven',
    price: 15,
    prepTime: 5,
    calories: 120,
    category: 'Bread',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '7',
    name: 'Butter Naan',
    description: 'Soft leavened flatbread brushed with butter',
    price: 20,
    prepTime: 6,
    calories: 150,
    category: 'Bread',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '8',
    name: 'Plain Rice',
    description: 'Steamed basmati rice',
    price: 40,
    prepTime: 8,
    calories: 200,
    category: 'Main Course',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '9',
    name: 'Gulab Jamun',
    description: 'Soft milk dumplings soaked in sugar syrup',
    price: 30,
    prepTime: 5,
    calories: 180,
    category: 'Dessert',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '10',
    name: 'Raita',
    description: 'Fresh yogurt mixed with grated cucumber and spices',
    price: 25,
    prepTime: 3,
    calories: 80,
    category: 'Side Dish',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '11',
    name: 'Salad',
    description: 'Fresh mixed salad with lemon dressing',
    price: 35,
    prepTime: 5,
    calories: 60,
    category: 'Side Dish',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  },
  {
    id: '12',
    name: 'Veg Soup',
    description: 'Healthy mixed vegetable soup',
    price: 45,
    prepTime: 8,
    calories: 90,
    category: 'Starter',
    image: '/api/placeholder/300/200',
    available: true,
    isVegetarian: true
  }
];

export default function Menu() {
  const { user, logout } = useAuth();
  const { cart, addToCart, removeFromCart, updateQuantity, getCartTotal, getCartItemQuantity, placeOrder, clearCart, fetchOrders } = useOrders();
  const { toggleFavorite, isFavorite } = useFavorites();
  const navigate = useNavigate();

  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [timeConstraint, setTimeConstraint] = useState<number | null>(null);
  const [showCart, setShowCart] = useState(false);
  const [vegetarianOnly, setVegetarianOnly] = useState(false);
  
  // Billing state
  const [showBilling, setShowBilling] = useState(false);
  const [placedOrder, setPlacedOrder] = useState<any>(null);

  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>(FALLBACK_CATEGORIES);
  const [availableCategories, setAvailableCategories] = useState<string[]>(['All']);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = API_URL.replace(/\/$/, '');

  // Fetch categories from API
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}${CATEGORIES_API.ALL}`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
        return data;
      } else {
        console.warn('Failed to fetch categories, using fallback');
        setCategories(FALLBACK_CATEGORIES);
        return FALLBACK_CATEGORIES;
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      setCategories(FALLBACK_CATEGORIES);
      return FALLBACK_CATEGORIES;
    }
  };

  // Fetch menu items
  useEffect(() => {
    const fetchMenu = async () => {
      try {
        setIsLoading(true);
        
        // Fetch categories first
        const categoriesData = await fetchCategories();
        
        const response = await fetch(`${API_BASE_URL}/api/menu`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Map backend response to frontend MenuItem interface
        const mappedItems: MenuItem[] = data.map((item: any) => ({
          id: item.id.toString(),
          name: item.name,
          description: item.description,
          price: item.price,
          prepTime: item.base_prep_time || 15, // fallback to 15 minutes
          calories: item.calories || 200, // fallback to 200 calories
          category: item.category_label || getCategoryLabel(categoriesData, item.category), // Use category_label from backend
          image: item.image_url ? `${API_BASE_URL}${item.image_url}` : '/api/placeholder/300/200',
          available: item.is_available !== false, // default to true
          isVegetarian: item.is_vegetarian || false // map is_vegetarian from backend
        }));
        
        setMenuItems(mappedItems);
        
        // Extract unique categories from menu items with counts
        const itemCategories = mappedItems.map((item: MenuItem) => item.category);
        const categoryCounts = itemCategories.reduce((acc: Record<string, number>, category: string) => {
          acc[category] = (acc[category] || 0) + 1;
          return acc;
        }, {});
        
        // Create categories with counts: ["All", "Main Course (5)", "Starter (3)", ...]
        // Only include categories that have items
        const uniqueCategoriesWithCounts = ['All', ...new Set(itemCategories)]
          .filter(category => category === 'All' || (categoryCounts[category] || 0) > 0)
          .map(category => {
            if (category === 'All') return 'All';
            return `${category} (${categoryCounts[category] || 0})`;
          });
        setAvailableCategories(uniqueCategoriesWithCounts);
        
        // Set selected category to 'All' if current selection is not available
        const availableCategoryNames = uniqueCategoriesWithCounts.map(cat => 
          cat.includes(' (') ? cat.split(' (')[0] : cat
        );
        const currentCategoryName = selectedCategory.includes(' (') ? selectedCategory.split(' (')[0] : selectedCategory;
        
        if (!availableCategoryNames.includes(currentCategoryName) && selectedCategory !== 'All') {
          setSelectedCategory('All');
        }
        
      } catch (err) {
        console.error('Error fetching menu:', err);
        // Use sample data as fallback
        console.log('Using sample menu data as fallback');
        setMenuItems(sampleMenuItems);
        
        // Extract unique categories from sample data with counts
        const sampleCategories = sampleMenuItems.map((item: MenuItem) => item.category);
        const sampleCategoryCounts = sampleCategories.reduce((acc: Record<string, number>, category: string) => {
          acc[category] = (acc[category] || 0) + 1;
          return acc;
        }, {});
        
        const uniqueSampleCategoriesWithCounts = ['All', ...new Set(sampleCategories)]
          .filter(category => category === 'All' || (sampleCategoryCounts[category] || 0) > 0)
          .map(category => {
            if (category === 'All') return 'All';
            return `${category} (${sampleCategoryCounts[category] || 0})`;
          });
        setAvailableCategories(uniqueSampleCategoriesWithCounts);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMenu();
  }, []);

  const cartItemCount = cart.reduce((total, item) => total + item.quantity, 0);

  const filteredItems = menuItems.filter(item => {
    const matchesCategory = selectedCategory === 'All' || 
      item.category === selectedCategory ||
      (selectedCategory.includes(' (') && item.category === selectedCategory.split(' (')[0]);
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTime = !timeConstraint || item.prepTime <= timeConstraint;
    const matchesVegetarian = !vegetarianOnly || (item.isVegetarian === true);
    return matchesCategory && matchesSearch && matchesTime && matchesVegetarian && item.available;
  });

  const cartTotal = getCartTotal();

  const handlePlaceOrder = async () => {
    if (!user) {
      toast.error('Please login to place an order');
      navigate('/login');
      return;
    }

    try {
      const newOrder = await placeOrder(user.id, user.fullname);
      setPlacedOrder({
        id: newOrder?.id,
        userId: user.id,
        customer_id: user.id,
        customer_name: user.fullname,
        customer_email: user.email,
        predicted_wait_time: (newOrder as any)?.estimatedTime,
        items: [...cart],
        total: cartTotal,
        timestamp: new Date()
      });
      setShowBilling(true);
      toast.success('Order placed successfully!');
    } catch (error) {
      console.error('Error placing order:', error);
      toast.error('Failed to place order. Please try again.');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
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
                // Find the menu item and add to cart
                const menuItem = menuItems.find(mi => mi.id === item.menu_item_id.toString());
                if (menuItem) {
                  addToCart(menuItem);
                }
              }}
            />

            {/* Search and Filters */}
            <div className="space-y-4 mb-6">
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    placeholder="Search menu..."
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

              {/* Vegetarian Filter Toggle */}
              <div className="flex items-center justify-between p-3 bg-card border rounded-lg">
                <div className="flex items-center gap-2">
                  <Label htmlFor="vegetarian-toggle" className="text-sm font-medium cursor-pointer">
                    Vegetarian Only
                  </Label>
                  <span className="text-xs text-muted-foreground">
                    Show only vegetarian items
                  </span>
                </div>
                <Switch
                  id="vegetarian-toggle"
                  checked={vegetarianOnly}
                  onCheckedChange={setVegetarianOnly}
                />
              </div>

              {/* Categories */}
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                {availableCategories.map((category) => (
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
                <p className="text-muted-foreground">
                  {vegetarianOnly 
                    ? "No vegetarian items available." 
                    : "No items available. Please check back later."
                  }
                </p>
                {vegetarianOnly && (
                  <Button 
                    variant="outline" 
                    onClick={() => setVegetarianOnly(false)}
                    className="mt-2"
                  >
                    Show All Items
                  </Button>
                )}
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
                          onError={(e) => {
                            e.currentTarget.src = '/api/placeholder/300/200';
                          }}
                        />
                        <div className="absolute top-3 right-3 flex gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 bg-white/90 hover:bg-white border border-border/60 shadow-sm transition-colors group"
                            onClick={(e) => {
                              e.stopPropagation();
                              const isCurrentlyFavorite = isFavorite(item.id);
                              toggleFavorite({
                                id: item.id,
                                name: item.name,
                                description: item.description,
                                price: item.price,
                                image: item.image,
                                category: item.category,
                                type: 'menu_item'
                              });
                              
                              // Show toast feedback
                              if (isCurrentlyFavorite) {
                                toast.success(`Removed ${item.name} from favorites`);
                              } else {
                                toast.success(`Added ${item.name} to favorites`);
                              }
                            }}
                          >
                            <Heart 
                              className={`h-4 w-4 transition-colors ${
                                isFavorite(item.id) 
                                  ? 'fill-red-500 text-red-500' 
                                  : 'text-gray-600 hover:text-red-500'
                              }`} 
                            />
                          </Button>
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
                        </div>

                        {quantity === 0 ? (
                          <Button
                            size="sm"
                            onClick={() => addToCart(item)}
                            className="w-full gradient-primary text-primary-foreground"
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
                              onClick={() => removeFromCart(item.id)}
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
                    </motion.div>
                  );
                })}
              </div>
            )}
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
                  <h2 className="text-lg font-semibold">Cart</h2>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowCart(false)}
                  >
                    <Minus className="h-4 w-4" />
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
                    {cart.map((item, index) => (
                      <div key={index} className="flex items-center gap-4 p-3 bg-muted/30 rounded-lg">
                        <img
                          src={item.menuItem.image}
                          alt={item.menuItem.name}
                          className="w-16 h-16 rounded-lg object-cover"
                          onError={(e) => {
                            e.currentTarget.src = '/api/placeholder/300/200';
                          }}
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
                            onClick={() => removeFromCart(item.menuItem.id)}
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

              <div className="p-4 border-t">
                <div className="flex items-center justify-between mb-4">
                  <span className="font-semibold">Total</span>
                  <span className="font-bold text-primary">₹{cartTotal.price.toFixed(2)}</span>
                </div>

                <Button
                  className="w-full h-12 gradient-primary text-primary-foreground font-semibold shadow-soft disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={handlePlaceOrder}
                  disabled={cart.length === 0}
                >
                  {cart.length === 0 ? 'Cart is Empty' : `Place Order - ₹${cartTotal.price.toFixed(2)}`}
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Order Billing Dialog */}
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
