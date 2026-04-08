import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';


interface FavoriteItem {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
  type: 'menu_item' | 'combo';
  addedAt: Date;
}

interface FavoritesContextType {
  favorites: FavoriteItem[];
  isFavorite: (itemId: string) => boolean;
  addToFavorites: (item: Omit<FavoriteItem, 'addedAt'>) => void;
  removeFromFavorites: (itemId: string) => void;
  toggleFavorite: (item: Omit<FavoriteItem, 'addedAt'>) => void;
  loading: boolean;
  error: string | null;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export function useFavorites() {
  const context = useContext(FavoritesContext);
  if (context === undefined) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return context;
}

interface FavoritesProviderProps {
  children: ReactNode;
}

export function FavoritesProvider({ children }: FavoritesProviderProps) {
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  // Get current user from localStorage or auth context
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  // Fetch favorites from API
  const fetchFavorites = async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const response = await fetch(`${API_URL}/api/favorites`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setFavorites(data.map((fav: any) => ({
        ...fav,
        addedAt: new Date(fav.added_at)
      })));
    } catch (err) {
      console.error('Error fetching favorites:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch favorites');
      
      // Fallback to localStorage for demo
      const localFavorites = localStorage.getItem(`favorites_${user?.id || 'guest'}`);
      if (localFavorites) {
        setFavorites(JSON.parse(localFavorites));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, [user]);

  // Save favorites to API
  const saveFavorites = async (updatedFavorites: FavoriteItem[]) => {
    if (!user) {
      // Fallback to localStorage for demo
      localStorage.setItem(`favorites_${user?.id || 'guest'}`, JSON.stringify(updatedFavorites));
      return;
    }

    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const response = await fetch(`${API_URL}/api/favorites`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          favorites: updatedFavorites.map(fav => ({
            ...fav,
            added_at: fav.addedAt.toISOString()
          }))
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (err) {
      console.error('Error saving favorites:', err);
      // Fallback to localStorage
      localStorage.setItem(`favorites_${user?.id || 'guest'}`, JSON.stringify(updatedFavorites));
    }
  };

  const isFavorite = (itemId: string) => {
    return favorites.some(fav => fav.id === itemId);
  };

  const addToFavorites = (item: Omit<FavoriteItem, 'addedAt'>) => {
    const favoriteItem: FavoriteItem = {
      ...item,
      addedAt: new Date()
    };

    const updatedFavorites = [...favorites, favoriteItem];
    setFavorites(updatedFavorites);
    saveFavorites(updatedFavorites);
  };

  const removeFromFavorites = (itemId: string) => {
    const updatedFavorites = favorites.filter(fav => fav.id !== itemId);
    setFavorites(updatedFavorites);
    saveFavorites(updatedFavorites);
  };

  const toggleFavorite = (item: Omit<FavoriteItem, 'addedAt'>) => {
    if (isFavorite(item.id)) {
      removeFromFavorites(item.id);
    } else {
      addToFavorites(item);
    }
  };

  const value: FavoritesContextType = {
    favorites,
    isFavorite,
    addToFavorites,
    removeFromFavorites,
    toggleFavorite,
    loading,
    error,
  };

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  );
}
