"""Application configuration using Pydantic Settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import secrets

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./smart_email.db"
    
    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # AI Config
    GEMINI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-2.5-flash"
    CONFIDENCE_THRESHOLD: int = 85

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), "..", ".env"), env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()
