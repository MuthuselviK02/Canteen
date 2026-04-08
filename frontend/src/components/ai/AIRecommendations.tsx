import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAIRecommendations, AIRecommendation } from '@/contexts/AIRecommendationContext';
import { useFavorites } from '@/contexts/FavoritesContext';
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
  Leaf,
  Flame,
  Cloud,
  Sun,
  CloudRain
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { toast } from 'sonner';

interface AIRecommendationsProps {
  onAddToCart?: (item: any) => void;
  onViewItem?: (item: any) => void;
  maxItems?: number;
}

export function AIRecommendations({ onAddToCart, onViewItem, maxItems = 6 }: AIRecommendationsProps) {
  const { 
    preferenceRecommendations,
    timeBasedRecommendations,
    dietaryRecommendations,
    calorieConsciousRecommendations,
    weatherBasedRecommendations,
    allRecommendations, 
    isLoadingPreferences,
    isLoadingTimeBased,
    isLoadingDietary,
    isLoadingAll, 
    allError, 
    fetchPreferenceRecommendations,
    fetchTimeBasedRecommendations,
    fetchDietaryRecommendations,
    fetchAllRecommendations,
    saveInteraction 
  } = useAIRecommendations();
  
  const { toggleFavorite, isFavorite } = useFavorites();
  
  const [activeTab, setActiveTab] = useState<'all' | 'preference' | 'time' | 'dietary'>('all');
  const [expandedReason, setExpandedReason] = useState<number | null>(null);

  // Fetch recommendations when component mounts
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        await fetchAllRecommendations(3, 3, 3, 3, 2000, 3);
      } catch (error) {
        console.error('Error fetching initial recommendations:', error);
        // Don't crash on initial load
      }
    };
    
    fetchInitialData();
  }, []);

  // Fetch specific recommendations when tab changes
  useEffect(() => {
    const fetchTabRecommendations = async () => {
      try {
        console.log('Tab changed to:', activeTab);
        switch (activeTab) {
          case 'preference':
            console.log('Fetching preference recommendations');
            await fetchPreferenceRecommendations(6);
            break;
          case 'time':
            console.log('Fetching time-based recommendations');
            await fetchTimeBasedRecommendations(6);
            break;
          case 'dietary':
            console.log('Fetching dietary recommendations');
            await fetchDietaryRecommendations(6);
            break;
          case 'all':
            // Already fetched on mount
            console.log('Using all recommendations (already fetched)');
            break;
        }
      } catch (error) {
        console.error(`Error fetching ${activeTab} recommendations:`, error);
        // Don't crash the page, just log the error
      }
    };

    if (activeTab !== 'all') {
      fetchTabRecommendations();
    }
  }, [activeTab]); // Remove function dependencies to prevent infinite loops

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
        // For regular items
        onAddToCart(recommendation);
        toast.success(`Added ${recommendation.name} to cart!`);
      } else if (action === 'favorite') {
        // Add to favorites using the favorites context
        const favoriteItem = {
          id: recommendation.menu_item_id.toString(),
          name: recommendation.name,
          description: recommendation.description || '',
          price: recommendation.price,
          image: recommendation.image_url ? 
            (recommendation.image_url.startsWith('http') ? recommendation.image_url : buildImageUrl(recommendation.image_url)) 
            : '/static/images/default_food.jpg',
          category: recommendation.category || 'Unknown',
          type: 'menu_item' as const
        };
        
        const wasFavorite = isFavorite(recommendation.menu_item_id.toString());
        toggleFavorite(favoriteItem);
        
        toast.success(
          wasFavorite 
            ? `Removed ${recommendation.name} from favorites!`
            : `Added ${recommendation.name} to favorites!`
        );
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

  const renderStandardCard = (recommendation: AIRecommendation, index: number) => {
    return (
      <motion.div
        key={recommendation.menu_item_id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
      >
        <Card className="h-full hover:shadow-md transition-shadow cursor-pointer group">
          <div className="relative">
            {recommendation.image_url && (
              <div className="h-32 bg-gray-100 rounded-t-lg overflow-hidden">
                <img
                  src={recommendation.image_url.startsWith('http') ? recommendation.image_url : buildImageUrl(recommendation.image_url)}
                  alt={recommendation.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = buildImageUrl('/static/images/default_food.jpg');
                  }}
                />
              </div>
            )}
            
            <div className="absolute top-2 right-2 flex gap-1">
              <Badge className={`text-xs ${getConfidenceColor(recommendation.confidence)}`}>
                {Math.round(recommendation.confidence * 100)}% match
              </Badge>
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
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`h-6 w-6 shrink-0 ml-2 ${
                    isFavorite(recommendation.menu_item_id.toString())
                      ? 'text-red-500 hover:text-red-600'
                      : 'text-muted-foreground hover:text-red-500'
                  }`}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleItemClick(recommendation, 'favorite');
                  }}
                >
                  <Heart 
                    className={`h-4 w-4 ${
                      isFavorite(recommendation.menu_item_id.toString())
                        ? 'fill-current'
                        : ''
                    }`} 
                  />
                </Button>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-primary text-lg">
                    ₹{recommendation.price.toFixed(2)}
                  </span>
                  <p className="text-xs text-muted-foreground">
                    {recommendation.category}
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={() => handleItemClick(recommendation, 'order')}
                  className="h-7 text-xs"
                >
                  <ShoppingCart className="h-3 w-3 mr-1" />
                  Add
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

  // Get the appropriate loading state based on active tab
  const isLoading = activeTab === 'all' 
    ? isLoadingAll 
    : activeTab === 'preference' 
    ? isLoadingPreferences 
    : activeTab === 'time' 
    ? isLoadingTimeBased 
    : activeTab === 'dietary' 
    ? isLoadingDietary 
    : isLoadingAll;
  
  const error = allError;
  
  // Filter recommendations based on active tab
  const displayRecommendations = (() => {
    switch (activeTab) {
      case 'preference':
        return preferenceRecommendations.slice(0, maxItems);
      case 'time':
        return timeBasedRecommendations.slice(0, maxItems);
      case 'dietary':
        return dietaryRecommendations.slice(0, maxItems);
      case 'all':
      default:
        return allRecommendations.slice(0, maxItems);
    }
  })();

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
            {[...Array(3)].map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="h-32 bg-gray-200 rounded-t-lg"></div>
                <div className="p-4 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            AI Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">Failed to load recommendations</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchAllRecommendations(3, 3, 3, 3, 2000, 3)}
              className="text-red-600 border-red-200"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
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
        </CardContent>
      </Card>
    );
  }

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
              renderStandardCard(recommendation, index)
            ))}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
