import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';

export type UserRole = 'USER' | 'STAFF' | 'ADMIN' | 'SUPER_ADMIN';

export interface User {
  id: number;
  email: string;
  fullname: string;
  role: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullname: string, email: string, password: string) => Promise<any>;
  logout: () => void;
  isAdmin: boolean;
  isSuperAdmin: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);


export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = async (email: string, password: string) => {
    console.log('Attempting login for:', email);
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    console.log('Login response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.log('Login error:', error);
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    console.log('Login successful, token received');
    localStorage.setItem('canteen_token', data.access_token);
    await fetchCurrentUser();
  };

  const register = async (fullname: string, email: string, password: string) => {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fullname, email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const userData = await response.json();
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('canteen_token');
    localStorage.removeItem('canteen_user');
    setUser(null);
  };

  const fetchCurrentUser = async () => {
    const token = localStorage.getItem('canteen_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
      console.log('Fetching current user from:', `${API_URL}/api/auth/me`);
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const userData = await response.json();
        console.log('User data received:', userData);
        setUser(userData);
      } else if (response.status === 401) {
        console.log('Unauthorized, logging out');
        logout();
      } else {
        console.log('Error response:', response.status);
        logout();
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Error fetching user:', error);
      }
      console.log('Fetch error, logging out');
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const isAdmin = user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN';
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        register,
        logout,
        isAdmin,
        isSuperAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
