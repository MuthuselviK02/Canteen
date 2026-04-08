import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.menu import MenuCreate, MenuResponse
from app.services.menu_service import create_menu_item, update_menu_item, delete_menu_item
from app.core.dependencies import super_admin_only

router = APIRouter(prefix="/api/admin/menu", tags=["Admin Menu"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=MenuResponse)
def create(item: MenuCreate, db: Session = Depends(get_db), admin=Depends(super_admin_only)):
    try:
        return create_menu_item(db, item, admin.id)
    except Exception as exc:
        logger.exception("Failed to create menu item", exc_info=exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{item_id}", response_model=MenuResponse)
def update(
    item_id: int,
    data: MenuCreate,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_only),
):
    try:
        item = update_menu_item(db, item_id, data)
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return item
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update menu item", exc_info=exc)
        raise HTTPException(status_code=500, detail="Unable to update menu item. Please try again.")


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db), admin=Depends(super_admin_only)):
    return delete_menu_item(db, item_id)
