# Kuma AI Prompt Manager

A web application for managing and organizing AI prompts with categories and tags. This application allows users to create, read, update, and delete prompts, organize them into categories, and tag them for easy searching and filtering.

## Features

- **Prompt Management**: Create, read, update, and delete prompts
- **Categorization**: Organize prompts into categories
- **Tagging**: Add tags to prompts for better organization
- **AI-Powered Assistance**: Get AI-generated suggestions to improve your prompts
- **Smart Tagging**: Automatic tag suggestions based on prompt content
- **Search**: Full-text search across prompts
- **Duplicate Detection**: Automatically detects similar prompts to prevent duplicates
- **RESTful API**: Built with FastAPI for the backend
- **Modern Frontend**: Built with React and TypeScript
- De-duplication of similar prompts
- Search and filter functionality

## AI Features

Kuma AI Prompt Manager includes powerful AI capabilities to enhance your prompt management experience:

### AI-Powered Prompt Enhancement
- Get AI-generated suggestions to improve your prompts
- Automatically refine and optimize your prompts for better results
- Receive alternative phrasings and improvements

### Smart Tagging System
- AI suggests relevant tags based on prompt content
- One-click application of suggested tags
- Helps maintain consistent tagging across your prompt library

### How to Use AI Features
1. While creating or editing a prompt, click the "AI Assistant" button
2. Enter your initial prompt and click "Get AI Suggestions"
3. Review the improved prompt and suggestions
4. Click "Apply Suggestion" to apply the improved prompt and suggested tags
5. Edit further if needed before saving

### Requirements
- Backend server must be running
- Internet connection (for AI API calls)
- Google AI API key (for AI features) - add to your `.env` file

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy (ORM)
- SQLite (development) / PostgreSQL (production)
- Pydantic (data validation)
- TheFuzz (duplicate detection)

### Frontend (coming soon)
- React
- TypeScript
- Material-UI
- React Query

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- pip (Python package manager)
- npm or yarn (for frontend)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-prompt-manager.git
   cd ai-prompt-manager/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file if needed
   ```

5. Initialize the database:
   ```bash
   python init_db.py
   ```

6. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

The backend API will be available at `http://localhost:8000`

### Frontend Setup (coming soon)

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend server is running, you can access:

- Interactive API docs: http://localhost:8000/api/docs
- Alternative API docs: http://localhost:8000/api/redoc

## Project Structure

```
ai-prompt-manager/
├── backend/               # Backend API server
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   └── schemas/      # Pydantic models
│   ├── tests/            # Backend tests
│   ├── .env              # Environment variables
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
└── frontend/             # Frontend React app (coming soon)
    ├── public/          # Static files
    └── src/              # React components
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest -v --cov=app --cov-report=term-missing
```

### Frontend Tests (coming soon)

```bash
cd frontend
npm test
```

## Deployment

### Backend

The backend can be deployed to any WSGI/ASGI server. Here's an example using Gunicorn with Uvicorn workers:

```bash
pip install gunicorn
cd backend
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b :8000 main:app
```

For production, you should:
1. Set `DEBUG=False` in your environment variables
2. Use a production-ready database like PostgreSQL
3. Set up proper CORS settings
4. Configure HTTPS
5. Set up proper logging and monitoring

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - The ORM used
- [React](https://reactjs.org/) - The frontend library (coming soon)
- [Material-UI](https://material-ui.com/) - The UI component library (coming soon)
