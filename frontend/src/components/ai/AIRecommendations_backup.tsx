import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAIRecommendations, AIRecommendation } from '@/contexts/AIRecommendationContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Clock, 
  Star, 
  TrendingUp, 
  UtensilsCrossed,
  Sparkles,
  Heart,
  ShoppingCart,
  Info,
  RefreshCw,
  Package,
  Leaf,
  Flame,
  Cloud,
  Sun,
  CloudRain
} from 'lucide-react';
import { toast } from 'sonner';

interface AIRecommendationsProps {
  onAddToCart?: (item: any) => void;
  onViewItem?: (item: any) => void;
  maxItems?: number;
}

export function AIRecommendations({ onAddToCart, onViewItem, maxItems = 6 }: AIRecommendationsProps) {
  const { 
    allRecommendations, 
    isLoadingAll, 
    allError, 
    fetchAllRecommendations,
    fetchComboRecommendations,
    comboRecommendations,
    isLoadingCombos,
    saveInteraction 
  } = useAIRecommendations();
  
  const [activeTab, setActiveTab] = useState<'all' | 'preference' | 'time' | 'combo' | 'dietary'>('all');
  const [expandedReason, setExpandedReason] = useState<number | null>(null);

  // Fetch combo recommendations when component mounts or tab changes to combo
  useEffect(() => {
    if (activeTab === 'combo' && comboRecommendations.length === 0) {
      fetchComboRecommendations(3);
    }
  }, [activeTab, comboRecommendations.length, fetchComboRecommendations]);

  const handleItemClick = async (recommendation: AIRecommendation, action: 'view' | 'order' | 'favorite') => {
    try {
      // Save interaction for AI learning
      await saveInteraction({
        menu_item_id: recommendation.menu_item_id,
        interaction_type: action,
        context_data: {
          recommendation_type: recommendation.recommendation_type,
          confidence: recommendation.confidence,
          timestamp: new Date().toISOString()
        }
      });

      // Handle different actions
      if (action === 'view' && onViewItem) {
        onViewItem(recommendation);
      } else if (action === 'order' && onAddToCart) {
        if (recommendation.recommendation_type === 'combo') {
          // For combos, add all individual items to cart
          const comboItems = (recommendation as any).combo_items || [];
          
          if (comboItems.length > 0) {
            // Add each combo item to cart by calling onAddToCart for each
            comboItems.forEach((item: any) => {
              const menuItem = {
                id: item.id?.toString() || item.menu_item_id?.toString(),
                name: item.name || item.item_name,
                description: item.description || '',
                price: item.price || 0,
                prepTime: item.prep_time || item.base_prep_time || 15,
                calories: item.calories || 200,
                category: item.category || 'Combo Item',
                image: item.image_url || item.image || '/api/placeholder/300/200',
                available: item.is_available !== false,
                menu_item_id: item.id || item.menu_item_id
              };
              
              // Add the item with proper quantity by calling onAddToCart multiple times
              const quantity = item.quantity || 1;
              for (let i = 0; i < quantity; i++) {
                onAddToCart(menuItem);
              }
            });
            
            toast.success(`Added ${recommendation.name} combo with ${comboItems.length} items to cart!`, {
              description: `All ${comboItems.length} items have been added to your cart`,
              duration: 3000
            });
          } else {
            // Fallback for combos without item details
            onAddToCart(recommendation);
            toast.success(`Added ${recommendation.name} combo to cart!`);
          }
        } else {
          // For regular items
          onAddToCart(recommendation);
          toast.success(`Added ${recommendation.name} to cart!`);
        }
      } else if (action === 'favorite') {
        toast.success(`Added ${recommendation.name} to favorites!`);
      }
    } catch (error) {
      console.error('Error handling item interaction:', error);
      toast.error('Failed to process action');
    }
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'preference_based': return <Brain className="h-4 w-4" />;
      case 'time_based': return <Clock className="h-4 w-4" />;
      case 'combo': return <Package className="h-4 w-4" />;
      case 'dietary': return <Leaf className="h-4 w-4" />;
      case 'calorie_conscious': return <Flame className="h-4 w-4" />;
      case 'weather_based': return <Cloud className="h-4 w-4" />;
      default: return <Sparkles className="h-4 w-4" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 border-green-200';
    if (confidence >= 0.6) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (confidence >= 0.4) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getMealTypeBadge = (mealType?: string) => {
    if (!mealType) return null;
    
    const mealConfig = {
      breakfast: { label: 'Breakfast', color: 'bg-orange-100 text-orange-800' },
      lunch: { label: 'Lunch', color: 'bg-green-100 text-green-800' },
      snack: { label: 'Snack', color: 'bg-purple-100 text-purple-800' },
      dinner: { label: 'Dinner', color: 'bg-blue-100 text-blue-800' },
      late_night: { label: 'Late Night', color: 'bg-indigo-100 text-indigo-800' }
    };
    
    const config = mealConfig[mealType as keyof typeof mealConfig];
    return config ? (
      <Badge className={`text-xs ${config.color}`}>
        {config.label}
      </Badge>
    ) : null;
  };

  const renderComboCard = (recommendation: AIRecommendation, index: number) => {
    // Extract combo items from the description or additional data
    const comboItems = (recommendation as any).combo_items || [];
    const savings = (recommendation as any).savings || 0;
    
    return (
      <motion.div
        key={recommendation.menu_item_id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
      >
        <Card className="h-full hover:shadow-md transition-shadow cursor-pointer group border-2 border-dashed border-primary/20">
          <div className="relative">
            <div className="h-32 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-t-lg flex items-center justify-center">
              <Package className="h-12 w-12 text-primary/60" />
            </div>
            
            <div className="absolute top-2 right-2 flex gap-1">
              <Badge className={`text-xs ${getConfidenceColor(recommendation.confidence)}`}>
                {Math.round(recommendation.confidence * 100)}% match
              </Badge>
              <Badge variant="secondary" className="text-xs flex items-center gap-1">
                <Package className="h-3 w-3" />
                Combo
              </Badge>
              {savings > 0 && (
                <Badge className="text-xs bg-green-500 text-white">
                  Save {savings}%
                </Badge>
              )}
            </div>
            
            <div className="absolute top-2 left-2">
              <Badge variant="secondary" className="text-xs flex items-center gap-1 bg-primary/10">
                {getRecommendationIcon(recommendation.recommendation_type)}
                {recommendation.recommendation_type.replace('_', ' ')}
              </Badge>
            </div>
          </div>
          
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-sm leading-tight text-primary">
                    {recommendation.name}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {recommendation.description}
                  </p>
                  
                  {/* Display combo items */}
                  {comboItems.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs font-medium text-muted-foreground">Includes:</p>
                      <div className="space-y-1">
                        {comboItems.slice(0, 3).map((item: any, itemIndex: number) => (
                          <div key={itemIndex} className="flex items-center gap-2 text-xs text-muted-foreground">
                            <div className="w-1 h-1 bg-primary rounded-full"></div>
                            <span>{item.name || item.item_name}</span>
                            {item.quantity && <span className="text-muted-foreground/70">x{item.quantity}</span>}
                          </div>
                        ))}
                        {comboItems.length > 3 && (
                          <p className="text-xs text-muted-foreground/70">
                            +{comboItems.length - 3} more items
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0 ml-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleItemClick(recommendation, 'favorite');
                  }}
                >
                  <Heart className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-primary text-lg">
                    ₹{recommendation.price.toFixed(2)}
                  </span>
                  <p className="text-xs text-muted-foreground">
                    {comboItems.length} items
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={() => handleItemClick(recommendation, 'order')}
                  className="h-7 text-xs bg-gradient-to-r from-primary to-secondary text-primary-foreground hover:from-primary/90 hover:to-secondary/90"
                >
                  <ShoppingCart className="h-3 w-3 mr-1" />
                  Add Combo
                </Button>
              </div>
              
              {recommendation.reasoning && (
                <div className="mt-3 pt-3 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpandedReason(
                      expandedReason === recommendation.menu_item_id ? null : recommendation.menu_item_id
                    )}
                    className="h-6 text-xs text-muted-foreground p-0"
                  >
                    <TrendingUp className="h-3 w-3 mr-1" />
                    Why recommended?
                  </Button>
                  
                  <AnimatePresence>
                    {expandedReason === recommendation.menu_item_id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-xs text-muted-foreground mt-2 p-2 bg-gray-50 rounded"
                      >
                        {recommendation.reasoning}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const renderCalorieCard = (recommendation: AIRecommendation, index: number) => {
    const calories = (recommendation as any).calories || 0;
    const caloriePercentage = (recommendation as any).calorie_percentage || 0;
    const calorieTags = (recommendation as any).calorie_tags || [];
    
    return (
      <motion.div
        key={recommendation.menu_item_id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
      >
        <Card className="h-full hover:shadow-md transition-shadow cursor-pointer group border-2 border-orange-200/30">
          <div className="relative">
            {recommendation.image_url && (
              <div className="h-32 bg-gray-100 rounded-t-lg overflow-hidden">
                <img
                  src={recommendation.image_url}
                  alt={recommendation.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.currentTarget.src = '/api/placeholder/300/200';
                  }}
                />
              </div>
            )}
            
            <div className="absolute top-2 right-2 flex gap-1 flex-col">
              <Badge className={`text-xs ${getConfidenceColor(recommendation.confidence)}`}>
                {Math.round(recommendation.confidence * 100)}% match
              </Badge>
              <Badge variant="secondary" className="text-xs flex items-center gap-1 bg-orange-100 text-orange-800">
                <Flame className="h-3 w-3" />
                {calories} cal
              </Badge>
            </div>
            
            <div className="absolute top-2 left-2">
              <Badge variant="secondary" className="text-xs flex items-center gap-1 bg-orange-50 text-orange-700">
                {getRecommendationIcon(recommendation.recommendation_type)}
                Calorie Smart
              </Badge>
            </div>
            
            {caloriePercentage > 0 && (
              <div className="absolute bottom-2 left-2">
                <div className="text-xs font-medium text-orange-700 bg-orange-100 px-2 py-1 rounded">
                  {caloriePercentage}% daily goal
                </div>
              </div>
            )}
          </div>
          
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-sm leading-tight line-clamp-2">
                    {recommendation.name}
                  </h3>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {recommendation.description}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0 ml-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleItemClick(recommendation, 'favorite');
                  }}
                >
                  <Heart className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-1">
                {calorieTags.map((tag: string, i: number) => (
                  <Badge key={i} variant="outline" className="text-xs border-orange-200 text-orange-700">
                    {tag}
                  </Badge>
                ))}
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-primary">
                    ₹{recommendation.price.toFixed(2)}
                  </span>
                  <p className="text-xs text-muted-foreground">
                    {calories > 0 && `${calories} calories`}
                  </p>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleItemClick(recommendation, 'view')}
                    className="h-7 text-xs"
                  >
                    <Info className="h-3 w-3 mr-1" />
                    View
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleItemClick(recommendation, 'order')}
                    className="h-7 text-xs"
                  >
                    <ShoppingCart className="h-3 w-3 mr-1" />
                    Add
                  </Button>
                </div>
              </div>
              
              {recommendation.reasoning && (
                <div className="mt-3 pt-3 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpandedReason(
                      expandedReason === recommendation.menu_item_id ? null : recommendation.menu_item_id
                    )}
                    className="h-6 text-xs text-muted-foreground p-0"
                  >
                    <TrendingUp className="h-3 w-3 mr-1" />
                    Why recommended?
                  </Button>
                  
                  <AnimatePresence>
                    {expandedReason === recommendation.menu_item_id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-xs text-muted-foreground mt-2 p-2 bg-gray-50 rounded"
                      >
                        {recommendation.reasoning}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const renderWeatherCard = (recommendation: AIRecommendation, index: number) => {
    const weatherData = (recommendation as any).weather_data || {};
    const weatherTags = (recommendation as any).weather_tags || [];
    const comfortLevel = (recommendation as any).comfort_level || 'Balanced';
    
    const getWeatherIcon = (condition: string) => {
      switch (condition.toLowerCase()) {
        case 'rainy': return <CloudRain className="h-4 w-4" />;
        case 'sunny': return <Sun className="h-4 w-4" />;
        default: return <Cloud className="h-4 w-4" />;
      }
    };
    
    return (
      <motion.div
        key={recommendation.menu_item_id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
      >
        <Card className="h-full hover:shadow-md transition-shadow cursor-pointer group border-2 border-blue-200/30">
          <div className="relative">
            {recommendation.image_url && (
              <div className="h-32 bg-gray-100 rounded-t-lg overflow-hidden">
                <img
                  src={recommendation.image_url}
                  alt={recommendation.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.currentTarget.src = '/api/placeholder/300/200';
                  }}
                />
              </div>
            )}
            
            <div className="absolute top-2 right-2 flex gap-1 flex-col">
              <Badge className={`text-xs ${getConfidenceColor(recommendation.confidence)}`}>
                {Math.round(recommendation.confidence * 100)}% match
              </Badge>
              <Badge variant="secondary" className="text-xs flex items-center gap-1 bg-blue-100 text-blue-800">
                {getWeatherIcon(weatherData.condition || 'clear')}
                {weatherData.temperature || 25}°C
              </Badge>
            </div>
            
            <div className="absolute top-2 left-2">
              <Badge variant="secondary" className="text-xs flex items-center gap-1 bg-blue-50 text-blue-700">
                {getRecommendationIcon(recommendation.recommendation_type)}
                Weather Smart
              </Badge>
            </div>
            
            <div className="absolute bottom-2 left-2">
              <div className="text-xs font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded">
                {comfortLevel}
              </div>
            </div>
          </div>
          
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-sm leading-tight line-clamp-2">
                    {recommendation.name}
                  </h3>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {recommendation.description}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0 ml-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleItemClick(recommendation, 'favorite');
                  }}
                >
                  <Heart className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-1">
                {weatherTags.map((tag: string, i: number) => (
                  <Badge key={i} variant="outline" className="text-xs border-blue-200 text-blue-700">
                    {tag}
                  </Badge>
                ))}
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-primary">
                    ₹{recommendation.price.toFixed(2)}
                  </span>
                  <p className="text-xs text-muted-foreground">
                    Perfect for {weatherData.condition || 'current'} weather
                  </p>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleItemClick(recommendation, 'view')}
                    className="h-7 text-xs"
                  >
                    <Info className="h-3 w-3 mr-1" />
                    View
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleItemClick(recommendation, 'order')}
                    className="h-7 text-xs"
                  >
                    <ShoppingCart className="h-3 w-3 mr-1" />
                    Add
                  </Button>
                </div>
              </div>
              
              {recommendation.reasoning && (
                <div className="mt-3 pt-3 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpandedReason(
                      expandedReason === recommendation.menu_item_id ? null : recommendation.menu_item_id
                    )}
                    className="h-6 text-xs text-muted-foreground p-0"
                  >
                    <TrendingUp className="h-3 w-3 mr-1" />
                    Why recommended?
                  </Button>
                  
                  <AnimatePresence>
                    {expandedReason === recommendation.menu_item_id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-xs text-muted-foreground mt-2 p-2 bg-gray-50 rounded"
                      >
                        {recommendation.reasoning}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const isLoading = activeTab === 'combo' ? isLoadingCombos : isLoadingAll;
  const error = activeTab === 'combo' ? null : allError; // Combo recommendations don't have error state yet
  const displayRecommendations = activeTab === 'combo' 
    ? comboRecommendations.slice(0, maxItems)
    : allRecommendations.slice(0, maxItems);

  if (isLoading) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            AI Recommendations
            <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-gray-200 h-32 rounded-lg mb-2"></div>
                <div className="bg-gray-200 h-4 rounded mb-1"></div>
                <div className="bg-gray-200 h-3 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (allError) {
    return (
      <Card className="mb-6 border-red-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <Brain className="h-5 w-5" />
            AI Recommendations Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600 text-sm mb-3">{allError}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => fetchAllRecommendations()}
            className="text-red-600 border-red-200"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!displayRecommendations.length && !isLoading) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            AI Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Sparkles className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>No recommendations available yet.</p>
            <p className="text-sm">Start ordering to get personalized suggestions!</p>
          </div>

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          AI Recommendations
          <Badge variant="secondary" className="ml-2">
            {displayRecommendations.length} items
          </Badge>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Personalized suggestions based on your preferences and ordering history
        </p>
      </CardHeader>
      
      <CardContent>
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 flex-wrap">
          <Button
            variant={activeTab === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('all')}
            className="text-xs"
          >
            All
          </Button>
          <Button
            variant={activeTab === 'preference' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('preference')}
            className="text-xs"
          >
            Preferences
          </Button>
          <Button
            variant={activeTab === 'time' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('time')}
            className="text-xs"
          >
            Time-based
          </Button>
          <Button
            variant={activeTab === 'combo' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('combo')}
            className="text-xs"
          >
            Combos
          </Button>
          <Button
            variant={activeTab === 'dietary' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('dietary')}
            className="text-xs"
          >
            Dietary
          </Button>
        </div>

        {/* Recommendations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {displayRecommendations.map((recommendation, index) => (
              recommendation.recommendation_type === 'combo' 
                ? renderComboCard(recommendation, index)
                : recommendation.recommendation_type === 'calorie_conscious'
                ? renderCalorieCard(recommendation, index)
                : recommendation.recommendation_type === 'weather_based'
                ? renderWeatherCard(recommendation, index)
                : renderStandardCard(recommendation, index)
                        </div>
                        
                        <div className="absolute top-2 left-2">
                          <Badge variant="secondary" className="text-xs flex items-center gap-1">
                            {getRecommendationIcon(recommendation.recommendation_type)}
                            {recommendation.recommendation_type.replace('_', ' ')}
                          </Badge>
                        </div>
                      </div>
                      
                      <CardContent className="p-4">
                        <div className="space-y-2">
                          <div className="flex items-start justify-between">
                            <h3 className="font-semibold text-sm leading-tight line-clamp-2">
                              {recommendation.name}
                            </h3>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6 shrink-0 ml-2"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleItemClick(recommendation, 'favorite');
                              }}
                            >
                              <Heart className="h-4 w-4" />
                            </Button>
                          </div>
                          
                          {recommendation.description && (
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {recommendation.description}
                            </p>
                          )}
                          
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-primary">
                              ₹{recommendation.price.toFixed(2)}
                            </span>
                            <div className="flex gap-1">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleItemClick(recommendation, 'view')}
                                className="h-7 text-xs"
                              >
                                <Info className="h-3 w-3 mr-1" />
                                View
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => handleItemClick(recommendation, 'order')}
                                className="h-7 text-xs"
                              >
                                <ShoppingCart className="h-3 w-3 mr-1" />
                                Add
                              </Button>
                            </div>
                          </div>
                          
                          {recommendation.reasoning && (
                            <div className="mt-3 pt-3 border-t">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setExpandedReason(
                                  expandedReason === recommendation.menu_item_id ? null : recommendation.menu_item_id
                                )}
                                className="h-6 text-xs text-muted-foreground p-0"
                              >
                                <TrendingUp className="h-3 w-3 mr-1" />
                                Why recommended?
                              </Button>
                              
                              <AnimatePresence>
                                {expandedReason === recommendation.menu_item_id && (
                                  <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="text-xs text-muted-foreground mt-2 p-2 bg-gray-50 rounded"
                                  >
                                    {recommendation.reasoning}
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                )
            ))}
          </AnimatePresence>
        </div>
        
        {allRecommendations.length > maxItems && (
          <div className="mt-4 text-center">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchAllRecommendations(10, 5)}
            >
              Load More Recommendations
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
