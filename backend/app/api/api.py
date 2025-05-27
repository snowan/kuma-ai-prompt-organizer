from fastapi import APIRouter

from app.api.endpoints import prompts, categories, tags, auth, likes
from app.api.ai import router as ai_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(likes.router, prefix="", tags=["likes"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
