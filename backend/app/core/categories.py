"""
Canonical Food Categories - Single Source of Truth

This file defines the official food categories for the Smart Canteen system.
All components must use these categories to ensure consistency.
"""

from typing import List, Dict
from enum import Enum

class CategoryKey(str, Enum):
    """Canonical category keys - use these for storage and logic"""
    MAIN_COURSE = "main_course"
    STARTER = "starter"
    SNACKS = "snacks"
    BEVERAGES = "beverages"
    DESSERT = "dessert"
    BREAD = "bread"
    RICE = "rice"
    SIDE_DISH = "side_dish"

# Canonical category definitions with display labels
CANONICAL_CATEGORIES: List[Dict[str, str]] = [
    {"key": CategoryKey.MAIN_COURSE, "label": "Main Course"},
    {"key": CategoryKey.STARTER, "label": "Starter"},
    {"key": CategoryKey.SNACKS, "label": "Snacks"},
    {"key": CategoryKey.BEVERAGES, "label": "Beverages"},
    {"key": CategoryKey.DESSERT, "label": "Dessert"},
    {"key": CategoryKey.BREAD, "label": "Bread"},
    {"key": CategoryKey.RICE, "label": "Rice"},
    {"key": CategoryKey.SIDE_DISH, "label": "Side Dish"},
]

# Helper functions for category management
def get_all_categories() -> List[Dict[str, str]]:
    """Returns all canonical categories"""
    return CANONICAL_CATEGORIES

def get_category_label(category_key: str) -> str:
    """Get display label for a category key"""
    for cat in CANONICAL_CATEGORIES:
        if cat["key"] == category_key:
            return cat["label"]
    return category_key.replace("_", " ").title()

def get_category_key(label: str) -> str:
    """Get category key from display label (case-insensitive)"""
    label_lower = label.lower()
    for cat in CANONICAL_CATEGORIES:
        if cat["label"].lower() == label_lower:
            return cat["key"]
    return label.lower().replace(" ", "_")

def is_valid_category(category_key: str) -> bool:
    """Check if category key is valid"""
    return category_key in [cat["key"] for cat in CANONICAL_CATEGORIES]

def get_category_keys() -> List[str]:
    """Get all category keys"""
    return [cat["key"] for cat in CANONICAL_CATEGORIES]

def get_category_labels() -> List[str]:
    """Get all category labels"""
    return [cat["label"] for cat in CANONICAL_CATEGORIES]

# Legacy category mapping for migration
LEGACY_CATEGORY_MAPPING = {
    "Main Course": CategoryKey.MAIN_COURSE,
    "Starter": CategoryKey.STARTER,
    "Snacks": CategoryKey.SNACKS,
    "Beverages": CategoryKey.BEVERAGES,
    "Beverage": CategoryKey.BEVERAGES,  # Handle singular form
    "Dessert": CategoryKey.DESSERT,
    "Desserts": CategoryKey.DESSERT,  # Handle plural form
    "Bread": CategoryKey.BREAD,
    "Rice": CategoryKey.RICE,
    "Side Dish": CategoryKey.SIDE_DISH,
    "Salad": CategoryKey.SIDE_DISH,  # Map Salad to Side Dish
    "Dietary": CategoryKey.SNACKS,  # Map Dietary to Snacks
    "Breakfast": CategoryKey.STARTER,  # Map Breakfast to Starter
    "Soup": CategoryKey.STARTER,  # Map Soup to Starter
}

def migrate_legacy_category(legacy_category: str) -> str:
    """Migrate legacy category name to canonical key"""
    if not legacy_category:
        return CategoryKey.MAIN_COURSE  # Default fallback
    
    # Direct mapping first
    if legacy_category in LEGACY_CATEGORY_MAPPING:
        return LEGACY_CATEGORY_MAPPING[legacy_category]
    
    # Try case-insensitive matching
    legacy_lower = legacy_category.lower()
    for legacy, canonical in LEGACY_CATEGORY_MAPPING.items():
        if legacy.lower() == legacy_lower:
            return canonical
    
    # Try to match with canonical labels
    return get_category_key(legacy_category)
