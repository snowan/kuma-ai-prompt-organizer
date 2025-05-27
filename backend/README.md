# AI Prompt Manager - Backend

This is the backend service for the AI Prompt Manager application, built with FastAPI and SQLAlchemy.

## Features

- RESTful API for managing prompts, categories, and tags
- Duplicate prompt detection using fuzzy string matching
- Full-text search capabilities
- SQLite database (can be easily switched to PostgreSQL/MySQL)
- Automated testing with pytest

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the backend directory:
   ```
   cp .env.example .env
   ```
5. Initialize the database:
   ```
   python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

## Running the Application

To start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- Interactive API docs: http://localhost:8000/api/docs
- Alternative API docs: http://localhost:8000/api/redoc

## Running Tests

To run the test suite:

```bash
pytest -v --cov=app --cov-report=term-missing
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── prompts.py
│   │   │   ├── categories.py
│   │   │   └── tags.py
│   │   └── api.py
│   ├── crud.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── __init__.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .env
├── .gitignore
├── main.py
├── pytest.ini
└── requirements.txt
```

## API Endpoints

### Prompts

- `GET /api/prompts/` - List all prompts
- `POST /api/prompts/` - Create a new prompt
- `GET /api/prompts/{prompt_id}` - Get a specific prompt
- `PUT /api/prompts/{prompt_id}` - Update a prompt
- `DELETE /api/prompts/{prompt_id}` - Delete a prompt

### Categories

- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create a new category
- `GET /api/categories/{category_id}` - Get a specific category
- `PUT /api/categories/{category_id}` - Update a category
- `DELETE /api/categories/{category_id}` - Delete a category

### Tags

- `GET /api/tags/` - List all tags
- `GET /api/tags/{tag_id}` - Get a specific tag
- `DELETE /api/tags/{tag_id}` - Delete a tag

## Development

### Database Migrations

This project uses SQLAlchemy with SQLite for development. For production, you might want to use a more robust database like PostgreSQL. To switch databases, update the `DATABASE_URL` in your `.env` file.

### Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///./sql_app.db`)
- `SECRET_KEY`: Secret key for JWT token signing
- `ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 30)
- `DEBUG`: Enable debug mode (default: False)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
