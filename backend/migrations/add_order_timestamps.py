"""
Database Migration: Add timestamp fields to orders table
Production-ready migration for order time tracking
"""

import sqlite3
import os

def run_migration():
    """
    Add new timestamp columns to the orders table
    """
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), "..", "canteen.db")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add columns if they don't exist
        if 'started_preparation_at' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN started_preparation_at DATETIME NULL")
            print("✅ Added 'started_preparation_at' column")
        
        if 'ready_at' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN ready_at DATETIME NULL")
            print("✅ Added 'ready_at' column")
        
        if 'completed_at' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN completed_at DATETIME NULL")
            print("✅ Added 'completed_at' column")
        
        conn.commit()
        conn.close()
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

def verify_migration():
    """
    Verify that the migration was successful
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", "canteen.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['started_preparation_at', 'ready_at', 'completed_at']
        missing_columns = [col for col in required_columns if col not in columns]
        
        conn.close()
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All timestamp columns are present")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Running database migration for order timestamps...")
    run_migration()
    
    if verify_migration():
        print("✅ Migration verified successfully!")
    else:
        print("❌ Migration verification failed!")
        exit(1)
