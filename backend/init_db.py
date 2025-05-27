import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app import models

def init_db():
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # Create engine and session
    engine = create_engine(database_url, connect_args={"check_same_thread": False} if "sqlite" in database_url else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Create a sample category and prompt if database is empty
    db = SessionLocal()
    try:
        # Check if we already have data
        if not db.query(models.Category).first():
            print("Creating sample data...")
            
            # Create a sample category
            category = models.Category(
                name="Sample Category",
                description="A sample category for demonstration purposes"
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            
            # Create a sample prompt
            prompt = models.Prompt(
                title="Sample Prompt",
                content="This is a sample prompt to demonstrate the API functionality.",
                category_id=category.id
            )
            db.add(prompt)
            db.commit()
            
            # Create some sample tags
            tags = ["sample", "demo", "test"]
            for tag_name in tags:
                tag = models.Tag(name=tag_name)
                db.add(tag)
                prompt.tags.append(tag)
            
            db.commit()
            print("Sample data created successfully!")
        else:
            print("Database already contains data. Skipping sample data creation.")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
