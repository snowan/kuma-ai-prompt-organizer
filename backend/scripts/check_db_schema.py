import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_schema():
    # Get the absolute path to the database file
    db_path = os.path.abspath("sql_app.db")
    print(f"Using database file: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check prompts table
        print("\nChecking 'prompts' table:")
        cursor.execute("PRAGMA table_info(prompts)")
        print("Columns in 'prompts' table:")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]}) {'NOT NULL' if not column[3] else ''} {column[4] or ''}")
        
        # Check prompt_likes table
        print("\nChecking 'prompt_likes' table:")
        cursor.execute("PRAGMA table_info(prompt_likes)")
        print("Columns in 'prompt_likes' table:")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]}) {'NOT NULL' if not column[3] else ''} {column[4] or ''}")
        
        # Check foreign key constraints
        print("\nForeign key constraints:")
        cursor.execute("""
            SELECT * FROM sqlite_master 
            WHERE type = 'table' 
            AND sql LIKE '%FOREIGN KEY%'
        """)
        fk_tables = cursor.fetchall()
        if fk_tables:
            for table in fk_tables:
                print(f"  {table[1]}: {table[4]}")
        else:
            print("  No foreign key constraints found")
            
        # Check indexes
        print("\nChecking indexes...")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type = 'index'")
        indexes = cursor.fetchall()
        if indexes:
            for idx in indexes:
                print(f"  Index: {idx[0]}")
                print(f"    SQL: {idx[1]}")
        else:
            print("  No indexes found")
            
        print("\nSchema check complete.")
            
    except sqlite3.Error as e:
        print(f"Error checking schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Checking database schema...")
    check_schema()
