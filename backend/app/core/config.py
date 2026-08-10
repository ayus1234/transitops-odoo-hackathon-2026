"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""
import os
from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "TransitOps"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    _raw_db_url: str = os.getenv("DATABASE_URL", "sqlite:////tmp/transitops.db")
    DATABASE_URL: str = _raw_db_url.replace("ssl_context=true", "sslmode=require").replace("ssl_context=false", "sslmode=disable").replace("ssl_context=", "sslmode=") if "ssl_context" in _raw_db_url else _raw_db_url
    DATABASE_ECHO: bool = False
    
    # JWT Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: Any = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://transitops-ui.vercel.app",
        "https://transitops-api-psi.vercel.app"
    ]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
        
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql://", 1)
            if v.startswith("postgresql://") and not v.startswith("postgresql+"):
                v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v


# Create global settings instance
settings = Settings()
