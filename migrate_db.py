import sqlite3
import sys

def migrate():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Check if wishlist_name exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'wishlist_name' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN wishlist_name VARCHAR(100);")
            print("Added wishlist_name")
            
        if 'wishlist_price' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN wishlist_price FLOAT;")
            print("Added wishlist_price")
            
        conn.commit()
        print("Migration successful")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    migrate()
