"""
Categories API endpoints

Provides the canonical category list for all frontend components.
This ensures single source of truth for food categories.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict
from app.core.categories import get_all_categories, get_category_label, get_category_key

router = APIRouter(prefix="/api/menu/categories", tags=["Categories"])

@router.get("/", response_model=List[Dict[str, str]])
def get_categories():
    """
    Get all canonical food categories.
    
    Returns:
        List of categories with 'key' and 'label' for each category.
        Frontend components should use this endpoint to populate category dropdowns
        and filter options to ensure consistency across the application.
    """
    return get_all_categories()

@router.get("/keys", response_model=List[str])
def get_category_keys_only():
    """
    Get all category keys only.
    
    Returns:
        List of category keys (e.g., 'main_course', 'starter', etc.)
        Useful for backend operations and validation.
    """
    from app.core.categories import get_category_keys
    return get_category_keys()

@router.get("/labels", response_model=List[str])
def get_category_labels_only():
    """
    Get all category labels only.
    
    Returns:
        List of category labels (e.g., 'Main Course', 'Starter', etc.)
        Useful for UI display purposes.
    """
    from app.core.categories import get_category_labels
    return get_category_labels()

@router.get("/validate/{category_key}")
def validate_category(category_key: str):
    """
    Validate if a category key is valid.
    
    Args:
        category_key: The category key to validate
        
    Returns:
        Boolean indicating if the category is valid
    """
    from app.core.categories import is_valid_category
    return {"is_valid": is_valid_category(category_key)}

@router.get("/label/{category_key}")
def get_label_for_key(category_key: str):
    """
    Get display label for a category key.
    
    Args:
        category_key: The category key
        
    Returns:
        Display label for the category
    """
    return {"label": get_category_label(category_key)}

@router.get("/key/{label}")
def get_key_for_label(label: str):
    """
    Get category key for a display label.
    
    Args:
        label: The display label
        
    Returns:
        Category key for the label
    """
    return {"key": get_category_key(label)}
