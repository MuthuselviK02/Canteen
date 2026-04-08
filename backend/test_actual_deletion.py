"""
Complete Menu Item Deletion Test

This will actually delete a menu item to demonstrate the full functionality.
"""

import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.services.menu_item_deletion_service import MenuItemDeletionService

def test_actual_deletion():
    db = SessionLocal()
    
    print('=== ACTUAL MENU ITEM DELETION TEST ===')
    
    try:
        # Find a safe item to delete (one of the items with no orders)
        # Let's use ID 66 which seems to be a test item based on the name "aslkh;ih"
        test_item_id = 66
        
        # First check what will be deleted
        print(f'Checking references for item ID {test_item_id}...')
        references = MenuItemDeletionService.get_menu_item_references(db, test_item_id)
        
        if 'error' in references:
            print(f'Error: {references["error"]}')
            return
        
        print(f'Item to delete: {references["menu_item_name"]}')
        print(f'Records that will be deleted:')
        for ref_type, count in references['references'].items():
            print(f'  {ref_type}: {count}')
        print(f'Total records to delete: {references["total_references"]}')
        
        # Confirm deletion
        if references["total_references"] <= 2:  # Only the menu item itself
            print(f'Safe to proceed with deletion')
            
            # Perform the actual deletion
            print(f'Deleting {references["menu_item_name"]}...')
            result = MenuItemDeletionService.delete_menu_item_complete(db, test_item_id)
            
            if result["success"]:
                print(f'SUCCESS: {result["message"]}')
                print(f'Deleted records summary:')
                for record_type, count in result["deleted_records"].items():
                    print(f'  {record_type}: {count}')
                print(f'Total records deleted: {result["total_records_deleted"]}')
                
                # Verify deletion
                from app.models.menu import MenuItem
                remaining_item = db.query(MenuItem).filter(MenuItem.id == test_item_id).first()
                if remaining_item is None:
                    print(f'VERIFIED: Menu item {test_item_id} no longer exists in database')
                else:
                    print(f'ERROR: Menu item still exists in database')
            else:
                print(f'DELETION FAILED: {result["error"]}')
        else:
            print(f'SKIPPING: Item has {references["total_references"]} references, too many to delete in test')
        
    except Exception as e:
        print(f'Error during deletion test: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print('=== DELETION TEST COMPLETE ===')

if __name__ == "__main__":
    test_actual_deletion()
