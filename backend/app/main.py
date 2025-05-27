import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.database import engine, get_db
from app.models import Base, User, UserLike  # Import models to ensure tables are created
from app.api.api import api_router
from app.config import settings

# This will be called when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables (in a real app, use migrations like Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up resources when the app shuts down
    await engine.dispose()

app = FastAPI(
    title="Kuma AI Prompt Manager API",
    description="API for managing AI prompts with categories and tags",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Kuma AI Prompt Manager API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
