from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Kuma AI Prompt Manager"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # External APIs
    GOOGLE_AI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = 'allow'  # Allow extra fields in environment variables

# Create settings instance
settings = Settings()
