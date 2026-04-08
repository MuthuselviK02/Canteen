/**
 * Canonical Food Categories - Frontend Types and Utilities
 * 
 * This file provides TypeScript types and utilities for the canonical
 * category system. It mirrors the backend category definitions.
 */

export interface Category {
  key: string;
  label: string;
}

export type CategoryKey = 
  | 'main_course'
  | 'starter' 
  | 'snacks'
  | 'beverages'
  | 'dessert'
  | 'bread'
  | 'rice'
  | 'side_dish';

// API endpoints for categories
export const CATEGORIES_API = {
  BASE: '/api/menu/categories',
  ALL: '/api/menu/categories/',
  KEYS: '/api/menu/categories/keys',
  LABELS: '/api/menu/categories/labels',
  VALIDATE: (key: string) => `/api/menu/categories/validate/${key}`,
  LABEL_FOR_KEY: (key: string) => `/api/menu/categories/label/${key}`,
  KEY_FOR_LABEL: (label: string) => `/api/menu/categories/key/${label}`,
};

// Utility functions
export const getCategoryLabel = (categories: Category[], key: string): string => {
  const category = categories.find(cat => cat.key === key);
  return category?.label || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const getCategoryKey = (categories: Category[], label: string): string => {
  const category = categories.find(cat => cat.label.toLowerCase() === label.toLowerCase());
  return category?.key || label.toLowerCase().replace(/\s+/g, '_');
};

export const isValidCategory = (categories: Category[], key: string): boolean => {
  return categories.some(cat => cat.key === key);
};

export const formatCategoryForDisplay = (key: string): string => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Sample fallback categories (used when API is unavailable)
export const FALLBACK_CATEGORIES: Category[] = [
  { key: 'main_course', label: 'Main Course' },
  { key: 'starter', label: 'Starter' },
  { key: 'snacks', label: 'Snacks' },
  { key: 'beverages', label: 'Beverages' },
  { key: 'dessert', label: 'Dessert' },
  { key: 'bread', label: 'Bread' },
  { key: 'rice', label: 'Rice' },
  { key: 'side_dish', label: 'Side Dish' },
];
