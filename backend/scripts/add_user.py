import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_db, init_db
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    print("Creating user...")
    
    # Initialize the database
    await init_db()
    
    # Get database session
    db = await anext(get_db())
    
    # Create user
    hashed_password = pwd_context.hash("admin123")
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    print("User created successfully!")
    print(f"Username: admin")
    print(f"Password: admin123")
    print("\nPlease change this password after your first login!")

if __name__ == "__main__":
    asyncio.run(create_user())
