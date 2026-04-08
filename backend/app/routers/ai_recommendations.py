from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.services.ai_recommendation_service import AIRecommendationService
from app.models.user import User

router = APIRouter(prefix="/api/ai", tags=["AI Recommendations"])

class RecommendationResponse(BaseModel):
    menu_item_id: int
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    image_url: Optional[str]
    score: float
    confidence: float
    reasoning: str
    recommendation_type: str
    meal_type: Optional[str] = None

class InteractionRequest(BaseModel):
    menu_item_id: int
    interaction_type: str  # 'view', 'order', 'favorite', 'rating'
    interaction_value: Optional[float] = None
    context_data: Optional[dict] = None

class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total_count: int
    recommendation_types: List[str]

@router.get("/recommendations/preferences", response_model=RecommendationListResponse)
async def get_preference_recommendations(
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 1: Get AI-powered menu recommendations based on user preferences
    """
    try:
        recommendations = AIRecommendationService.get_preference_based_recommendations(
            db, current_user.id, limit
        )
        
        return RecommendationListResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
            recommendation_types=["preference_based"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting preference recommendations: {str(e)}")

@router.get("/recommendations/time-based", response_model=RecommendationListResponse)
async def get_time_based_recommendations(
    limit: int = Query(5, ge=1, le=15),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 2: Get intelligent meal suggestions based on time of day
    """
    try:
        recommendations = AIRecommendationService.get_time_based_recommendations(
            db, current_user.id, datetime.utcnow(), limit
        )
        
        return RecommendationListResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
            recommendation_types=["time_based"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting time-based recommendations: {str(e)}")

@router.get("/recommendations/combo", response_model=RecommendationListResponse)
async def get_combo_recommendations(
    limit: int = Query(5, ge=1, le=15),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 3: Get personalized combo suggestions using order history
    """
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        
        recommendations = AIRecommendationService.get_combo_recommendations(
            db, current_user.id, limit
        )
        
        # Convert combo recommendations to response format
        response_recommendations = []
        combo_id_counter = 999999  # Start from a high number to avoid conflicts
        for rec in recommendations:
            combo_id = combo_id_counter  # Use integer instead of string
            response_recommendations.append(RecommendationResponse(
                menu_item_id=combo_id,  # Use integer combo_id for combos
                name=rec['name'],
                description=rec['description'],
                price=rec['total_price'],
                category=f"Combo ({rec['item_count']} items)",
                image_url=None,  # Combos don't have single images
                score=rec['score'],
                confidence=rec['confidence'],
                reasoning=rec['reasoning'],
                recommendation_type=rec['recommendation_type']
            ))
            combo_id_counter += 1
        
        return RecommendationListResponse(
            recommendations=response_recommendations,
            total_count=len(response_recommendations),
            recommendation_types=["combo"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting combo recommendations: {str(e)}")

@router.get("/recommendations/dietary", response_model=RecommendationListResponse)
async def get_dietary_recommendations(
    dietary_restrictions: str = Query(None),  # Comma-separated list
    limit: int = Query(5, ge=1, le=15),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 4: Get dietary preference learning recommendations
    """
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        
        # Parse dietary restrictions
        restrictions = []
        if dietary_restrictions:
            restrictions = [r.strip() for r in dietary_restrictions.split(',')]
        
        recommendations = AIRecommendationService.get_dietary_recommendations(
            db, current_user.id, restrictions, limit
        )
        
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(RecommendationResponse(**rec))
        
        return RecommendationListResponse(
            recommendations=response_recommendations,
            total_count=len(response_recommendations),
            recommendation_types=["dietary"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dietary recommendations: {str(e)}")

@router.get("/recommendations/calorie-conscious", response_model=RecommendationListResponse)
async def get_calorie_conscious_recommendations(
    daily_calorie_goal: int = Query(2000, ge=1000, le=5000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 5: Get calorie-conscious meal planning recommendations
    """
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        
        recommendations = AIRecommendationService.get_calorie_conscious_recommendations(
            db, current_user.id, daily_calorie_goal
        )
        
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(RecommendationResponse(**rec))
        
        return RecommendationListResponse(
            recommendations=response_recommendations,
            total_count=len(response_recommendations),
            recommendation_types=["calorie_conscious"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting calorie-conscious recommendations: {str(e)}")

@router.get("/recommendations/weather-based", response_model=RecommendationListResponse)
async def get_weather_based_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 6: Get weather-based food recommendations
    """
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        
        recommendations = AIRecommendationService.get_weather_based_recommendations(
            db, current_user.id
        )
        
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(RecommendationResponse(**rec))
        
        return RecommendationListResponse(
            recommendations=response_recommendations,
            total_count=len(response_recommendations),
            recommendation_types=["weather_based"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weather-based recommendations: {str(e)}")

@router.get("/recommendations/mood-based", response_model=RecommendationListResponse)
async def get_mood_based_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 7: Get mood-based food suggestions
    """
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        
        recommendations = AIRecommendationService.get_mood_based_recommendations(
            db, current_user.id
        )
        
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(RecommendationResponse(**rec))
        
        return RecommendationListResponse(
            recommendations=response_recommendations,
            total_count=len(response_recommendations),
            recommendation_types=["mood_based"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mood-based recommendations: {str(e)}")

@router.get("/recommendations/all", response_model=RecommendationListResponse)
async def get_all_recommendations(
    preference_limit: int = Query(2, ge=1, le=10),
    time_limit: int = Query(2, ge=1, le=10),
    combo_limit: int = Query(2, ge=1, le=10),
    dietary_limit: int = Query(2, ge=1, le=10),
    calorie_limit: int = Query(2, ge=1, le=10),
    daily_calorie_goal: int = Query(2000, ge=1000, le=5000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all types of recommendations combined
    """
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        
        # Get preference-based recommendations
        preference_recs = AIRecommendationService.get_preference_based_recommendations(
            db, current_user.id, preference_limit
        )
        
        # Get time-based recommendations
        time_recs = AIRecommendationService.get_time_based_recommendations(
            db, current_user.id, datetime.utcnow(), time_limit
        )
        
        # Get combo recommendations
        combo_recs = AIRecommendationService.get_combo_recommendations(
            db, current_user.id, combo_limit
        )
        
        # Get dietary recommendations
        dietary_recs = AIRecommendationService.get_dietary_recommendations(
            db, current_user.id, None, dietary_limit
        )
        
        # Get calorie-conscious recommendations
        calorie_recs = AIRecommendationService.get_calorie_conscious_recommendations(
            db, current_user.id, daily_calorie_goal
        )
        
        # Get weather-based recommendations
        weather_recs = AIRecommendationService.get_weather_based_recommendations(
            db, current_user.id
        )
        
        # Get mood-based recommendations
        mood_recs = AIRecommendationService.get_mood_based_recommendations(
            db, current_user.id
        )
        
        # Combine and deduplicate
        all_recommendations = []
        seen_items = set()
        
        # Add preference recommendations first
        for rec in preference_recs:
            if rec['menu_item_id'] not in seen_items:
                all_recommendations.append(RecommendationResponse(**rec))
                seen_items.add(rec['menu_item_id'])
        
        # Add time-based recommendations
        for rec in time_recs:
            if rec['menu_item_id'] not in seen_items:
                all_recommendations.append(RecommendationResponse(**rec))
                seen_items.add(rec['menu_item_id'])
        
        # Add combo recommendations
        combo_id_counter = 999999  # Start from a high number to avoid conflicts
        for rec in combo_recs:
            combo_id = combo_id_counter  # Use integer instead of string
            if combo_id not in seen_items:
                all_recommendations.append(RecommendationResponse(
                    menu_item_id=combo_id,
                    name=rec['name'],
                    description=rec['description'],
                    price=rec['total_price'],
                    category=f"Combo ({rec['item_count']} items)",
                    image_url=None,
                    score=rec['score'],
                    confidence=rec['confidence'],
                    reasoning=rec['reasoning'],
                    recommendation_type=rec['recommendation_type']
                ))
                seen_items.add(combo_id)
                combo_id_counter += 1
        
        # Add dietary recommendations
        for rec in dietary_recs:
            if rec['menu_item_id'] not in seen_items:
                all_recommendations.append(RecommendationResponse(**rec))
                seen_items.add(rec['menu_item_id'])
        
        # Add calorie-conscious recommendations
        for rec in calorie_recs:
            if rec['menu_item_id'] not in seen_items:
                all_recommendations.append(RecommendationResponse(**rec))
                seen_items.add(rec['menu_item_id'])
        
        # Add weather-based recommendations
        for rec in weather_recs:
            if rec['menu_item_id'] not in seen_items:
                all_recommendations.append(RecommendationResponse(**rec))
                seen_items.add(rec['menu_item_id'])
        
        # Add mood-based recommendations
        for rec in mood_recs:
            if rec['menu_item_id'] not in seen_items:
                all_recommendations.append(RecommendationResponse(**rec))
                seen_items.add(rec['menu_item_id'])
        
        return RecommendationListResponse(
            recommendations=all_recommendations,
            total_count=len(all_recommendations),
            recommendation_types=["preference_based", "time_based", "combo", "dietary", "calorie_conscious", "weather_based", "mood_based"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.post("/interactions")
async def save_user_interaction(
    interaction: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save user interaction for AI learning
    """
    try:
        AIRecommendationService.save_user_interaction(
            db=db,
            user_id=current_user.id,
            menu_item_id=interaction.menu_item_id,
            interaction_type=interaction.interaction_type,
            interaction_value=interaction.interaction_value,
            context_data=interaction.context_data
        )
        
        return {"message": "Interaction saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving interaction: {str(e)}")

@router.get("/preferences")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's preference profile
    """
    try:
        preferences = AIRecommendationService.get_user_preferences(db, current_user.id)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")

@router.post("/preferences")
async def update_user_preference(
    preference_type: str,
    preference_value: str,
    weight: float = Query(1.0, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences
    """
    try:
        from app.models.ai_recommendations import UserPreference
        
        # Check if preference already exists
        existing_pref = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id,
            UserPreference.preference_type == preference_type,
            UserPreference.preference_value == preference_value
        ).first()
        
        if existing_pref:
            existing_pref.weight = weight
            existing_pref.updated_at = datetime.utcnow()
        else:
            new_pref = UserPreference(
                user_id=current_user.id,
                preference_type=preference_type,
                preference_value=preference_value,
                weight=weight
            )
            db.add(new_pref)
        
        db.commit()
        return {"message": "Preference updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating preference: {str(e)}")
