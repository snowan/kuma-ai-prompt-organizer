import sqlite3
from pathlib import Path
from datetime import datetime
from passlib.hash import bcrypt

# Path to the SQLite database
DB_PATH = Path(__file__).parent.parent / "sql_app.db"

def create_user():
    print("Creating user...")
    
    # Connect to the database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users';
    """)
    
    if not cursor.fetchone():
        print("Error: 'users' table does not exist.")
        return
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        print("User 'admin' already exists!")
        print("Username: admin")
        print("Password: [use the one you set earlier]")
        return
    
    # Create user
    hashed_password = bcrypt.hash("admin123")
    created_at = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO users (username, email, hashed_password, is_active, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, ("admin", "admin@example.com", hashed_password, True, created_at))
    
    conn.commit()
    conn.close()
    
    print("User created successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("\nPlease change this password after your first login!")

if __name__ == "__main__":
    create_user()
