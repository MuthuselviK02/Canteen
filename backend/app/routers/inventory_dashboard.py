from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import admin_only
from app.database.session import get_db
from app.schemas.inventory import (
    InventoryDashboardResponse,
    ManualStockUpdateRequest,
    ManualStockUpdateResponse,
)
from app.services.inventory_service import (
    get_inventory_dashboard,
    manual_stock_update_with_confirmation,
)

router = APIRouter(
    prefix="/api/inventory",
    tags=["Inventory"],
)


def _parse_iso_datetime(value: str) -> datetime:
    # Frontend may send timestamps with trailing 'Z'
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@router.get("/dashboard", response_model=InventoryDashboardResponse)
def get_inventory_dashboard_api(
    start_date: str = Query(...),
    end_date: str = Query(...),
    category: str = Query("all"),
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    try:
        print(f"[DEBUG] Inventory dashboard request: start={start_date}, end={end_date}, category={category}")
        
        start_dt = _parse_iso_datetime(start_date)
        end_dt = _parse_iso_datetime(end_date)
        
        print(f"[DEBUG] Parsed dates: start={start_dt}, end={end_dt}")

        # Predictions are guidance only; this endpoint accepts an optional mapping in the future.
        kpis, items = get_inventory_dashboard(db, start_dt, end_dt, category=category)
        
        print(f"[DEBUG] Generated {len(items)} items, KPIs: {kpis}")

        return {
            "inventory_kpis": kpis,
            "inventory_items": items,
        }
    except Exception as e:
        print(f"[ERROR] Inventory dashboard error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inventory dashboard failed: {str(e)}")


@router.post("/sync-inventory")
def sync_inventory_from_orders(
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    """
    Manually sync inventory levels from all completed orders.
    This ensures inventory reflects all past order completions.
    """
    try:
        from app.services.realtime_inventory_service import RealTimeInventoryService
        
        print(f"Starting inventory sync at {datetime.utcnow()}")
        RealTimeInventoryService.bulk_update_inventory_for_completed_orders(db)
        print(f"Inventory sync completed at {datetime.utcnow()}")
        
        return {
            "message": "Inventory sync completed successfully",
            "synced_at": datetime.utcnow().isoformat()
        }
    except ImportError as e:
        print(f"Import error in sync endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Service import failed: {str(e)}")
    except Exception as e:
        print(f"Error in inventory sync: {e}")
        raise HTTPException(status_code=500, detail=f"Inventory sync failed: {str(e)}")


@router.post("/stock-update", response_model=ManualStockUpdateResponse)
def post_manual_stock_update(
    payload: ManualStockUpdateRequest,
    db: Session = Depends(get_db),
    admin=Depends(admin_only),
):
    result = manual_stock_update_with_confirmation(
        db=db,
        menu_item_id=payload.menu_item_id,
        quantity_delta=payload.quantity_delta,
        set_stock_quantity=payload.set_stock_quantity,
        reason=payload.reason,
        confirmed=payload.confirmed,
    )
    return result
