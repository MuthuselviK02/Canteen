"""
Menu Item Management API Endpoints

These endpoints provide complete menu item management including deletion
and cleanup of related records.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database.session import get_db
from app.core.dependencies import admin_only
from app.services.menu_item_deletion_service import MenuItemDeletionService

router = APIRouter(prefix="/api/menu-items", tags=["Menu Item Management"])


class MenuItemDeletionRequest(BaseModel):
    menu_item_id: int
    confirm_deletion: bool = False


class BatchMenuItemDeletionRequest(BaseModel):
    menu_item_ids: List[int]
    confirm_deletion: bool = False


@router.delete("/{menu_item_id}/delete")
def delete_menu_item(
    menu_item_id: int,
    confirm: bool = False,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Delete a menu item and all its related records.
    
    WARNING: This is a permanent deletion that will remove:
    - The menu item itself
    - All order items for this menu item
    - All inventory logs
    - All stock updates
    - All demand forecasts
    - All preparation time predictions
    
    Set confirm=true to proceed with deletion.
    """
    if not confirm:
        # First show what will be deleted
        references = MenuItemDeletionService.get_menu_item_references(db, menu_item_id)
        if "error" in references:
            raise HTTPException(status_code=404, detail=references["error"])
        
        return {
            "warning": "This will permanently delete the menu item and all related records",
            "confirm_required": True,
            "item_info": references,
            "deletion_endpoint": f"/api/menu-items/{menu_item_id}/delete?confirm=true"
        }
    
    # Perform the actual deletion
    result = MenuItemDeletionService.delete_menu_item_complete(db, menu_item_id)
    
    if not result["success"]:
        if "not found" in result.get("error", "").lower():
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.get("/{menu_item_id}/references")
def get_menu_item_references(
    menu_item_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Get all records that reference a menu item.
    Useful for understanding what will be deleted before deletion.
    """
    references = MenuItemDeletionService.get_menu_item_references(db, menu_item_id)
    
    if "error" in references:
        raise HTTPException(status_code=404, detail=references["error"])
    
    return references


@router.post("/batch-delete")
def batch_delete_menu_items(
    request: BatchMenuItemDeletionRequest,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Delete multiple menu items in a single operation.
    
    WARNING: This is a permanent deletion for all specified menu items.
    Set confirm_deletion=true to proceed.
    """
    if not request.confirm_deletion:
        # Show what will be deleted for each item
        preview = {
            "warning": "This will permanently delete multiple menu items and all their related records",
            "confirm_required": True,
            "items_to_delete": len(request.menu_item_ids),
            "items_preview": []
        }
        
        for menu_item_id in request.menu_item_ids:
            references = MenuItemDeletionService.get_menu_item_references(db, menu_item_id)
            if "error" not in references:
                preview["items_preview"].append(references)
        
        return preview
    
    # Perform the actual batch deletion
    result = MenuItemDeletionService.batch_delete_menu_items(db, request.menu_item_ids)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Batch deletion failed"))
    
    return result


@router.post("/cleanup-orphaned")
def cleanup_orphaned_menu_items(
    confirm: bool = False,
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Find and optionally delete orphaned menu items.
    This is a maintenance endpoint for database cleanup.
    """
    if not confirm:
        # Just show what would be cleaned up
        result = MenuItemDeletionService.cleanup_orphaned_menu_items(db)
        return {
            "preview": result,
            "confirm_required": True,
            "cleanup_endpoint": "/api/menu-items/cleanup-orphaned?confirm=true"
        }
    
    # Perform the actual cleanup
    result = MenuItemDeletionService.cleanup_orphaned_menu_items(db)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.get("/deletion-summary")
def get_deletion_summary(
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Get a summary of all menu items and their reference counts.
    Useful for identifying items that can be safely deleted.
    """
    from app.models.menu import MenuItem
    
    menu_items = db.query(MenuItem).all()
    summary = {
        "total_menu_items": len(menu_items),
        "items_with_references": [],
        "items_without_orders": []
    }
    
    for item in menu_items:
        references = MenuItemDeletionService.get_menu_item_references(db, item.id)
        if "error" not in references:
            item_data = {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "total_references": references["total_references"],
                "references": references["references"]
            }
            
            summary["items_with_references"].append(item_data)
            
            if references["references"]["order_items"] == 0:
                summary["items_without_orders"].append(item_data)
    
    return summary
