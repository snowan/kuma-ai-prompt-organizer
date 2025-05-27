import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.database import get_db, init_db
from app.models import User

async def create_admin_user():
    print("Creating admin user...")
    
    # Initialize the database
    await init_db()
    
    # Get database session
    db = await anext(get_db())
    
    # Check if admin user already exists
    result = await db.execute(
        "SELECT * FROM users WHERE username = 'admin'"
    )
    admin = result.first()
    
    if admin:
        print("Admin user already exists!")
        print(f"Username: admin")
        print(f"Password: [use the one you set earlier]")
        return
    
    # Create admin user
    hashed_password = get_password_hash("admin123")
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    print("Admin user created successfully!")
    print(f"Username: admin")
    print(f"Password: admin123")
    print("\nPlease change this password after your first login!")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
