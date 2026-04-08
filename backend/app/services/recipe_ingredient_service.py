from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.menu import MenuItem
from app.models.predictive_analytics import DemandForecast
from .predictive_analytics_service import PredictiveAnalyticsService

# In-memory recipe/ingredient mapping for demonstration.
# In production, replace this with a proper Recipe/Ingredient model and database tables.
# Structure: menu_item_id -> { ingredient_name: { quantity_per_portion: float, unit: str } }
RECIPE_INGREDIENT_MAP: Dict[int, Dict[str, Dict[str, Any]]] = {
    # Example: Biryani (id=1) -> Rice: 150g, Chicken: 100g, Yogurt: 30ml
    1: {
        "Rice": {"quantity_per_portion": 150, "unit": "g"},
        "Chicken": {"quantity_per_portion": 100, "unit": "g"},
        "Yogurt": {"quantity_per_portion": 30, "unit": "ml"},
        "Onion": {"quantity_per_portion": 40, "unit": "g"},
    },
    # Example: Samosa (id=2) -> Potatoes: 80g, Flour: 50g, Peas: 30g
    2: {
        "Potato": {"quantity_per_portion": 80, "unit": "g"},
        "Flour": {"quantity_per_portion": 50, "unit": "g"},
        "Peas": {"quantity_per_portion": 30, "unit": "g"},
        "Oil": {"quantity_per_portion": 15, "unit": "ml"},
    },
    # Add more mappings as needed for your menu items
}

class RecipeIngredientService:
    @staticmethod
    def get_recipe_for_item(menu_item_id: int) -> Dict[str, Dict[str, Any]] | None:
        """
        Get recipe/ingredient mapping for a menu item.
        Returns None if no mapping exists.
        """
        return RECIPE_INGREDIENT_MAP.get(menu_item_id)

    @staticmethod
    def has_recipe_mapping(menu_item_id: int) -> bool:
        """Check if an item has a recipe/ingredient mapping."""
        return menu_item_id in RECIPE_INGREDIENT_MAP

    @staticmethod
    def convert_demand_to_ingredients(
        db: Session,
        demand_forecasts: List[DemandForecast],
        days: int = 7,
        safety_buffer_percent: float = 0.15
    ) -> Dict[str, Any]:
        """
        Convert item demand forecasts into ingredient quantities.
        Falls back to category trends or yesterday's prep with safety buffer when item data is insufficient.
        Returns ingredient-level forecasts with confidence, fallback flags, and ranges.
        """
        try:
            now = datetime.now()
            start_date = now.date()
            end_date = start_date + timedelta(days=days)

            # Bucket ingredient demand by date and ingredient
            ingredient_buckets: Dict[str, Dict[str, Any]] = {}

            # Helper to add ingredient demand
            def add_ingredient_demand(date: str, ingredient: str, quantity: float, unit: str, confidence: float, used_fallback: bool, reasons: List[str]):
                key = (date, ingredient)
                if key not in ingredient_buckets:
                    ingredient_buckets[key] = {
                        "date": date,
                        "ingredient": ingredient,
                        "total_quantity": 0.0,
                        "unit": unit,
                        "confidence_sum": 0.0,
                        "count": 0,
                        "used_fallback": False,
                        "reasons_set": set(),
                    }
                bucket = ingredient_buckets[key]
                bucket["total_quantity"] += quantity
                bucket["confidence_sum"] += confidence
                bucket["count"] += 1
                if used_fallback:
                    bucket["used_fallback"] = True
                bucket["reasons_set"].update(reasons)

            # Process each demand forecast
            for f in demand_forecasts:
                menu_item = db.query(MenuItem).filter(MenuItem.id == f.menu_item_id).first()
                if not menu_item:
                    continue

                recipe = RecipeIngredientService.get_recipe_for_item(f.menu_item_id)
                if not recipe:
                    # No recipe mapping: skip this item for ingredient forecasting
                    continue

                # Extract confidence metadata
                factors = f.factors or {}
                hist_points = int(factors.get("historical_data_points", 0) or 0)
                used_fallback = bool(factors.get("used_fallback", False))
                state = PredictiveAnalyticsService._prediction_state(f.confidence_score, hist_points)
                reasons = PredictiveAnalyticsService._confidence_reasons(menu_item, hist_points, used_fallback)

                # Calculate ingredient quantities
                for ingredient, spec in recipe.items():
                    qty_per_portion = spec["quantity_per_portion"]
                    unit = spec["unit"]
                    total_qty = f.predicted_quantity * qty_per_portion

                    # Apply safety buffer for low-confidence or fallback predictions
                    effective_confidence = f.confidence_score
                    if state != "Reliable" or used_fallback:
                        total_qty *= (1 + safety_buffer_percent)
                        effective_confidence = min(effective_confidence, 0.55)  # Cap confidence for safety-buffered forecasts

                    add_ingredient_demand(
                        date=f.forecast_date.strftime("%Y-%m-%d"),
                        ingredient=ingredient,
                        quantity=total_qty,
                        unit=unit,
                        confidence=effective_confidence,
                        used_fallback=used_fallback,
                        reasons=reasons
                    )

            # Build final ingredient forecast list
            ingredient_forecasts = []
            for (date, ingredient), bucket in ingredient_buckets.items():
                avg_confidence = (bucket["confidence_sum"] / bucket["count"]) if bucket["count"] else 0
                total_qty = bucket["total_quantity"]
                state = PredictiveAnalyticsService._prediction_state(avg_confidence, bucket["count"])
                reasons_list = sorted(list(bucket["reasons_set"]))
                qty_range = PredictiveAnalyticsService._range_for_value(total_qty, avg_confidence)

                ingredient_forecasts.append({
                    "ingredient": ingredient,
                    "date": date,
                    "predicted_quantity": round(total_qty, 2),
                    "unit": bucket["unit"],
                    "confidence": avg_confidence,
                    "prediction_state": state,
                    "reasons": reasons_list,
                    "used_fallback": bucket["used_fallback"],
                    "predicted_quantity_range": {
                        "low": round(qty_range["low"], 2),
                        "high": round(qty_range["high"], 2),
                    },
                    "procurement_suggested": state == "Reliable" and not bucket["used_fallback"],
                    "notes": (
                        "Safety buffer applied due to low confidence or fallback" if state != "Reliable" or bucket["used_fallback"]
                        else "Reliable forecast"
                    ),
                })

            # Sort by date and ingredient
            ingredient_forecasts.sort(key=lambda x: (x["date"], x["ingredient"]))

            return {
                "ingredient_forecasts": ingredient_forecasts,
                "forecast_period": f"{days} days",
                "safety_buffer_percent": safety_buffer_percent,
                "generated_at": datetime.now().isoformat(),
                "items_without_mapping": [
                    f.menu_item_id for f in demand_forecasts if not RecipeIngredientService.has_recipe_mapping(f.menu_item_id)
                ],
            }

        except Exception as e:
            print(f"Error in convert_demand_to_ingredients: {e}")
            return {"error": str(e)}
