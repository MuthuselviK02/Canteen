import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useFavorites } from '@/contexts/FavoritesContext';
import { useOrders } from '@/contexts/OrderContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Heart, 
  ShoppingCart, 
  Star, 
  Clock,
  UtensilsCrossed,
  ArrowLeft,
  Trash2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export default function Favorites() {
  const { favorites, removeFromFavorites, loading, error } = useFavorites();
  const { addToCart } = useOrders();
  const navigate = useNavigate();
  const [removingItem, setRemovingItem] = useState<string | null>(null);

  const handleAddToCart = (item: any) => {
    addToCart(item);
    toast.success(`Added ${item.name} to cart!`);
  };

  const handleRemoveFavorite = async (itemId: string) => {
    setRemovingItem(itemId);
    try {
      removeFromFavorites(itemId);
      toast.success('Item removed from favorites');
    } catch (error) {
      toast.error('Failed to remove from favorites');
    } finally {
      setRemovingItem(null);
    }
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-16">
            <Heart className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-2xl font-bold mb-2">Error Loading Favorites</h2>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={handleGoBack} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="icon"
              onClick={handleGoBack}
              className="shrink-0"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <Heart className="h-8 w-8 text-red-500" />
                My Favorites
              </h1>
              <p className="text-muted-foreground">
                {favorites.length} {favorites.length === 1 ? 'item' : 'items'} in your favorites
              </p>
            </div>
          </div>
        </div>

        {/* Favorites Grid */}
        {favorites.length === 0 ? (
          <Card>
            <CardContent className="py-16">
              <div className="text-center">
                <Heart className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h2 className="text-2xl font-bold mb-2">No Favorites Yet</h2>
                <p className="text-muted-foreground mb-6">
                  Start adding items to your favorites to see them here!
                </p>
                <Button onClick={() => navigate('/menu')}>
                  <UtensilsCrossed className="h-4 w-4 mr-2" />
                  Browse Menu
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {favorites.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow duration-300">
                  <CardHeader className="pb-3">
                    <div className="relative">
                      {item.image && (
                        <div className="h-48 bg-gray-100 rounded-lg overflow-hidden">
                          <img
                            src={item.image}
                            alt={item.name}
                            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.src = '/api/placeholder/300/200';
                            }}
                          />
                        </div>
                      )}
                      
                      {/* Remove from Favorites Button */}
                      <Button
                        variant="destructive"
                        size="icon"
                        className="absolute top-2 right-2 h-8 w-8 bg-white/90 hover:bg-white text-red-500 border border-red-200"
                        onClick={() => handleRemoveFavorite(item.id)}
                        disabled={removingItem === item.id}
                      >
                        {removingItem === item.id ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-500"></div>
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>

                      {/* Category Badge */}
                      <Badge className="absolute top-2 left-2 bg-primary/90 text-white">
                        {item.category}
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                        {item.name}
                      </h3>
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                        {item.description}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-primary">
                            ₹{item.price}
                          </span>
                        </div>
                        
                        <Badge variant="secondary" className="text-xs">
                          {item.type === 'combo' ? 'Combo' : 'Menu Item'}
                        </Badge>
                      </div>
                    </div>

                    {/* Added Date */}
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      Added {item.addedAt.toLocaleDateString()}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => handleAddToCart(item)}
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        Add to Cart
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
