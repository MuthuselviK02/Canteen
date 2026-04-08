import logging

from sqlalchemy.orm import Session
from app.models.menu import MenuItem
from app.core.categories import migrate_legacy_category

logger = logging.getLogger(__name__)


def get_menu(db: Session):
    """Get all available menu items with category migration"""
    items = db.query(MenuItem).filter(MenuItem.is_available == True).all()
    
    # Migrate legacy categories to canonical keys
    for item in items:
        if item.category and not item.category.startswith('_'):  # Skip if already migrated
            try:
                # Check if category is already a valid key
                from app.core.categories import is_valid_category
                if not is_valid_category(item.category):
                    # Migrate legacy category to canonical key
                    item.category = migrate_legacy_category(item.category)
                    db.commit()
            except Exception as e:
                logger.warning(f"Failed to migrate category for item {item.id}: {e}")
                # Set default category if migration fails
                item.category = "main_course"
                db.commit()
    
    return items


def create_menu_item(db: Session, data, admin_id: int):
    """Create menu item with category migration"""
    try:
        payload = data.dict()
        logger.info(f"Creating menu item with payload: {payload}")
        
        # Migrate category if needed
        if 'category' in payload:
            payload['category'] = migrate_legacy_category(payload['category'])
        
        item = MenuItem(**payload)
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"Created menu item: {item.id} - {item.name}")
        return item
    except Exception as exc:
        logger.exception("create_menu_item failed", exc_info=exc)
        raise exc


def update_menu_item(db: Session, item_id: int, data):
    """Update menu item with category migration"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return None

    update_data = data.dict(exclude_unset=True)
    
    # Migrate category if present
    if 'category' in update_data:
        update_data['category'] = migrate_legacy_category(update_data['category'])

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)   # IMPORTANT
    return item        # IMPORTANT

def delete_menu_item(db: Session, item_id: int):
    item = db.query(MenuItem).get(item_id)
    if not item:
        return False

    item.is_available = False
    db.commit()
    return True
