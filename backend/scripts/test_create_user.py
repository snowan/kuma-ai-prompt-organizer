import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_db, init_db
from app.models import User
from app.core.security import get_password_hash

async def create_user():
    print("Creating test user...")
    
    # Initialize the database
    await init_db()
    
    # Get database session
    db = await anext(get_db())
    
    try:
        # Check if user already exists
        result = await db.execute(
            "SELECT * FROM users WHERE username = 'testuser'"
        )
        if result.first():
            print("Test user already exists!")
            print("Username: testuser")
            print("Password: testpassword")
            return
        
        # Create test user
        hashed_password = get_password_hash("testpassword")
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        
        print("Test user created successfully!")
        print("Username: testuser")
        print("Password: testpassword")
        print("\nYou can now use these credentials to log in.")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(create_user())
