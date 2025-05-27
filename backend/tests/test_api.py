import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
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

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Create test client
app = create_application()
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Prompt Manager API"}

def test_create_and_read_category():
    # Create a category
    category_data = {"name": "Test Category", "description": "Test Description"}
    response = client.post("/api/categories/", json=category_data)
    assert response.status_code == 201
    category = response.json()
    assert category["name"] == category_data["name"]
    assert category["description"] == category_data["description"]
    category_id = category["id"]
    
    # Read the category
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["id"] == category_id

def test_create_and_read_prompt():
    # First create a category
    category_data = {"name": "Prompt Test Category"}
    response = client.post("/api/categories/", json=category_data)
    category_id = response.json()["id"]
    
    # Create a prompt
    prompt_data = {
        "title": "Test Prompt",
        "content": "This is a test prompt",
        "category_id": category_id,
        "tag_names": ["test", "example"]
    }
    response = client.post("/api/prompts/", json=prompt_data)
    assert response.status_code == 201
    prompt = response.json()
    assert prompt["title"] == prompt_data["title"]
    assert prompt["content"] == prompt_data["content"]
    assert len(prompt["tags"]) == 2
    
    # Read the prompt
    response = client.get(f"/api/prompts/{prompt['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == prompt["id"]

def test_duplicate_prompt_detection():
    # First create a category
    category_data = {"name": "Duplicate Test Category"}
    response = client.post("/api/categories/", json=category_data)
    category_id = response.json()["id"]
    
    # Create first prompt
    prompt_data = {
        "title": "Unique Prompt",
        "content": "This is a unique prompt",
        "category_id": category_id
    }
    response = client.post("/api/prompts/", json=prompt_data)
    assert response.status_code == 201
    
    # Try to create a very similar prompt
    similar_prompt = prompt_data.copy()
    similar_prompt["title"] = "Slightly different title"
    similar_prompt["content"] = "This is a unique prompt with minor changes"
    
    response = client.post("/api/prompts/", json=similar_prompt)
    assert response.status_code == 400
    assert "similar_prompt_id" in response.json()["detail"]
    assert "similarity" in response.json()["detail"]

def test_search_prompts():
    # First create a category
    category_data = {"name": "Search Test Category"}
    response = client.post("/api/categories/", json=category_data)
    category_id = response.json()["id"]
    
    # Create test prompts
    prompts = [
        {"title": "Search Test 1", "content": "This is about machine learning", "category_id": category_id},
        {"title": "Search Test 2", "content": "This is about data science", "category_id": category_id},
        {"title": "Another Test", "content": "This is about artificial intelligence", "category_id": category_id}
    ]
    
    for prompt in prompts:
        response = client.post("/api/prompts/", json=prompt)
        assert response.status_code == 201
    
    # Search for prompts
    response = client.get("/api/prompts/?search=machine")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert "machine" in results[0]["content"].lower() or "machine" in results[0]["title"].lower()

# Clean up after tests
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    # Clean up test database after tests
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("test.db")
    except:
        pass
