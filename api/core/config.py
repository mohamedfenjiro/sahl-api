from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
import os
import secrets

class Settings(BaseSettings):
    # File storage settings
    FILE_PATH: str = "/data/files"
    
    # API security
    API_KEY: str = Field(default_factory=lambda: os.environ.get("API_KEY", secrets.token_urlsafe(32)))
    
    # Supabase settings
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    
    # JWT settings
    JWT_SECRET: str = Field(default_factory=lambda: os.environ.get("JWT_SECRET", secrets.token_urlsafe(32)))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: list[str] = [
        "https://sahlfinancial.com",
        "https://app.sahlfinancial.com",
        "https://sahl-api-sandbox.onrender.com",
        "http://localhost:8080"
    ]
    
    # Environment settings
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

settings = Settings()