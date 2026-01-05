"""Configuration settings for the API"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
import os
import sys


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Musigo"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    PORT: int = 8000
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database (default to Postgres; override via env for local dev)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://musicuser:musicpass@postgres:5432/musicdb",
    )
    # For local dev fallback, you can use SQLite by setting env DATABASE_URL to:
    # sqlite+aiosqlite:///./music_discovery.db
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY is secure in production"""
        if not os.getenv("DEBUG", "true").lower() in {"1", "true", "yes"}:
            # Production mode
            if v == "your-secret-key-change-in-production":
                raise ValueError(
                    "SECURITY ERROR: SECRET_KEY must be changed in production! "
                    "Set a strong random value in your environment variables."
                )
            if len(v) < 32:
                raise ValueError(
                    "SECURITY ERROR: SECRET_KEY must be at least 32 characters long for production use."
                )
        return v
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    REQUIRE_CHROMA: bool = os.getenv("REQUIRE_CHROMA", "true").lower() in {"1", "true", "yes"}
    
    # OpenAI (optional for advanced features)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Spotify API (for music metadata)
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    # Redis (for caching and queues)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STORAGE: str = "memory://"  # Use "redis://localhost:6379/1" for distributed rate limiting
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".m4a", ".ogg"]
    
    # ML Models
    MODEL_DIR: str = "./models"
    
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # ignore unknown env vars (e.g., NEXT_PUBLIC_API_URL)
    )


settings = Settings()


def validate_production_config() -> List[str]:
    """
    Validate configuration for production readiness.
    Returns a list of warnings/errors.
    """
    warnings = []
    is_production = not settings.DEBUG
    
    if not is_production:
        return warnings  # Skip validation in development mode
    
    # Check SECRET_KEY
    if settings.SECRET_KEY == "your-secret-key-change-in-production":
        warnings.append("CRITICAL: SECRET_KEY is using default value. Set a strong random key!")
    elif len(settings.SECRET_KEY) < 32:
        warnings.append("WARNING: SECRET_KEY should be at least 32 characters long")
    
    # Check DATABASE_URL
    if "sqlite" in settings.DATABASE_URL.lower():
        warnings.append("WARNING: Using SQLite in production. Consider PostgreSQL for better performance and reliability.")
    
    # Check CORS origins
    if "*" in settings.CORS_ORIGINS or "localhost" in str(settings.CORS_ORIGINS):
        warnings.append("WARNING: CORS allows localhost. Update CORS_ORIGINS for production domains only.")
    
    # Check Spotify credentials (optional but recommended)
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
        warnings.append("INFO: Spotify API credentials not set. Some discovery features may be limited.")
    
    # Check Redis
    if "localhost" in settings.REDIS_URL:
        warnings.append("INFO: Redis URL points to localhost. Ensure Redis is accessible in production.")
    
    # Check rate limiting
    if settings.RATE_LIMIT_STORAGE == "memory://":
        warnings.append("WARNING: Rate limiting uses in-memory storage. Use Redis for multi-instance deployments.")
    
    return warnings


def print_config_validation():
    """Print configuration validation results"""
    warnings = validate_production_config()
    
    if warnings:
        print("\n" + "="*70)
        print("⚠️  CONFIGURATION WARNINGS")
        print("="*70)
        for warning in warnings:
            level = "❌" if "CRITICAL" in warning else "⚠️" if "WARNING" in warning else "ℹ️"
            print(f"{level} {warning}")
        print("="*70 + "\n")
        
        # Exit if critical errors in production
        if any("CRITICAL" in w for w in warnings):
            print("🛑 Critical configuration errors detected. Fix them before running in production.")
            sys.exit(1)
    else:
        print("✅ Configuration validation passed")
