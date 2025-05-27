import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from app.database import engine, get_db, SQLALCHEMY_DATABASE_URL, async_session_maker
from app.models import Base
from app.api.api import api_router

# This will be called when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables (in a real app, use migrations like Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up resources when the app shuts down
    await engine.dispose()

def create_application() -> FastAPI:
    app = FastAPI(
        title="AI Prompt Manager API",
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
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:58310"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Include API router
    app.include_router(api_router, prefix="/api")

    return app

app = create_application()

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Prompt Manager API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3002, reload=True)
