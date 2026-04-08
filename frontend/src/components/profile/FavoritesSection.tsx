import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Heart, ShoppingCart, Clock, Flame, X, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { useFavorites } from '@/contexts/FavoritesContext';
import { useOrders } from '@/contexts/OrderContext';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

export default function FavoritesSection() {
  const { favorites, removeFromFavorites, loading } = useFavorites();
  const { addToCart, getCartItemQuantity } = useOrders();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'menu_item' | 'combo'>('all');

  const filteredFavorites = favorites.filter(fav => {
    const matchesSearch = fav.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         fav.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || fav.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const handleAddToCart = (item: any) => {
    // Convert favorite item back to menu item format
    const menuItem = {
      id: item.id,
      name: item.name,
      description: item.description,
      price: item.price,
      prepTime: 15, // Default prep time
      calories: 300, // Default calories
      category: item.category,
      image: item.image,
      available: true
    };
    
    addToCart(menuItem);
    toast.success(`${item.name} added to cart!`);
  };

  const handleRemoveFavorite = (itemId: string, itemName: string) => {
    removeFromFavorites(itemId);
    toast.success(`${itemName} removed from favorites`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="mt-4 text-muted-foreground">Loading favorites...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">My Favorites</h2>
          <p className="text-muted-foreground">
            {favorites.length} {favorites.length === 1 ? 'item' : 'items'} saved
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Heart className="h-5 w-5 text-red-500" />
          <span className="text-sm text-muted-foreground">Quick access to your favorites</span>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="Search favorites..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={filterType === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('all')}
          >
            All
          </Button>
          <Button
            variant={filterType === 'menu_item' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('menu_item')}
          >
            Items
          </Button>
          <Button
            variant={filterType === 'combo' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('combo')}
          >
            Combos
          </Button>
        </div>
      </div>

      {/* Favorites Grid */}
      {favorites.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-20">
            <Heart className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">No favorites yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Start adding your favorite items to see them here. Click the heart icon on any menu item to save it.
            </p>
            <Button onClick={() => window.location.href = '/menu'}>
              Browse Menu
            </Button>
          </CardContent>
        </Card>
      ) : filteredFavorites.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-20">
            <Search className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">No favorites found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search or filter criteria
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredFavorites.map((item, index) => {
            const quantity = getCartItemQuantity(item.id);
            
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-card rounded-2xl overflow-hidden border shadow-soft hover:shadow-card transition-all duration-300 group"
              >
                {/* Item Image */}
                <div className="relative h-40 overflow-hidden">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  
                  {/* Type Badge */}
                  <div className="absolute top-3 left-3">
                    <Badge 
                      variant={item.type === 'combo' ? 'default' : 'secondary'}
                      className={cn(
                        "border-0",
                        item.type === 'combo' 
                          ? "bg-gradient-to-r from-orange-500 to-red-500 text-white" 
                          : "bg-primary text-primary-foreground"
                      )}
                    >
                      {item.type === 'combo' ? 'COMBO' : 'ITEM'}
                    </Badge>
                  </div>

                  {/* Remove Favorite Button */}
                  <Button
                    size="icon"
                    variant="ghost"
                    className="absolute top-3 right-3 h-8 w-8 bg-black/20 hover:bg-black/40 text-white"
                    onClick={() => handleRemoveFavorite(item.id, item.name)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {/* Item Details */}
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-foreground line-clamp-1">{item.name}</h3>
                    <span className="font-bold text-primary">₹{item.price.toFixed(2)}</span>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {item.description}
                  </p>

                  <div className="flex items-center gap-3 text-sm text-muted-foreground mb-3">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4 text-secondary" />
                      15 min
                    </div>
                    <div className="flex items-center gap-1">
                      <Flame className="h-4 w-4 text-secondary" />
                      300 cal
                    </div>
                  </div>

                  {/* Added Date */}
                  <div className="text-xs text-muted-foreground mb-3">
                    Added {item.addedAt.toLocaleDateString()}
                  </div>

                  {/* Add to Cart / Quantity Controls */}
                  {quantity === 0 ? (
                    <Button
                      size="sm"
                      onClick={() => handleAddToCart(item)}
                      className="w-full gradient-primary text-primary-foreground"
                    >
                      <ShoppingCart className="h-4 w-4 mr-2" />
                      Add to Cart
                    </Button>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Button
                          size="icon"
                          variant="outline"
                          className="h-8 w-8"
                          onClick={() => {
                            // Update quantity logic would go here
                            // For now, just show the quantity
                          }}
                        >
                          <span className="text-sm">-</span>
                        </Button>
                        <span className="font-semibold w-6 text-center">{quantity}</span>
                        <Button
                          size="icon"
                          variant="outline"
                          className="h-8 w-8"
                          onClick={() => handleAddToCart(item)}
                        >
                          <span className="text-sm">+</span>
                        </Button>
                      </div>
                      <span className="text-xs text-green-600">In cart</span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
