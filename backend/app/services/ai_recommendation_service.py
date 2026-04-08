from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import math
from collections import defaultdict
import random

from app.models.user import User
from app.models.menu import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.ai_recommendations import UserPreference, UserInteraction, AIRecommendation

class AIRecommendationService:
    """
    Production-level AI recommendation service for smart ordering
    """
    
    @staticmethod
    def get_user_preferences(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user preferences for AI recommendations
        """
        try:
            # Get user's explicit preferences
            preferences = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).all()
            
            # Get user's order history for implicit preferences
            order_history = db.query(OrderItem, MenuItem).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.user_id == user_id,
                Order.status == 'completed'
            ).all()
            
            # Get user interactions
            interactions = db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id
            ).order_by(desc(UserInteraction.created_at)).limit(50).all()
            
            # Analyze preferences
            category_preferences = defaultdict(float)
            spice_preferences = defaultdict(float)
            dietary_preferences = defaultdict(float)
            
            # Process order history
            for order_item, menu_item in order_history:
                category = menu_item.category or 'general'
                category_preferences[category] += 1
                
                # Extract dietary info from description
                desc = (menu_item.description or '').lower()
                if 'vegetarian' in desc or 'veg' in desc:
                    dietary_preferences['vegetarian'] += 1
                elif 'non-vegetarian' in desc or 'non-veg' in desc:
                    dietary_preferences['non-vegetarian'] += 1
                    
                # Extract spice level
                if 'spicy' in desc or 'hot' in desc:
                    spice_preferences['spicy'] += 1
                elif 'mild' in desc:
                    spice_preferences['mild'] += 1
            
            # Process explicit preferences
            for pref in preferences:
                if pref.preference_type == 'category':
                    category_preferences[pref.preference_value] += pref.weight * 5
                elif pref.preference_type == 'spice_level':
                    spice_preferences[pref.preference_value] += pref.weight * 5
                elif pref.preference_type == 'dietary':
                    dietary_preferences[pref.preference_value] += pref.weight * 5
            
            # Normalize preferences
            total_orders = len(order_history)
            if total_orders > 0:
                for key in category_preferences:
                    category_preferences[key] /= total_orders
                for key in spice_preferences:
                    spice_preferences[key] /= total_orders
                for key in dietary_preferences:
                    dietary_preferences[key] /= total_orders
            
            return {
                'category_preferences': dict(category_preferences),
                'spice_preferences': dict(spice_preferences),
                'dietary_preferences': dict(dietary_preferences),
                'total_orders': total_orders,
                'explicit_preferences': len(preferences),
                'interaction_count': len(interactions)
            }
            
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            return AIRecommendationService.get_fallback_preferences()
    
    @staticmethod
    def get_preference_based_recommendations(
        db: Session, 
        user_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Step 1: AI-powered menu recommendations based on user preferences
        """
        try:
            preferences = AIRecommendationService.get_user_preferences(db, user_id)
            
            # Get all available menu items
            menu_items = db.query(MenuItem).filter(
                MenuItem.is_available == True
            ).all()
            
            recommendations = []
            
            for item in menu_items:
                score = 0.0
                reasoning = []
                
                # Category preference scoring
                category = item.category or 'general'
                if category in preferences['category_preferences']:
                    category_score = preferences['category_preferences'][category]
                    score += category_score * 0.4
                    reasoning.append(f"Category preference: {category} ({category_score:.2f})")
                
                # Dietary preference scoring
                desc = (item.description or '').lower()
                dietary_score = 0.0
                
                if 'vegetarian' in desc or 'veg' in desc:
                    if 'vegetarian' in preferences['dietary_preferences']:
                        dietary_score = preferences['dietary_preferences']['vegetarian']
                        score += dietary_score * 0.3
                        reasoning.append(f"Vegetarian preference ({dietary_score:.2f})")
                elif 'non-vegetarian' in desc or 'non-veg' in desc:
                    if 'non-vegetarian' in preferences['dietary_preferences']:
                        dietary_score = preferences['dietary_preferences']['non-vegetarian']
                        score += dietary_score * 0.3
                        reasoning.append(f"Non-vegetarian preference ({dietary_score:.2f})")
                
                # Spice preference scoring
                if 'spicy' in desc or 'hot' in desc:
                    if 'spicy' in preferences['spice_preferences']:
                        spice_score = preferences['spice_preferences']['spicy']
                        score += spice_score * 0.2
                        reasoning.append(f"Spicy preference ({spice_score:.2f})")
                elif 'mild' in desc:
                    if 'mild' in preferences['spice_preferences']:
                        spice_score = preferences['spice_preferences']['mild']
                        score += spice_score * 0.2
                        reasoning.append(f"Mild preference ({spice_score:.2f})")
                
                # Price preference (based on user's average order value)
                if preferences['total_orders'] > 0:
                    avg_price = db.query(func.avg(MenuItem.price)).join(
                        OrderItem, MenuItem.id == OrderItem.menu_item_id
                    ).join(Order, OrderItem.order_id == Order.id).filter(
                        Order.user_id == user_id
                    ).scalar() or 0
                    
                    if avg_price > 0:
                        price_diff = abs(item.price - avg_price) / avg_price
                        price_score = max(0, 1 - price_diff)
                        score += price_score * 0.1
                        reasoning.append(f"Price preference ({price_score:.2f})")
                
                # Only include items with meaningful scores
                if score > 0.1:
                    recommendations.append({
                        'menu_item_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': item.price,
                        'category': item.category,
                        'image_url': item.image_url,
                        'score': score,
                        'confidence': min(score, 1.0),
                        'reasoning': '; '.join(reasoning),
                        'recommendation_type': 'preference_based'
                    })
            
            # Sort by score and limit results
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in preference-based recommendations: {e}")
            return AIRecommendationService.get_fallback_recommendations(db, limit)
    
    @staticmethod
    def get_time_based_recommendations(
        db: Session, 
        user_id: int, 
        current_time: Optional[datetime] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Step 2: Intelligent meal suggestions based on time of day
        """
        try:
            if current_time is None:
                current_time = datetime.utcnow()
            
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # Define time-based meal patterns
            time_patterns = {
                'breakfast': (6, 10),      # 6 AM - 10 AM
                'lunch': (11, 14),         # 11 AM - 2 PM
                'snack': (15, 17),         # 3 PM - 5 PM
                'dinner': (18, 22),        # 6 PM - 10 PM
                'late_night': (23, 5)      # 11 PM - 5 AM
            }
            
            # Determine current meal type
            current_meal = 'lunch'  # default
            for meal, (start, end) in time_patterns.items():
                if meal == 'late_night':
                    if hour >= start or hour <= end:
                        current_meal = meal
                        break
                else:
                    if start <= hour <= end:
                        current_meal = meal
                        break
            
            # Get user's historical preferences for this time
            historical_orders = db.query(OrderItem, MenuItem).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.user_id == user_id,
                Order.status == 'completed',
                func.extract('hour', Order.created_at).between(
                    max(0, hour - 1), min(23, hour + 1)
                )
            ).all()
            
            # Analyze historical patterns
            meal_preferences = defaultdict(int)
            for order_item, menu_item in historical_orders:
                category = menu_item.category or 'general'
                meal_preferences[category] += 1
            
            # Get available menu items suitable for current meal
            menu_items = db.query(MenuItem).filter(
                MenuItem.is_available == True
            ).all()
            
            recommendations = []
            
            # Meal-specific logic
            meal_keywords = {
                'breakfast': ['breakfast', 'morning', 'coffee', 'tea', 'bread', 'egg', 'cereal'],
                'lunch': ['lunch', 'rice', 'curry', 'meal', 'thali', 'biryani'],
                'snack': ['snack', 'chaat', 'samosa', 'tea', 'coffee', 'juice'],
                'dinner': ['dinner', 'rice', 'curry', 'meal', 'soup', 'salad'],
                'late_night': ['light', 'soup', 'salad', 'sandwich']
            }
            
            for item in menu_items:
                score = 0.0
                reasoning = [f"Time-based: {current_meal}"]
                
                # Check if item matches current meal keywords
                desc = (item.description or '').lower() + ' ' + (item.name or '').lower()
                keyword_match = False
                
                for keyword in meal_keywords.get(current_meal, []):
                    if keyword in desc:
                        score += 0.5
                        reasoning.append(f"Matches {current_meal} keyword: {keyword}")
                        keyword_match = True
                        break
                
                # Check historical preferences for this time
                category = item.category or 'general'
                if category in meal_preferences and len(historical_orders) > 0:
                    historical_score = meal_preferences[category] / len(historical_orders)
                    score += historical_score * 0.3
                    reasoning.append(f"Historical preference for {category}")
                
                # Weekend vs weekday adjustments
                if day_of_week >= 5:  # Weekend
                    if 'special' in desc or 'deluxe' in desc:
                        score += 0.2
                        reasoning.append("Weekend special item")
                else:  # Weekday
                    if 'quick' in desc or 'express' in desc:
                        score += 0.2
                        reasoning.append("Quick weekday option")
                
                # Only include items with meaningful scores
                if score > 0.2:
                    recommendations.append({
                        'menu_item_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': item.price,
                        'category': item.category,
                        'image_url': item.image_url,
                        'score': score,
                        'confidence': min(score, 1.0),
                        'reasoning': '; '.join(reasoning),
                        'recommendation_type': 'time_based',
                        'meal_type': current_meal
                    })
            
            # Sort by score and limit results
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in time-based recommendations: {e}")
            return AIRecommendationService.get_fallback_recommendations(db, limit)
    
    @staticmethod
    def save_user_interaction(
        db: Session, 
        user_id: int, 
        menu_item_id: int, 
        interaction_type: str,
        interaction_value: Optional[float] = None,
        context_data: Optional[Dict[str, Any]] = None
    ):
        """
        Save user interaction for learning
        """
        try:
            interaction = UserInteraction(
                user_id=user_id,
                menu_item_id=menu_item_id,
                interaction_type=interaction_type,
                interaction_value=interaction_value,
                context_data=context_data or {}
            )
            db.add(interaction)
            db.commit()
        except Exception as e:
            print(f"Error saving user interaction: {e}")
            db.rollback()
    
    @staticmethod
    def get_combo_recommendations(
        db: Session, 
        user_id: int, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Step 3: Personalized combo suggestions using order history
        """
        try:
            # Get user's complete order history
            order_history = db.query(Order).filter(
                Order.user_id == user_id,
                Order.status == 'completed'
            ).all()
            
            if len(order_history) < 2:
                return []  # Not enough history for combo analysis
            
            # Analyze item combinations in orders
            combo_patterns = defaultdict(int)
            item_frequency = defaultdict(int)
            
            for order in order_history:
                # Get all items in this order
                order_items = db.query(OrderItem).filter(
                    OrderItem.order_id == order.id
                ).all()
                
                item_ids = [oi.menu_item_id for oi in order_items]
                
                # Update item frequency
                for item_id in item_ids:
                    item_frequency[item_id] += 1
                
                # Generate combinations (pairs and triplets)
                if len(item_ids) >= 2:
                    # Pairs
                    for i in range(len(item_ids)):
                        for j in range(i + 1, len(item_ids)):
                            pair = tuple(sorted([item_ids[i], item_ids[j]]))
                            combo_patterns[pair] += 1
                
                if len(item_ids) >= 3:
                    # Triplets
                    for i in range(len(item_ids)):
                        for j in range(i + 1, len(item_ids)):
                            for k in range(j + 1, len(item_ids)):
                                triplet = tuple(sorted([item_ids[i], item_ids[j], item_ids[k]]))
                                combo_patterns[triplet] += 1
            
            # Get most frequent combos
            top_combos = sorted(combo_patterns.items(), key=lambda x: x[1], reverse=True)[:limit * 2]
            
            # Build combo recommendations
            recommendations = []
            
            for combo_items, frequency in top_combos:
                if len(recommendations) >= limit:
                    break
                
                # Get menu item details
                combo_menu_items = []
                total_price = 0
                total_calories = 0
                
                for item_id in combo_items:
                    menu_item = db.query(MenuItem).filter(
                        MenuItem.id == item_id,
                        MenuItem.is_available == True
                    ).first()
                    
                    if menu_item:
                        combo_menu_items.append(menu_item)
                        total_price += menu_item.price
                        if menu_item.calories:
                            total_calories += menu_item.calories
                
                # Skip if any items are unavailable
                if len(combo_menu_items) != len(combo_items):
                    continue
                
                # Calculate combo score
                combo_score = min(frequency / len(order_history), 1.0)
                
                # Generate combo name and reasoning
                combo_name = AIRecommendationService._generate_combo_name(combo_menu_items)
                reasoning = f"Ordered together {frequency} times ({frequency/len(order_history)*100:.1f}% of your orders)"
                
                # Calculate savings (if any)
                individual_total = sum(item.price for item in combo_menu_items)
                discount_suggestion = max(0, (individual_total - total_price) / individual_total * 100)
                
                recommendation = {
                    'combo_id': f"combo_{'_'.join(map(str, combo_items))}",
                    'name': combo_name,
                    'description': f"Perfect combination based on your ordering history",
                    'items': [
                        {
                            'menu_item_id': item.id,
                            'name': item.name,
                            'price': item.price,
                            'category': item.category,
                            'image_url': item.image_url
                        }
                        for item in combo_menu_items
                    ],
                    'total_price': total_price,
                    'individual_total': individual_total,
                    'savings_percentage': discount_suggestion,
                    'total_calories': total_calories,
                    'item_count': len(combo_menu_items),
                    'frequency': frequency,
                    'score': combo_score,
                    'confidence': min(combo_score * 1.2, 1.0),  # Boost confidence for combos
                    'reasoning': reasoning,
                    'recommendation_type': 'combo'
                }
                
                recommendations.append(recommendation)
            
            # Sort by score and return
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in combo recommendations: {e}")
            return []
    
    @staticmethod
    def _generate_combo_name(items: List[MenuItem]) -> str:
        """
        Generate a descriptive name for a combo
        """
        categories = [item.category or 'Item' for item in items]
        
        # Common combo patterns
        if len(items) == 2:
            if 'Beverage' in categories and any(cat in ['Main Course', 'Starter'] for cat in categories):
                return f"Classic Meal Combo"
            elif all(cat in ['Main Course', 'Starter'] for cat in categories):
                return f"Hearty Combo"
            else:
                return f"Perfect Pair"
        
        elif len(items) == 3:
            if 'Beverage' in categories and any(cat in ['Main Course'] for cat in categories):
                return f"Complete Meal Deal"
            elif all(cat in ['Main Course', 'Starter'] for cat in categories):
                return f"Feast Combo"
            else:
                return f"Triple Treat"
        
        else:
            return f"Family Combo"
    
    @staticmethod
    def get_dietary_recommendations(
        db: Session, 
        user_id: int, 
        dietary_restrictions: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Step 4: Dietary preference learning (veg/non-veg, allergies)
        """
        try:
            # Get user's dietary preferences from interactions and orders
            user_orders = db.query(OrderItem, MenuItem).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.user_id == user_id,
                Order.status == 'completed'
            ).all()
            
            # Analyze dietary patterns
            veg_count = 0
            non_veg_count = 0
            spicy_count = 0
            mild_count = 0
            
            for order_item, menu_item in user_orders:
                if menu_item.is_vegetarian:
                    veg_count += 1
                else:
                    non_veg_count += 1
                
                if menu_item.is_spicy:
                    spicy_count += 1
                else:
                    mild_count += 1
            
            total_orders = len(user_orders)
            if total_orders == 0:
                return []
            
            # Determine dietary preference
            veg_preference = veg_count / total_orders
            non_veg_preference = non_veg_count / total_orders
            spicy_preference = spicy_count / total_orders
            
            # Get available menu items matching dietary preferences
            menu_items = db.query(MenuItem).filter(
                MenuItem.is_available == True
            ).all()
            
            recommendations = []
            
            for item in menu_items:
                score = 0.0
                reasoning = []
                
                # Vegetarian preference scoring
                if item.is_vegetarian:
                    score += veg_preference * 0.4
                    if veg_preference > 0.7:
                        reasoning.append("Matches your vegetarian preference")
                else:
                    score += non_veg_preference * 0.4
                    if non_veg_preference > 0.7:
                        reasoning.append("Matches your non-vegetarian preference")
                
                # Spice preference scoring
                if item.is_spicy:
                    score += spicy_preference * 0.3
                    if spicy_preference > 0.6:
                        reasoning.append("Matches your spicy preference")
                else:
                    score += mild_preference * 0.3
                    if mild_preference > 0.6:
                        reasoning.append("Matches your mild preference")
                
                # Check for explicit dietary restrictions
                if dietary_restrictions:
                    desc = (item.description or '').lower()
                    item_name = (item.name or '').lower()
                    
                    # Check for allergens
                    allergens = ['nuts', 'peanuts', 'dairy', 'gluten', 'shellfish']
                    has_allergen = any(allergen in desc or allergen in item_name for allergen in allergens)
                    
                    if has_allergen:
                        score -= 0.5
                        reasoning.append("Contains potential allergens")
                    
                    # Check for dietary requirements
                    if 'vegetarian' in dietary_restrictions and not item.is_vegetarian:
                        score -= 0.8
                        reasoning.append("Not vegetarian")
                    
                    if 'vegan' in dietary_restrictions:
                        # Simple vegan check (can be enhanced)
                        desc_words = desc.split()
                        if any(word in ['milk', 'cheese', 'butter', 'cream', 'dairy'] for word in desc_words):
                            score -= 0.6
                            reasoning.append("Contains dairy")
                
                # Only include items with meaningful scores
                if score > 0.2:
                    recommendations.append({
                        'menu_item_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': item.price,
                        'category': item.category,
                        'image_url': item.image_url,
                        'calories': item.calories,
                        'is_vegetarian': item.is_vegetarian,
                        'is_spicy': item.is_spicy,
                        'score': score,
                        'confidence': min(score, 1.0),
                        'reasoning': '; '.join(reasoning),
                        'recommendation_type': 'dietary',
                        'dietary_tags': AIRecommendationService._get_dietary_tags(item)
                    })
            
            # Sort by score and limit results
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in dietary recommendations: {e}")
            return []
    
    @staticmethod
    def _get_dietary_tags(item: MenuItem) -> List[str]:
        """
        Get dietary tags for a menu item
        """
        tags = []
        
        if item.is_vegetarian:
            tags.append('Vegetarian')
        else:
            tags.append('Non-Vegetarian')
        
        if item.is_spicy:
            tags.append('Spicy')
        else:
            tags.append('Mild')
        
        if item.calories and item.calories < 300:
            tags.append('Low-Calorie')
        elif item.calories and item.calories > 600:
            tags.append('High-Calorie')
        
        return tags
    
    @staticmethod
    def get_calorie_conscious_recommendations(
        db: Session, 
        user_id: int, 
        daily_calorie_goal: int = 2000,
        meal_calorie_targets: Dict[str, int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Step 5: Calorie-conscious meal planning
        """
        try:
            # Default meal targets if not provided
            if meal_calorie_targets is None:
                meal_calorie_targets = {
                    'breakfast': daily_calorie_goal * 0.25,  # 25%
                    'lunch': daily_calorie_goal * 0.35,      # 35%
                    'snack': daily_calorie_goal * 0.10,       # 10%
                    'dinner': daily_calorie_goal * 0.30       # 30%
                }
            
            # Get user's order history to understand calorie patterns
            user_orders = db.query(OrderItem, MenuItem, Order).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.user_id == user_id,
                Order.status == 'completed',
                MenuItem.calories.isnot(None)
            ).all()
            
            # Analyze user's typical calorie consumption
            calorie_patterns = {
                'avg_breakfast': 0,
                'avg_lunch': 0,
                'avg_snack': 0,
                'avg_dinner': 0,
                'total_orders': 0
            }
            
            meal_type_orders = defaultdict(list)
            
            for order_item, menu_item, order in user_orders:
                hour = order.created_at.hour if order.created_at else 12
                meal_type = AIRecommendationService._determine_meal_type(hour)
                
                if menu_item.calories:
                    meal_type_orders[meal_type].append(menu_item.calories)
                    calorie_patterns[f'avg_{meal_type}'] += menu_item.calories
                    calorie_patterns['total_orders'] += 1
            
            # Calculate averages
            for meal_type in ['breakfast', 'lunch', 'snack', 'dinner']:
                if meal_type_orders[meal_type]:
                    calorie_patterns[f'avg_{meal_type}'] = sum(meal_type_orders[meal_type]) / len(meal_type_orders[meal_type])
            
            # Get current time to determine meal type
            current_hour = datetime.utcnow().hour
            current_meal = AIRecommendationService._determine_meal_type(current_hour)
            target_calories = meal_calorie_targets.get(current_meal, 500)
            
            # Get available menu items with calorie information
            menu_items = db.query(MenuItem).filter(
                MenuItem.is_available == True,
                MenuItem.calories.isnot(None)
            ).all()
            
            recommendations = []
            
            for item in menu_items:
                score = 0.0
                reasoning = []
                
                # Calorie appropriateness for current meal
                calorie_diff = abs(item.calories - target_calories)
                calorie_score = max(0, 1 - (calorie_diff / target_calories))
                score += calorie_score * 0.4
                
                if calorie_score > 0.7:
                    reasoning.append(f"Perfect calorie range for {current_meal}")
                elif calorie_score > 0.5:
                    reasoning.append(f"Good calorie fit for {current_meal}")
                
                # Compare with user's historical preferences
                user_avg = calorie_patterns[f'avg_{current_meal}']
                if user_avg > 0:
                    user_preference_score = max(0, 1 - (abs(item.calories - user_avg) / user_avg))
                    score += user_preference_score * 0.3
                    
                    if user_preference_score > 0.7:
                        reasoning.append("Matches your usual portion size")
                
                # Nutritional balance scoring
                nutrition_score = AIRecommendationService._calculate_nutrition_score(item)
                score += nutrition_score * 0.2
                
                if nutrition_score > 0.7:
                    reasoning.append("Well-balanced nutritional profile")
                
                # Calorie density (calories per rupee)
                if item.price > 0:
                    calorie_density = item.calories / item.price
                    if calorie_density > 2:  # Good value
                        score += 0.1
                        reasoning.append("Good calorie value for money")
                
                # Daily goal consideration
                if daily_calorie_goal > 0:
                    calorie_percentage = (item.calories / daily_calorie_goal) * 100
                    if calorie_percentage <= 15:  # Less than 15% of daily goal
                        score += 0.1
                        reasoning.append("Fits well within daily calorie goal")
                
                # Only include items with meaningful scores
                if score > 0.3:
                    recommendations.append({
                        'menu_item_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': item.price,
                        'category': item.category,
                        'image_url': item.image_url,
                        'calories': item.calories,
                        'calorie_percentage': round((item.calories / daily_calorie_goal) * 100, 1) if daily_calorie_goal > 0 else 0,
                        'calorie_density': round(item.calories / item.price, 1) if item.price > 0 else 0,
                        'score': score,
                        'confidence': min(score, 1.0),
                        'reasoning': '; '.join(reasoning),
                        'recommendation_type': 'calorie_conscious',
                        'meal_type': current_meal,
                        'target_calories': target_calories,
                        'nutrition_score': nutrition_score,
                        'calorie_tags': AIRecommendationService._get_calorie_tags(item, daily_calorie_goal)
                    })
            
            # Sort by score and limit results
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in calorie-conscious recommendations: {e}")
            return []
    
    @staticmethod
    def _determine_meal_type(hour: int) -> str:
        """
        Determine meal type based on hour
        """
        if 6 <= hour <= 10:
            return 'breakfast'
        elif 11 <= hour <= 14:
            return 'lunch'
        elif 15 <= hour <= 17:
            return 'snack'
        elif 18 <= hour <= 22:
            return 'dinner'
        else:
            return 'snack'  # Default to snack for late night
    
    @staticmethod
    def _calculate_nutrition_score(item: MenuItem) -> float:
        """
        Calculate nutrition balance score based on available information
        """
        score = 0.5  # Base score
        
        # Check if calories are reasonable for a meal item
        if item.calories:
            if 200 <= item.calories <= 800:  # Reasonable range
                score += 0.3
            elif item.calories < 200:  # Very light
                score += 0.1
            elif item.calories > 800:  # Very heavy
                score -= 0.1
        
        # Consider vegetarian options as generally healthier
        if item.is_vegetarian:
            score += 0.1
        
        # Consider spice level (mild is often healthier)
        if not item.is_spicy:
            score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def _get_calorie_tags(item: MenuItem, daily_goal: int) -> List[str]:
        """
        Get calorie-related tags for a menu item
        """
        tags = []
        
        if item.calories:
            # Calorie range tags
            if item.calories < 200:
                tags.append('Light')
            elif item.calories <= 400:
                tags.append('Moderate')
            elif item.calories <= 600:
                tags.append('Hearty')
            else:
                tags.append('High-Calorie')
            
            # Daily goal percentage
            if daily_goal > 0:
                percentage = (item.calories / daily_goal) * 100
                if percentage <= 10:
                    tags.append('Low-Impact')
                elif percentage <= 20:
                    tags.append('Moderate-Impact')
                else:
                    tags.append('High-Impact')
        
        return tags
    
    @staticmethod
    def get_weather_based_recommendations(
        db: Session, 
        user_id: int,
        weather_data: Dict[str, Any] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Step 6: Weather-based food recommendations
        """
        try:
            # If no weather data provided, fetch from API (mock for now)
            if weather_data is None:
                weather_data = AIRecommendationService._get_current_weather()
            
            temperature = weather_data.get('temperature', 25)  # Celsius
            humidity = weather_data.get('humidity', 60)  # Percentage
            weather_condition = weather_data.get('condition', 'clear')  # clear, cloudy, rainy, sunny, etc.
            season = AIRecommendationService._get_season()
            
            # Get user's order history to understand weather preferences
            user_orders = db.query(OrderItem, MenuItem, Order).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.user_id == user_id,
                Order.status == 'completed'
            ).all()
            
            # Analyze user's weather-based ordering patterns
            weather_preferences = AIRecommendationService._analyze_weather_preferences(user_orders)
            
            # Get available menu items
            menu_items = db.query(MenuItem).filter(
                MenuItem.is_available == True
            ).all()
            
            recommendations = []
            
            for item in menu_items:
                score = 0.0
                reasoning = []
                
                # Temperature-based recommendations
                temp_score = AIRecommendationService._calculate_temperature_score(item, temperature, weather_preferences)
                score += temp_score * 0.4
                
                if temp_score > 0.7:
                    reasoning.append(f"Perfect for {temperature}°C weather")
                elif temp_score > 0.5:
                    reasoning.append(f"Good match for {temperature}°C")
                
                # Weather condition-based recommendations
                condition_score = AIRecommendationService._calculate_condition_score(item, weather_condition, season)
                score += condition_score * 0.3
                
                if condition_score > 0.7:
                    reasoning.append(f"Ideal for {weather_condition} weather")
                elif condition_score > 0.5:
                    reasoning.append(f"Suitable for {weather_condition} conditions")
                
                # Humidity considerations
                humidity_score = AIRecommendationService._calculate_humidity_score(item, humidity)
                score += humidity_score * 0.2
                
                if humidity_score > 0.7:
                    reasoning.append(f"Comfortable in {humidity}% humidity")
                elif humidity_score < 0.3:
                    reasoning.append(f"May feel heavy in high humidity")
                
                # Seasonal appropriateness
                seasonal_score = AIRecommendationService._calculate_seasonal_score(item, season)
                score += seasonal_score * 0.1
                
                if seasonal_score > 0.7:
                    reasoning.append(f"Perfect {season} choice")
                
                # Weather-based comfort food
                comfort_score = AIRecommendationService._calculate_comfort_score(item, temperature, weather_condition)
                score += comfort_score * 0.2
                
                if comfort_score > 0.7:
                    reasoning.append("Comfort food for current weather")
                
                # Only include items with meaningful scores
                if score > 0.3:
                    recommendations.append({
                        'menu_item_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': item.price,
                        'category': item.category,
                        'image_url': item.image_url,
                        'calories': item.calories,
                        'is_vegetarian': item.is_vegetarian,
                        'is_spicy': item.is_spicy,
                        'score': score,
                        'confidence': min(score, 1.0),
                        'reasoning': '; '.join(reasoning),
                        'recommendation_type': 'weather_based',
                        'weather_data': {
                            'temperature': temperature,
                            'humidity': humidity,
                            'condition': weather_condition,
                            'season': season
                        },
                        'weather_tags': AIRecommendationService._get_weather_tags(item, weather_data),
                    })
            
            # Sort by score and limit results
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in mood-based recommendations: {e}")
            return []
    
    @staticmethod
    def _analyze_current_mood(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Analyze current user mood based on time, day, and patterns
        """
        import datetime
        
        conditions = ['clear', 'cloudy', 'rainy', 'sunny', 'partly_cloudy', 'overcast']
        return {
            'temperature': random.randint(15, 35),
            'humidity': random.randint(30, 80),
            'condition': random.choice(conditions),
            'season': 'summer' if random.randint(1, 12) in [6, 7, 8] else 'winter' if random.randint(1, 12) in [12, 1, 2] else 'monsoon' if random.randint(1, 12) in [3, 4, 5, 9, 10, 11] else 'spring'
        }
    
    @staticmethod
    def _analyze_weather_preferences(user_orders: List) -> Dict[str, float]:
        """
        Analyze user's historical weather-based ordering patterns
        """
        weather_patterns = {
            'hot': 0,
            'cold': 0,
            'rainy': 0,
            'clear': 0,
            'cloudy': 0
        }
        
        # This would normally use actual weather data from order timestamps
        # For now, we'll use a simple pattern based on item characteristics
        for order_item, menu_item, order in user_orders:
            if menu_item.is_spicy:
                weather_patterns['hot'] += 1
            elif menu_item.category in ['Beverage', 'Ice Cream', 'Juice']:
                weather_patterns['hot'] += 1
            elif menu_item.category in ['Soup', 'Hot Beverage']:
                weather_patterns['cold'] += 1
            elif 'soup' in (menu_item.description or '').lower():
                weather_patterns['cold'] += 1
            elif 'hot' in (menu_item.description or '').lower():
                weather_patterns['hot'] += 1
            else:
                weather_patterns['clear'] += 1
        
        total_patterns = sum(weather_patterns.values())
        if total_patterns > 0:
            for key in weather_patterns:
                weather_patterns[key] /= total_patterns
        
        return weather_patterns
    
    @staticmethod
    def _calculate_temperature_score(item: MenuItem, temperature: float, preferences: Dict[str, float]) -> float:
        """
        Calculate temperature appropriateness score for food item
        """
        score = 0.5  # Base score
        
        # Hot weather preferences
        if temperature >= 30:  # Hot weather
            if item.category in ['Beverage', 'Ice Cream', 'Juice', 'Salad', 'Cold Dessert']:
                score += 0.4
            elif item.is_spicy:
                score -= 0.3  # Spicy food might be uncomfortable in hot weather
            elif item.category in ['Hot Soup', 'Hot Beverage']:
                score -= 0.4
        
        # Cold weather preferences
        elif temperature <= 15:  # Cold weather
            if item.category in ['Hot Soup', 'Hot Beverage', 'Starter', 'Main Course']:
                score += 0.4
            elif item.category in ['Ice Cream', 'Cold Dessert', 'Salad']:
                score -= 0.3
            elif item.is_spicy:
                score += 0.2  # Spicy food can be warming in cold weather
        
        # Mild weather
        else:  # 16-29°C
            if item.category in ['Main Course', 'Starter']:
                score += 0.3
            elif item.category in ['Beverage']:
                score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_condition_score(item: MenuItem, condition: str, season: str) -> float:
        """
        Calculate weather condition appropriateness score
        """
        score = 0.5  # Base score
        
        condition_lower = condition.lower()
        
        # Rainy weather recommendations
        if 'rain' in condition_lower:
            if item.category in ['Hot Soup', 'Hot Beverage', 'Comfort Food']:
                score += 0.4
            elif item.category in ['Ice Cream', 'Cold Dessert']:
                score -= 0.3
            elif 'soup' in (item.description or '').lower():
                score += 0.3
        
        # Sunny/hot weather
        elif 'sunny' in condition_lower or 'clear' in condition_lower:
            if item.category in ['Salad', 'Light Meal', 'Beverage', 'Fruit']:
                score += 0.3
            elif item.category in ['Hot Soup', 'Heavy Meal']:
                score -= 0.2
        
        # Cloudy/overcast weather
        elif 'cloudy' in condition_lower or 'overcast' in condition_lower:
            if item.category in ['Comfort Food', 'Main Course']:
                score += 0.2
            elif item.category in ['Ice Cream']:
                score -= 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_humidity_score(item: MenuItem, humidity: float) -> float:
        """
        Calculate humidity appropriateness score
        """
        score = 0.5  # Base score
        
        if humidity >= 70:  # High humidity
            if item.category in ['Light Meal', 'Salad', 'Fruit']:
                score += 0.3
            elif item.category in ['Heavy Meal', 'Fried Food']:
                score -= 0.3
            elif item.is_spicy:
                score -= 0.2
        
        elif humidity <= 40:  # Low humidity
            if item.category in ['Soup', 'Hot Beverage']:
                score += 0.2
            elif item.category in ['Beverage', 'Juice']:
                score += 0.3
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_seasonal_score(item: MenuItem, season: str) -> float:
        """
        Calculate seasonal appropriateness score
        """
        score = 0.5  # Base score
        
        season_lower = season.lower()
        
        # Summer recommendations
        if season_lower in ['summer']:
            if item.category in ['Salad', 'Fruit', 'Beverage', 'Light Meal', 'Ice Cream']:
                score += 0.3
            elif item.category in ['Hot Soup', 'Heavy Meal']:
                score -= 0.2
        
        # Winter recommendations
        elif season_lower in ['winter']:
            if item.category in ['Hot Soup', 'Starter', 'Main Course', 'Hot Beverage']:
                score += 0.3
            elif item.category in ['Ice Cream', 'Cold Dessert', 'Salad']:
                score -= 0.2
        
        # Monsoon recommendations
        elif season_lower in ['monsoon']:
            if item.category in ['Hot Soup', 'Tea', 'Snack', 'Comfort Food']:
                score += 0.3
            elif item.category in ['Ice Cream']:
                score -= 0.1
        
        # Spring recommendations
        elif season_lower in ['spring']:
            score += 0.1  # Most foods are suitable in spring
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_comfort_score(item: MenuItem, temperature: float, condition: str) -> float:
        """
        Calculate comfort food score based on weather
        """
        score = 0.5  # Base score
        
        # Comfort foods based on weather
        if temperature <= 15 or 'rain' in condition.lower():
            if item.category in ['Soup', 'Hot Beverage', 'Comfort Food']:
                score += 0.4
            elif 'soup' in (item.description or '').lower():
                score += 0.3
        
        elif temperature >= 30:
            if item.category in ['Salad', 'Light Meal', 'Beverage']:
                score += 0.3
            elif item.category in ['Comfort Food']:
                score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def _get_season() -> str:
        """
        Get current season based on month
        """
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:  # [9, 10, 11]
            return 'monsoon'
    
    @staticmethod
    def _get_weather_tags(item: MenuItem, weather_data: Dict[str, Any]) -> List[str]:
        """
        Get weather-related tags for a menu item
        """
        tags = []
        temperature = weather_data.get('temperature', 25)
        condition = weather_data.get('condition', 'clear')
        
        # Temperature tags
        if temperature <= 10:
            tags.append('Cold Weather')
        elif temperature <= 20:
            tags.append('Cool Weather')
        elif temperature <= 30:
            tags.append('Warm Weather')
        else:
            tags.append('Hot Weather')
        
        # Condition tags
        if 'rain' in condition.lower():
            tags.append('Rainy Day')
        elif 'sunny' in condition.lower():
            tags.append('Sunny')
        elif 'cloudy' in condition.lower():
            tags.append('Cloudy')
        
        # Seasonal tags
        season = weather_data.get('season', 'summer')
        tags.append(season.title())
        
        return tags
    
    @staticmethod
    def _get_comfort_level(item: MenuItem, temperature: float, condition: str) -> str:
        """
        Get comfort level for current weather
        """
        if temperature <= 10 or 'rain' in condition.lower():
            return 'Comforting'
        elif temperature >= 35:
            return 'Cooling'
        elif 20 <= temperature <= 25:
            return 'Balanced'
        else:
            return 'Moderate'
    
    @staticmethod
    def get_fallback_preferences() -> Dict[str, Any]:
        """
        Fallback preferences for new users
        """
        return {
            'category_preferences': {'general': 0.5},
            'spice_preferences': {'mild': 0.6, 'spicy': 0.4},
            'dietary_preferences': {'vegetarian': 0.5, 'non-vegetarian': 0.5},
            'total_orders': 0,
            'explicit_preferences': 0,
            'interaction_count': 0
        }
    
    @staticmethod
    def get_fallback_recommendations(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fallback recommendations (popular items)
        """
        try:
            # Get most ordered items
            popular_items = db.query(
                MenuItem.id,
                MenuItem.name,
                MenuItem.description,
                MenuItem.price,
                MenuItem.category,
                MenuItem.image_url,
                func.count(OrderItem.id).label('order_count')
            ).join(
                OrderItem, MenuItem.id == OrderItem.menu_item_id
            ).filter(
                MenuItem.is_available == True
            ).group_by(
                MenuItem.id
            ).order_by(
                desc('order_count')
            ).limit(limit).all()
            
            recommendations = []
            for item in popular_items:
                recommendations.append({
                    'menu_item_id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': item.price,
                    'category': item.category,
                    'image_url': item.image_url,
                    'score': 0.5,
                    'confidence': 0.5,
                    'reasoning': 'Popular item',
                    'recommendation_type': 'popular'
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error in fallback recommendations: {e}")
            return []
    
    @staticmethod
    def get_mood_based_recommendations(
        db: Session, 
        user_id: int,
        mood_data: Dict[str, Any] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Step 7: Mood-based food suggestions
        """
        try:
            # If no mood data provided, use default mood analysis
            if mood_data is None:
                mood_data = AIRecommendationService._analyze_current_mood(user_id, db)
            
            current_mood = mood_data.get('mood', 'neutral')
            mood_intensity = mood_data.get('intensity', 0.5)  # 0-1 scale
            mood_context = mood_data.get('context', {})  # Additional context
            
            # Get user's order history to understand mood-food patterns
            user_orders = db.query(OrderItem, MenuItem, Order).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Order.user_id == user_id,
                Order.status == 'completed'
            ).all()
            
            # Analyze user's mood-based ordering patterns
            mood_preferences = AIRecommendationService._analyze_mood_preferences(user_orders)
            
            # Get available menu items
            menu_items = db.query(MenuItem).filter(
                MenuItem.is_available == True
            ).all()
            
            recommendations = []
            
            for item in menu_items:
                score = 0.0
                reasoning = []
                
                # Mood-based food matching
                mood_score = AIRecommendationService._calculate_mood_score(item, current_mood, mood_intensity, mood_preferences)
                score += mood_score * 0.4
                
                if mood_score > 0.7:
                    reasoning.append(f"Perfect for {current_mood} mood")
                elif mood_score > 0.5:
                    reasoning.append(f"Good match for {current_mood} feelings")
                
                # Emotional comfort food analysis
                comfort_score = AIRecommendationService._calculate_emotional_comfort(item, current_mood, mood_intensity)
                score += comfort_score * 0.3
                
                if comfort_score > 0.7:
                    reasoning.append("Emotional comfort food")
                elif comfort_score > 0.5:
                    reasoning.append("Mood-enhancing choice")
                
                # Nutritional mood impact
                nutrition_score = AIRecommendationService._calculate_nutritional_mood_impact(item, current_mood)
                score += nutrition_score * 0.2
                
                if nutrition_score > 0.7:
                    reasoning.append("Nutritionally supports mood")
                elif nutrition_score < 0.3:
                    reasoning.append("May affect mood negatively")
                
                # Texture and temperature preferences
                texture_score = AIRecommendationService._calculate_texture_mood_match(item, current_mood, mood_intensity)
                score += texture_score * 0.1
                
                if texture_score > 0.7:
                    reasoning.append("Perfect texture for current mood")
                
                # Spice level mood correlation
                spice_score = AIRecommendationService._calculate_spice_mood_match(item, current_mood, mood_intensity)
                score += spice_score * 0.1
                
                if spice_score > 0.7:
                    reasoning.append("Spice level matches mood")
                
                # Only include items with meaningful scores
                if score > 0.3:
                    recommendations.append({
                        'menu_item_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'price': item.price,
                        'category': item.category,
                        'image_url': item.image_url,
                        'calories': item.calories,
                        'is_vegetarian': item.is_vegetarian,
                        'is_spicy': item.is_spicy,
                        'score': score,
                        'confidence': min(score, 1.0),
                        'reasoning': '; '.join(reasoning),
                        'recommendation_type': 'mood_based',
                        'mood_data': {
                            'mood': current_mood,
                            'intensity': mood_intensity,
                            'context': mood_context
                        },
                        'mood_tags': AIRecommendationService._get_mood_tags(item, mood_data),
                        'emotional_impact': AIRecommendationService._get_emotional_impact(item, current_mood),
                        'comfort_level': AIRecommendationService._get_mood_comfort_level(item, current_mood)
                    })
            
            # Sort by score and limit results
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error in mood-based recommendations: {e}")
            return []
    
    @staticmethod
    def _analyze_current_mood(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Analyze current user mood based on time, day, and patterns
        """
        from datetime import datetime
        
        # Time-based mood analysis
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
        
        # Default mood based on time
        if 6 <= current_hour <= 10:
            base_mood = 'energetic'
            intensity = 0.7
        elif 11 <= current_hour <= 14:
            base_mood = 'focused'
            intensity = 0.6
        elif 15 <= current_hour <= 17:
            base_mood = 'relaxed'
            intensity = 0.5
        elif 18 <= current_hour <= 22:
            base_mood = 'social'
            intensity = 0.8
        else:  # Late night
            base_mood = 'tired'
            intensity = 0.4
        
        # Weekend adjustments
        if day_of_week >= 5:  # Weekend
            if base_mood == 'relaxed':
                intensity = 0.8
            elif base_mood == 'social':
                intensity = 0.9
        
        return {
            'mood': base_mood,
            'intensity': intensity,
            'context': {
                'time_of_day': current_hour,
                'day_of_week': day_of_week,
                'recent_orders': 0
            }
        }
    
    @staticmethod
    def _analyze_mood_preferences(user_orders: List) -> Dict[str, float]:
        """
        Analyze user's historical mood-based ordering patterns
        """
        mood_patterns = {
            'happy': 0,
            'energetic': 0,
            'stressed': 0,
            'relaxed': 0,
            'focused': 0,
            'social': 0,
            'sad': 0,
            'neutral': 0
        }
        
        # Analyze food choices for mood indicators
        for order_item, menu_item, order in user_orders:
            item_name = (menu_item.name or '').lower()
            item_desc = (menu_item.description or '').lower()
            category = (menu_item.category or '').lower()
            
            # Happy mood indicators
            if any(word in item_name or word in item_desc for word in ['sweet', 'dessert', 'chocolate', 'ice cream', 'cake']):
                mood_patterns['happy'] += 1
            
            # Energetic mood indicators
            elif any(word in item_name or word in item_desc for word in ['coffee', 'tea', 'energy', 'protein', 'boost']):
                mood_patterns['energetic'] += 1
            
            # Stressed mood indicators
            elif any(word in item_name or word in item_desc for word in ['comfort', 'soup', 'warm', 'hot', 'chocolate']):
                mood_patterns['stressed'] += 1
            
            # Relaxed mood indicators
            elif any(word in item_name or word in item_desc for word in ['light', 'salad', 'fruit', 'calm', 'peace']):
                mood_patterns['relaxed'] += 1
            
            # Focused mood indicators
            elif any(word in item_name or word in item_desc for word in ['healthy', 'protein', 'water', 'clean']):
                mood_patterns['focused'] += 1
            
            # Social mood indicators
            elif any(word in item_name or word in item_desc for word in ['sharing', 'combo', 'variety', 'party', 'snack']):
                mood_patterns['social'] += 1
            
            # Sad mood indicators
            elif any(word in item_name or word in item_desc for word in ['comfort', 'warm', 'sweet', 'chocolate']):
                mood_patterns['sad'] += 1
            
            # Default to neutral
            else:
                mood_patterns['neutral'] += 1
        
        total_patterns = sum(mood_patterns.values())
        if total_patterns > 0:
            for key in mood_patterns:
                mood_patterns[key] /= total_patterns
        
        return mood_patterns
    
    @staticmethod
    def _calculate_mood_score(item: MenuItem, mood: str, intensity: float, preferences: Dict[str, float]) -> float:
        """
        Calculate mood appropriateness score for food item
        """
        score = 0.5  # Base score
        
        item_name = (item.name or '').lower()
        item_desc = (item.description or '').lower()
        category = (item.category or '').lower()
        
        # Happy mood recommendations
        if mood == 'happy':
            if any(word in item_name or word in item_desc for word in ['sweet', 'dessert', 'chocolate', 'ice cream', 'cake', 'celebration']):
                score += 0.4
            elif item.category in ['Dessert', 'Sweet', 'Beverage']:
                score += 0.3
            elif item.is_spicy and intensity > 0.7:
                score -= 0.2  # Very spicy might reduce happiness
        
        # Energetic mood recommendations
        elif mood == 'energetic':
            if any(word in item_name or word in item_desc for word in ['protein', 'energy', 'boost', 'coffee', 'tea']):
                score += 0.4
            elif item.category in ['Main Course', 'Protein', 'Beverage']:
                score += 0.3
            elif item.calories and item.calories > 400:
                score += 0.2  # High energy foods
        
        # Stressed mood recommendations
        elif mood == 'stressed':
            if any(word in item_name or word in item_desc for word in ['comfort', 'warm', 'soup', 'hot', 'chocolate']):
                score += 0.4
            elif item.category in ['Hot Soup', 'Hot Beverage', 'Comfort Food']:
                score += 0.3
            elif item.is_spicy and intensity < 0.5:
                score += 0.1  # Mild spice can be comforting
            elif item.is_spicy and intensity > 0.7:
                score -= 0.3  # Too spicy when stressed
        
        # Relaxed mood recommendations
        elif mood == 'relaxed':
            if any(word in item_name or word in item_desc for word in ['light', 'calm', 'peace', 'gentle', 'soft']):
                score += 0.4
            elif item.category in ['Light Meal', 'Salad', 'Fruit', 'Tea']:
                score += 0.3
            elif item.is_spicy and intensity > 0.6:
                score -= 0.2
        
        # Focused mood recommendations
        elif mood == 'focused':
            if any(word in item_name or word in item_desc for word in ['healthy', 'clean', 'protein', 'brain', 'concentrate']):
                score += 0.4
            elif item.category in ['Healthy', 'Protein', 'Light Meal']:
                score += 0.3
            elif item.calories and item.calories < 400:
                score += 0.2  # Light foods help focus
        
        # Social mood recommendations
        elif mood == 'social':
            if any(word in item_name or word in item_desc for word in ['sharing', 'combo', 'variety', 'party', 'fun']):
                score += 0.4
            elif item.category in ['Combo', 'Snack', 'Variety']:
                score += 0.3
            elif item.price and item.price < 200:  # Affordable for sharing
                score += 0.1
        
        # Sad mood recommendations
        elif mood == 'sad':
            if any(word in item_name or word in item_desc for word in ['comfort', 'warm', 'sweet', 'chocolate', 'hug']):
                score += 0.4
            elif item.category in ['Comfort Food', 'Hot Soup', 'Hot Beverage']:
                score += 0.3
            elif item.is_spicy and intensity < 0.4:
                score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_emotional_comfort(item: MenuItem, mood: str, intensity: float) -> float:
        """
        Calculate emotional comfort score based on mood
        """
        score = 0.5  # Base score
        
        # Comfort foods for negative moods
        if mood in ['stressed', 'sad', 'tired']:
            if item.category in ['Comfort Food', 'Hot Soup', 'Hot Beverage']:
                score += 0.4
            elif any(word in (item.description or '').lower() for word in ['warm', 'comforting', 'soothing']):
                score += 0.3
            elif item.is_spicy and intensity < 0.5:
                score += 0.1
        
        # Uplifting foods for positive moods
        elif mood in ['happy', 'energetic', 'social']:
            if item.category in ['Dessert', 'Sweet', 'Celebration']:
                score += 0.3
            elif any(word in (item.description or '').lower() for word in ['uplifting', 'joyful', 'celebration']):
                score += 0.2
        
        # Calming foods for high intensity moods
        if intensity > 0.8:
            if item.category in ['Tea', 'Light Meal', 'Calm']:
                score += 0.2
            elif any(word in (item.description or '').lower() for word in ['calming', 'soothing']):
                score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_nutritional_mood_impact(item: MenuItem, mood: str) -> float:
        """
        Calculate how food nutrition impacts mood
        """
        score = 0.5  # Base score
        
        # Mood-boosting nutrients
        if item.category in ['Healthy', 'Protein', 'Fruit', 'Vegetable']:
            score += 0.3
        
        # Sugar impact on mood
        if any(word in (item.description or '').lower() for word in ['sugar', 'sweet']):
            if mood in ['happy', 'energetic']:
                score += 0.2  # Sugar can boost these moods
            elif mood in ['stressed', 'sad']:
                score += 0.1  # Comforting effect
            else:
                score -= 0.1  # May cause crashes
        
        # Caffeine impact
        if any(word in (item.description or '').lower() for word in ['caffeine', 'coffee', 'tea']):
            if mood in ['focused', 'energetic']:
                score += 0.3
            elif mood in ['stressed', 'tired']:
                score += 0.1
            elif mood in ['relaxed', 'social']:
                score -= 0.2
        
        # Complex carbs for sustained energy
        if item.calories and 200 <= item.calories <= 400:
            if mood in ['focused', 'energetic']:
                score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_texture_mood_match(item: MenuItem, mood: str, intensity: float) -> float:
        """
        Calculate texture appropriateness for mood
        """
        score = 0.5  # Base score
        
        item_desc = (item.description or '').lower()
        
        # Texture preferences based on mood
        if mood in ['stressed', 'sad', 'tired']:
            if any(word in item_desc for word in ['soft', 'smooth', 'creamy', 'warm']):
                score += 0.3
            elif any(word in item_desc for word in ['crunchy', 'hard', 'rough']):
                score -= 0.2
        
        elif mood in ['happy', 'energetic', 'social']:
            if any(word in item_desc for word in ['crunchy', 'crispy', 'textured']):
                score += 0.2
            elif any(word in item_desc for word in ['soft', 'smooth', 'creamy']):
                score += 0.1
        
        elif mood in ['relaxed', 'focused']:
            if any(word in item_desc for word in ['light', 'delicate', 'fine']):
                score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_spice_mood_match(item: MenuItem, mood: str, intensity: float) -> float:
        """
        Calculate spice level appropriateness for mood
        """
        score = 0.5  # Base score
        
        if mood in ['energetic', 'social']:
            if item.is_spicy:
                score += 0.2  # Spice can be stimulating
        elif mood in ['stressed', 'tired']:
            if item.is_spicy and intensity < 0.5:
                score += 0.1  # Mild spice can be comforting
            elif item.is_spicy and intensity > 0.7:
                score -= 0.3  # Too spicy when stressed
        elif mood in ['relaxed', 'focused']:
            if not item.is_spicy:
                score += 0.1  # Mild foods better for concentration
        
        return min(score, 1.0)
    
    @staticmethod
    def _get_mood_tags(item: MenuItem, mood_data: Dict[str, Any]) -> List[str]:
        """
        Get mood-related tags for a menu item
        """
        tags = []
        mood = mood_data.get('mood', 'neutral')
        intensity = mood_data.get('intensity', 0.5)
        
        # Mood tags
        tags.append(mood.title())
        
        # Intensity tags
        if intensity >= 0.8:
            tags.append('Intense')
        elif intensity <= 0.3:
            tags.append('Mild')
        else:
            tags.append('Moderate')
        
        # Emotional impact tags
        if mood in ['happy', 'energetic']:
            tags.append('Uplifting')
        elif mood in ['relaxed', 'focused']:
            tags.append('Calming')
        elif mood in ['stressed', 'sad', 'tired']:
            tags.append('Comforting')
        else:
            tags.append('Balanced')
        
        return tags
    
    @staticmethod
    def _get_emotional_impact(item: MenuItem, mood: str) -> str:
        """
        Get emotional impact for current mood
        """
        if mood == 'happy':
            return 'Joyful'
        elif mood == 'energetic':
            return 'Stimulating'
        elif mood == 'relaxed':
            return 'Calming'
        elif mood == 'focused':
            return 'Supportive'
        elif mood == 'social':
            return 'Celebratory'
        elif mood == 'stressed':
            return 'Comforting'
        elif mood == 'sad':
            return 'Nurturing'
        elif mood == 'tired':
            return 'Restoring'
        else:
            return 'Balanced'
    
    @staticmethod
    def _get_mood_comfort_level(item: MenuItem, mood: str) -> str:
        """
        Get comfort level for current mood
        """
        if mood in ['happy', 'energetic', 'social']:
            return 'Enhancing'
        elif mood in ['relaxed', 'focused']:
            return 'Supportive'
        elif mood in ['stressed', 'sad', 'tired']:
            return 'Comforting'
        else:
            return 'Neutral'
    
    @staticmethod
    def get_fallback_preferences() -> Dict[str, Any]:
        """
        Fallback preferences for new users
        """
        return {
            'category_preferences': {'general': 0.5},
            'spice_preferences': {'mild': 0.6, 'spicy': 0.4},
            'dietary_preferences': {'vegetarian': 0.5, 'non-vegetarian': 0.5},
            'total_orders': 0,
            'explicit_preferences': 0,
            'interaction_history': []
        }
