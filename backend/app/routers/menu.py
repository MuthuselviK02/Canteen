from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.menu_service import get_menu
from app.schemas.menu import MenuResponse

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("/", response_model=list[MenuResponse])
def fetch_menu(db: Session = Depends(get_db)):
    """
    Public endpoint.
    Returns all available food items with category labels.
    """
    menu_items = get_menu(db)
    return [MenuResponse.from_db_item(item) for item in menu_items]
