import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Heart, ShoppingCart, Plus, Minus, Clock, Flame, X, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { MenuItem } from '@/contexts/OrderContext';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface ComboItem {
  id: string;
  name: string;
  description: string;
  price: number;
  prepTime: number;
  calories: number;
  category: string;
  image: string;
  available: boolean;
}

interface ComboCardProps {
  combo: {
    id: string;
    name: string;
    description: string;
    price: number;
    prepTime: number;
    calories: number;
    image: string;
    items: ComboItem[];
    available: boolean;
  };
  quantity: number;
  onAddToCart: () => void;
  onUpdateQuantity: (id: string, quantity: number) => void;
  isFavorite: boolean;
  onToggleFavorite: () => void;
}

export default function ComboCard({ 
  combo, 
  quantity, 
  onAddToCart, 
  onUpdateQuantity, 
  isFavorite, 
  onToggleFavorite 
}: ComboCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  const handleAddComboToCart = () => {
    // Add all combo items to cart as a single combo
    onAddToCart();
    toast.success(`${combo.name} added to cart with all items!`);
  };

  const handleToggleFavorite = () => {
    onToggleFavorite();
    if (isFavorite) {
      toast.success(`${combo.name} removed from favorites`);
    } else {
      toast.success(`${combo.name} added to favorites!`);
    }
  };

  const totalSavings = combo.items.reduce((total, item) => total + item.price, 0) - combo.price;
  const savingsPercentage = totalSavings > 0 ? Math.round((totalSavings / (combo.items.reduce((total, item) => total + item.price, 0))) * 100) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-2xl overflow-hidden border shadow-soft hover:shadow-card transition-all duration-300 group"
    >
      {/* Main Card */}
      <div className="relative">
        {/* Combo Image with Items Preview */}
        <div className="relative h-48 overflow-hidden">
          <img
            src={combo.image}
            alt={combo.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />
          
          {/* Combo Badge */}
          <div className="absolute top-3 left-3">
            <Badge className="bg-gradient-to-r from-orange-500 to-red-500 text-white border-0">
              COMBO
            </Badge>
          </div>

          {/* Savings Badge */}
          {savingsPercentage > 0 && (
            <div className="absolute top-3 right-3">
              <Badge className="bg-green-500 text-white border-0">
                Save {savingsPercentage}%
              </Badge>
            </div>
          )}

          {/* Items Preview Overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {combo.items.slice(0, 3).map((item, index) => (
                    <img
                      key={index}
                      src={item.image}
                      alt={item.name}
                      className="w-8 h-8 rounded-full border-2 border-white object-cover"
                    />
                  ))}
                  {combo.items.length > 3 && (
                    <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-600 flex items-center justify-center">
                      <span className="text-xs text-white">+{combo.items.length - 3}</span>
                    </div>
                  )}
                </div>
                <span className="text-white text-sm font-medium">
                  {combo.items.length} items
                </span>
              </div>
              
              <Dialog open={showDetails} onOpenChange={setShowDetails}>
                <DialogTrigger asChild>
                  <Button
                    size="sm"
                    variant="secondary"
                    className="bg-white/20 hover:bg-white/30 text-white border-white/30"
                  >
                    <Info className="h-4 w-4 mr-1" />
                    Details
                  </Button>
                </DialogTrigger>
              </Dialog>
            </div>
          </div>
        </div>

        {/* Card Content */}
        <div className="p-4">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold text-foreground">{combo.name}</h3>
            <div className="text-right">
              <span className="font-bold text-primary">₹{combo.price.toFixed(2)}</span>
              {totalSavings > 0 && (
                <div className="text-xs text-green-600 line-through">
                  ₹{(combo.price + totalSavings).toFixed(2)}
                </div>
              )}
            </div>
          </div>

          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
            {combo.description}
          </p>

          {/* Combo Items Summary */}
          <div className="mb-3 p-2 bg-muted/30 rounded-lg">
            <p className="text-xs font-medium text-muted-foreground mb-1">Includes:</p>
            <div className="flex flex-wrap gap-1">
              {combo.items.slice(0, 3).map((item) => (
                <span key={item.id} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                  {item.name}
                </span>
              ))}
              {combo.items.length > 3 && (
                <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded">
                  +{combo.items.length - 3} more
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4 text-secondary" />
                {combo.prepTime} min
              </div>
              <div className="flex items-center gap-1">
                <Flame className="h-4 w-4 text-secondary" />
                {combo.calories} cal
              </div>
            </div>

            {/* Favorite Button */}
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8"
              onClick={handleToggleFavorite}
            >
              <Heart 
                className={cn(
                  "h-4 w-4 transition-colors",
                  isFavorite ? "fill-red-500 text-red-500" : "text-muted-foreground"
                )} 
              />
            </Button>
          </div>

          {/* Add to Cart / Quantity Controls */}
          {quantity === 0 ? (
            <Button
              size="sm"
              onClick={handleAddComboToCart}
              className="w-full gradient-primary text-primary-foreground"
              disabled={!combo.available}
            >
              <ShoppingCart className="h-4 w-4 mr-2" />
              Add Combo to Cart
            </Button>
          ) : (
            <div className="flex items-center gap-2">
              <Button
                size="icon"
                variant="outline"
                className="h-8 w-8"
                onClick={() => onUpdateQuantity(combo.id, quantity - 1)}
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="font-semibold w-6 text-center">{quantity}</span>
              <Button
                size="icon"
                variant="outline"
                className="h-8 w-8"
                onClick={() => onUpdateQuantity(combo.id, quantity + 1)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Combo Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <div className="p-2 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg">
                <ShoppingCart className="h-5 w-5 text-white" />
              </div>
              {combo.name}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Combo Image */}
            <div className="relative h-48 rounded-lg overflow-hidden">
              <img
                src={combo.image}
                alt={combo.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3">
                <Badge className="bg-gradient-to-r from-orange-500 to-red-500 text-white border-0">
                  COMBO DEAL
                </Badge>
              </div>
              {savingsPercentage > 0 && (
                <div className="absolute top-3 right-3">
                  <Badge className="bg-green-500 text-white border-0">
                    Save {savingsPercentage}%
                  </Badge>
                </div>
              )}
            </div>

            {/* Combo Description */}
            <div>
              <h4 className="font-semibold mb-2">Description</h4>
              <p className="text-muted-foreground">{combo.description}</p>
            </div>

            {/* Combo Items */}
            <div>
              <h4 className="font-semibold mb-3">What's Included ({combo.items.length} items)</h4>
              <div className="space-y-3">
                {combo.items.map((item) => (
                  <div key={item.id} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                    <div className="flex-1">
                      <h5 className="font-medium">{item.name}</h5>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">₹{item.price.toFixed(2)}</div>
                      <div className="text-xs text-muted-foreground">{item.prepTime} min</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pricing Summary */}
            <div className="border-t pt-4">
              <h4 className="font-semibold mb-3">Pricing Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Individual Items Total:</span>
                  <span>₹{combo.items.reduce((total, item) => total + item.price, 0).toFixed(2)}</span>
                </div>
                {totalSavings > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Combo Discount:</span>
                    <span>-₹{totalSavings.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between font-semibold text-lg">
                  <span>Combo Price:</span>
                  <span className="text-primary">₹{combo.price.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Nutrition Info */}
            <div className="border-t pt-4">
              <h4 className="font-semibold mb-3">Nutrition & Timing</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Preparation: {combo.prepTime} minutes</span>
                </div>
                <div className="flex items-center gap-2">
                  <Flame className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Calories: {combo.calories}</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                onClick={handleToggleFavorite}
                variant="outline"
                className="flex-1"
              >
                <Heart className={cn(
                  "h-4 w-4 mr-2",
                  isFavorite ? "fill-red-500 text-red-500" : ""
                )} />
                {isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
              </Button>
              <Button
                onClick={handleAddComboToCart}
                className="flex-1 gradient-primary text-primary-foreground"
                disabled={!combo.available}
              >
                <ShoppingCart className="h-4 w-4 mr-2" />
                Add Combo to Cart
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
