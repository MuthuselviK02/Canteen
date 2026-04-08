from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse
)
from app.services.inventory_service import (
    create_inventory,
    update_inventory_stock,
    get_all_inventory
)
from app.core.dependencies import admin_only

router = APIRouter(
    prefix="/api/admin/inventory",
    tags=["Admin Inventory"]
)


@router.post("/", response_model=InventoryResponse)
def add_inventory(
    data: InventoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    return create_inventory(
        db,
        data.menu_item_id,
        data.stock_quantity
    )


@router.put("/{menu_item_id}", response_model=InventoryResponse)
def update_inventory(
    menu_item_id: int,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    return update_inventory_stock(
        db,
        menu_item_id,
        data.stock_quantity
    )


@router.get("/", response_model=list[InventoryResponse])
def list_inventory(
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    return get_all_inventory(db)

