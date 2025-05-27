import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from main import create_application

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

# Dependency to override get_db in the app
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Create test client
@pytest.fixture(scope="module")
def client():
    app = create_application()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

# Fixture to get a test database session
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# Fixture to create a test category
@pytest.fixture(scope="function")
def test_category(client):
    category_data = {"name": "Test Category", "description": "Test Description"}
    response = client.post("/api/categories/", json=category_data)
    return response.json()

# Fixture to create a test prompt
@pytest.fixture(scope="function")
def test_prompt(client, test_category):
    prompt_data = {
        "title": "Test Prompt",
        "content": "This is a test prompt",
        "category_id": test_category["id"],
        "tag_names": ["test", "example"]
    }
    response = client.post("/api/prompts/", json=prompt_data)
    return response.json()
