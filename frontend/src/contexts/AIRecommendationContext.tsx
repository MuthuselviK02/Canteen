import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';

export interface AIRecommendation {
  menu_item_id: number;
  name: string;
  description?: string;
  price: number;
  category?: string;
  image_url?: string;
  score: number;
  confidence: number;
  reasoning: string;
  recommendation_type: string;
  meal_type?: string;
}

export interface AIRecommendationResponse {
  recommendations: AIRecommendation[];
  total_count: number;
  recommendation_types: string[];
}

export interface UserInteraction {
  menu_item_id: number;
  interaction_type: 'view' | 'order' | 'favorite' | 'rating';
  interaction_value?: number;
  context_data?: Record<string, any>;
}

interface AIRecommendationContextType {
  // Recommendations
  preferenceRecommendations: AIRecommendation[];
  timeBasedRecommendations: AIRecommendation[];
  dietaryRecommendations: AIRecommendation[];
  calorieConsciousRecommendations: AIRecommendation[];
  weatherBasedRecommendations: AIRecommendation[];
  allRecommendations: AIRecommendation[];
  
  // Loading states
  isLoadingPreferences: boolean;
  isLoadingTimeBased: boolean;
  isLoadingDietary: boolean;
  isLoadingCalorie: boolean;
  isLoadingWeather: boolean;
  isLoadingAll: boolean;
  
  // Error states
  preferencesError: string | null;
  timeBasedError: string | null;
  dietaryError: string | null;
  calorieError: string | null;
  weatherError: string | null;
  allError: string | null;
  
  // Actions
  fetchPreferenceRecommendations: (limit?: number) => Promise<void>;
  fetchTimeBasedRecommendations: (limit?: number) => Promise<void>;
  fetchDietaryRecommendations: (limit?: number, restrictions?: string[]) => Promise<void>;
  fetchCalorieConsciousRecommendations: (limit?: number, dailyGoal?: number) => Promise<void>;
  fetchWeatherBasedRecommendations: (limit?: number) => Promise<void>;
  fetchAllRecommendations: (preferenceLimit?: number, timeLimit?: number, dietaryLimit?: number, calorieLimit?: number, dailyGoal?: number, weatherLimit?: number) => Promise<void>;
  saveInteraction: (interaction: UserInteraction) => Promise<void>;
  
  // User preferences
  userPreferences: Record<string, any> | null;
  fetchUserPreferences: () => Promise<void>;
  updateUserPreference: (type: string, value: string, weight?: number) => Promise<void>;
}

const AIRecommendationContext = createContext<AIRecommendationContextType | undefined>(undefined);

export function AIRecommendationProvider({ children }: { children: ReactNode }) {
  const [preferenceRecommendations, setPreferenceRecommendations] = useState<AIRecommendation[]>([]);
  const [timeBasedRecommendations, setTimeBasedRecommendations] = useState<AIRecommendation[]>([]);
  const [dietaryRecommendations, setDietaryRecommendations] = useState<AIRecommendation[]>([]);
  const [calorieConsciousRecommendations, setCalorieConsciousRecommendations] = useState<AIRecommendation[]>([]);
  const [weatherBasedRecommendations, setWeatherBasedRecommendations] = useState<AIRecommendation[]>([]);
  const [allRecommendations, setAllRecommendations] = useState<AIRecommendation[]>([]);
  
  const [isLoadingPreferences, setIsLoadingPreferences] = useState(false);
  const [isLoadingTimeBased, setIsLoadingTimeBased] = useState(false);
  const [isLoadingDietary, setIsLoadingDietary] = useState(false);
  const [isLoadingCalorie, setIsLoadingCalorie] = useState(false);
  const [isLoadingWeather, setIsLoadingWeather] = useState(false);
  const [isLoadingAll, setIsLoadingAll] = useState(false);
  
  const [preferencesError, setPreferencesError] = useState<string | null>(null);
  const [timeBasedError, setTimeBasedError] = useState<string | null>(null);
  const [dietaryError, setDietaryError] = useState<string | null>(null);
  const [calorieError, setCalorieError] = useState<string | null>(null);
  const [weatherError, setWeatherError] = useState<string | null>(null);
  const [allError, setAllError] = useState<string | null>(null);
  
  const [userPreferences, setUserPreferences] = useState<Record<string, any> | null>(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('canteen_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  const fetchPreferenceRecommendations = async (limit: number = 10) => {
    setIsLoadingPreferences(true);
    setPreferencesError(null);
    
    try {
      const response = await fetch(
        buildApiUrl(`/api/ai/recommendations/preferences?limit=${limit}`),
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AIRecommendationResponse = await response.json();
      console.log('Preference recommendations data received:', data);
      
      // If API returns empty data, use fallback
      if (data.recommendations && data.recommendations.length > 0) {
        setPreferenceRecommendations(data.recommendations);
      } else {
        console.log('API returned empty preference recommendations, using fallback data');
        const fallbackData: AIRecommendation[] = [
          {
            menu_item_id: 1,
            name: 'Sample Preference Item 1',
            description: 'This is a sample preference-based recommendation',
            price: 120,
            category: 'Main Course',
            image_url: '/static/images/default_food.jpg',
            score: 0.85,
            confidence: 0.80,
            reasoning: 'Based on your previous preferences',
            recommendation_type: 'preference_based'
          },
          {
            menu_item_id: 2,
            name: 'Sample Preference Item 2',
            description: 'Another preference-based recommendation',
            price: 80,
            category: 'Starter',
            image_url: '/static/images/default_food.jpg',
            score: 0.78,
            confidence: 0.75,
            reasoning: 'Matches your taste profile',
            recommendation_type: 'preference_based'
          }
        ];
        setPreferenceRecommendations(fallbackData);
        console.log('Fallback preference data set:', fallbackData);
      }
    } catch (error) {
      console.error('Error fetching preference recommendations:', error);
      setPreferencesError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
      
      // Provide fallback sample data to prevent crashes
      const fallbackData: AIRecommendation[] = [
        {
          menu_item_id: 1,
          name: 'Sample Preference Item 1',
          description: 'This is a sample preference-based recommendation',
          price: 120,
          category: 'Main Course',
          image_url: '/static/images/default_food.jpg',
          score: 0.85,
          confidence: 0.80,
          reasoning: 'Based on your previous preferences',
          recommendation_type: 'preference_based'
        },
        {
          menu_item_id: 2,
          name: 'Sample Preference Item 2',
          description: 'Another preference-based recommendation',
          price: 80,
          category: 'Starter',
          image_url: '/static/images/default_food.jpg',
          score: 0.78,
          confidence: 0.75,
          reasoning: 'Matches your taste profile',
          recommendation_type: 'preference_based'
        }
      ];
      setPreferenceRecommendations(fallbackData);
    } finally {
      setIsLoadingPreferences(false);
    }
  };

  const fetchTimeBasedRecommendations = async (limit: number = 5) => {
    setIsLoadingTimeBased(true);
    setTimeBasedError(null);
    
    try {
      const response = await fetch(
        buildApiUrl(`/api/ai/recommendations/time-based?limit=${limit}`),
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AIRecommendationResponse = await response.json();
      console.log('Time-based recommendations data received:', data);
      
      // If API returns empty data, use fallback
      if (data.recommendations && data.recommendations.length > 0) {
        setTimeBasedRecommendations(data.recommendations);
      } else {
        console.log('API returned empty time-based recommendations, using fallback data');
        const fallbackData: AIRecommendation[] = [
          {
            menu_item_id: 3,
            name: 'Lunch Special',
            description: 'Perfect for lunch time',
            price: 150,
            category: 'Main Course',
            image_url: '/static/images/default_food.jpg',
            score: 0.82,
            confidence: 0.78,
            reasoning: 'Ideal for current time of day',
            recommendation_type: 'time_based',
            meal_type: 'lunch'
          },
          {
            menu_item_id: 4,
            name: 'Evening Snack',
            description: 'Light evening option',
            price: 60,
            category: 'Snack',
            image_url: '/static/images/default_food.jpg',
            score: 0.75,
            confidence: 0.70,
            reasoning: 'Good choice for evening time',
            recommendation_type: 'time_based',
            meal_type: 'snack'
          }
        ];
        setTimeBasedRecommendations(fallbackData);
        console.log('Fallback time-based data set:', fallbackData);
      }
    } catch (error) {
      console.error('Error fetching time-based recommendations:', error);
      setTimeBasedError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
      
      // Provide fallback sample data to prevent crashes
      const fallbackData: AIRecommendation[] = [
        {
          menu_item_id: 3,
          name: 'Lunch Special',
          description: 'Perfect for lunch time',
          price: 150,
          category: 'Main Course',
          image_url: '/static/images/default_food.jpg',
          score: 0.82,
          confidence: 0.78,
          reasoning: 'Ideal for current time of day',
          recommendation_type: 'time_based',
          meal_type: 'lunch'
        },
        {
          menu_item_id: 4,
          name: 'Evening Snack',
          description: 'Light evening option',
          price: 60,
          category: 'Snack',
          image_url: '/static/images/default_food.jpg',
          score: 0.75,
          confidence: 0.70,
          reasoning: 'Good choice for evening time',
          recommendation_type: 'time_based',
          meal_type: 'snack'
        }
      ];
      setTimeBasedRecommendations(fallbackData);
    } finally {
      setIsLoadingTimeBased(false);
    }
  };

  const fetchDietaryRecommendations = async (limit: number = 5, restrictions?: string[]) => {
    setIsLoadingDietary(true);
    setDietaryError(null);
    
    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (restrictions && restrictions.length > 0) {
        params.append('dietary_restrictions', restrictions.join(','));
      }
      
      console.log('Fetching dietary recommendations from:', buildApiUrl(`/api/ai/recommendations/dietary?${params}`));
      
      const response = await fetch(
        buildApiUrl(`/api/ai/recommendations/dietary?${params}`),
        {
          headers: getAuthHeaders()
        }
      );
      
      console.log('Dietary recommendations response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AIRecommendationResponse = await response.json();
      console.log('Dietary recommendations data received:', data);
      
      // If API returns empty data, fetch real menu items and filter for dietary category
      if (data.recommendations && data.recommendations.length > 0) {
        setDietaryRecommendations(data.recommendations);
      } else {
        console.log('API returned empty dietary recommendations, fetching real dietary menu items');
        try {
          // Fetch all menu items from backend
          const menuResponse = await fetch(buildApiUrl('/api/menu/'), {
            headers: getAuthHeaders()
          });
          
          if (menuResponse.ok) {
            const menuItems = await menuResponse.json();
            console.log('Menu items fetched:', menuItems);
            
            // Filter for dietary category items and convert to AIRecommendation format
            const dietaryItems = menuItems
              .filter(item => item.category === 'Dietary' || item.category === 'Side Dish' || item.category === 'Starter')
              .slice(0, 6)
              .map(item => ({
                menu_item_id: item.id,
                name: item.name,
                description: item.description,
                price: item.price,
                category: item.category,
                image_url: item.image_url || '/static/images/default_food.jpg',
                score: 0.85 + Math.random() * 0.1, // Random score between 0.85-0.95
                confidence: 0.80 + Math.random() * 0.1, // Random confidence between 0.80-0.90
                reasoning: `${item.category.toLowerCase()} option - ${item.calories || 'moderate'} calories, perfect for dietary preferences`,
                recommendation_type: 'dietary'
              }));
            
            console.log('Filtered dietary items:', dietaryItems);
            
            if (dietaryItems.length > 0) {
              setDietaryRecommendations(dietaryItems);
            } else {
              // Fallback to sample data if no dietary items found
              const fallbackData: AIRecommendation[] = [
                {
                  menu_item_id: 11,
                  name: 'Salad',
                  description: 'Fresh mixed salad with lemon dressing',
                  price: 35,
                  category: 'Side Dish',
                  image_url: buildImageUrl('/static/images/salad.jpg'),
                  score: 0.92,
                  confidence: 0.90,
                  reasoning: 'Low calorie (60 cal) and fresh - perfect for dietary preferences',
                  recommendation_type: 'dietary'
                },
                {
                  menu_item_id: 12,
                  name: 'Veg Soup',
                  description: 'Healthy mixed vegetable soup',
                  price: 45,
                  category: 'Starter',
                  image_url: buildImageUrl('/static/images/soup.jpg'),
                  score: 0.88,
                  confidence: 0.85,
                  reasoning: 'Nutritious and light (90 cal) - excellent for health-conscious choices',
                  recommendation_type: 'dietary'
                }
              ];
              setDietaryRecommendations(fallbackData);
              console.log('Using fallback dietary data with local images');
            }
          } else {
            throw new Error('Failed to fetch menu items');
          }
        } catch (menuError) {
          console.error('Error fetching menu items:', menuError);
          // Final fallback with local image paths
          const fallbackData: AIRecommendation[] = [
            {
              menu_item_id: 11,
              name: 'Salad',
              description: 'Fresh mixed salad with lemon dressing',
              price: 35,
              category: 'Side Dish',
              image_url: buildImageUrl('/static/images/salad.jpg'),
              score: 0.92,
              confidence: 0.90,
              reasoning: 'Low calorie (60 cal) and fresh - perfect for dietary preferences',
              recommendation_type: 'dietary'
            }
          ];
          setDietaryRecommendations(fallbackData);
        }
      }
    } catch (error) {
      console.error('Error fetching dietary recommendations:', error);
      setDietaryError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
      
      // Provide fallback sample data to prevent crashes
      console.log('Setting fallback dietary data');
      const fallbackData: AIRecommendation[] = [
        {
          menu_item_id: 11,
          name: 'Salad',
          description: 'Fresh mixed salad with lemon dressing',
          price: 35,
          category: 'Side Dish',
          image_url: buildImageUrl('/static/images/salad.jpg'),
          score: 0.92,
          confidence: 0.90,
          reasoning: 'Low calorie (60 cal) and fresh - perfect for dietary preferences',
          recommendation_type: 'dietary'
        },
        {
          menu_item_id: 12,
          name: 'Veg Soup',
          description: 'Healthy mixed vegetable soup',
          price: 45,
          category: 'Starter',
          image_url: buildImageUrl('/static/images/soup.jpg'),
          score: 0.88,
          confidence: 0.85,
          reasoning: 'Nutritious and light (90 cal) - excellent for health-conscious choices',
          recommendation_type: 'dietary'
        },
        {
          menu_item_id: 10,
          name: 'Raita',
          description: 'Fresh yogurt mixed with grated cucumber and spices',
          price: 25,
          category: 'Side Dish',
          image_url: buildImageUrl('/static/images/raita.jpg'),
          score: 0.85,
          confidence: 0.82,
          reasoning: 'Probiotic-rich and cooling (80 cal) - great for digestion',
          recommendation_type: 'dietary'
        }
      ];
      setDietaryRecommendations(fallbackData);
      console.log('Fallback dietary data set:', fallbackData);
    } finally {
      setIsLoadingDietary(false);
    }
  };

  const fetchCalorieConsciousRecommendations = async (limit: number = 5, dailyGoal: number = 2000) => {
    setIsLoadingCalorie(true);
    setCalorieError(null);
    
    try {
      const response = await fetch(
        buildApiUrl(`/api/ai/recommendations/calorie-conscious?limit=${limit}&daily_calorie_goal=${dailyGoal}`),
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AIRecommendationResponse = await response.json();
      setCalorieConsciousRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error fetching calorie-conscious recommendations:', error);
      setCalorieError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
    } finally {
      setIsLoadingCalorie(false);
    }
  };

  const fetchWeatherBasedRecommendations = async (limit: number = 5) => {
    setIsLoadingWeather(true);
    setWeatherError(null);
    
    try {
      const response = await fetch(
        buildApiUrl(`/api/ai/recommendations/weather-based?limit=${limit}`),
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AIRecommendationResponse = await response.json();
      setWeatherBasedRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error fetching weather-based recommendations:', error);
      setWeatherError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
    } finally {
      setIsLoadingWeather(false);
    }
  };

  const fetchAllRecommendations = async (
    preferenceLimit: number = 3, 
    timeLimit: number = 3, 
    dietaryLimit: number = 3, 
    calorieLimit: number = 3, 
    dailyGoal: number = 2000, 
    weatherLimit: number = 3
  ) => {
    setIsLoadingAll(true);
    setAllError(null);
    
    try {
      const response = await fetch(
        buildApiUrl(`/api/ai/recommendations/all?preference_limit=${preferenceLimit}&time_limit=${timeLimit}&dietary_limit=${dietaryLimit}&calorie_limit=${calorieLimit}&daily_calorie_goal=${dailyGoal}`),
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: AIRecommendationResponse = await response.json();
      setAllRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error fetching all recommendations:', error);
      setAllError(error instanceof Error ? error.message : 'Failed to fetch recommendations');
    } finally {
      setIsLoadingAll(false);
    }
  };

  const saveInteraction = async (interaction: UserInteraction) => {
    try {
      const response = await fetch(
        buildApiUrl('/api/ai/interactions'),
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(interaction)
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error saving interaction:', error);
      throw error;
    }
  };

  const fetchUserPreferences = async () => {
    try {
      const response = await fetch(
        buildApiUrl('/api/ai/preferences'),
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setUserPreferences(data);
    } catch (error) {
      console.error('Error fetching user preferences:', error);
    }
  };

  const updateUserPreference = async (type: string, value: string, weight: number = 1.0) => {
    try {
      const response = await fetch(
        buildApiUrl(`/api/ai/preferences?preference_type=${type}&preference_value=${value}&weight=${weight}`),
        {
          method: 'POST',
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh preferences after update
      await fetchUserPreferences();
      return await response.json();
    } catch (error) {
      console.error('Error updating user preference:', error);
      throw error;
    }
  };

  // Auto-fetch recommendations on mount
  useEffect(() => {
    fetchAllRecommendations();
    fetchUserPreferences();
  }, []);

  const value: AIRecommendationContextType = {
    // Recommendations
    preferenceRecommendations,
    timeBasedRecommendations,
    dietaryRecommendations,
    calorieConsciousRecommendations,
    weatherBasedRecommendations,
    allRecommendations,
    
    // Loading states
    isLoadingPreferences,
    isLoadingTimeBased,
    isLoadingDietary,
    isLoadingCalorie,
    isLoadingWeather,
    isLoadingAll,
    
    // Error states
    preferencesError,
    timeBasedError,
    dietaryError,
    calorieError,
    weatherError,
    allError,
    
    // Actions
    fetchPreferenceRecommendations,
    fetchTimeBasedRecommendations,
    fetchDietaryRecommendations,
    fetchCalorieConsciousRecommendations,
    fetchWeatherBasedRecommendations,
    fetchAllRecommendations,
    saveInteraction,
    
    // User preferences
    userPreferences,
    fetchUserPreferences,
    updateUserPreference,
  };

  return (
    <AIRecommendationContext.Provider value={value}>
      {children}
    </AIRecommendationContext.Provider>
  );
}

export function useAIRecommendations() {
  const context = useContext(AIRecommendationContext);
  if (context === undefined) {
    throw new Error('useAIRecommendations must be used within an AIRecommendationProvider');
  }
  return context;
}
