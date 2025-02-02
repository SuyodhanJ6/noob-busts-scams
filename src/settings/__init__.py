from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Settings
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Noob Busts Scams"
    
    # CORS
    ALLOWED_ORIGINS: str = "*"  # Changed to str to match .env
    
    # Security
    SECRET_KEY: str
    API_TOKEN: str
    
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # Redis
    REDIS_URL: str
    
    # LLM
    GROQ_API_KEY: str
    GROQ_MODEL: str
    
    # Monitoring
    COMET_API_KEY: str
    COMET_PROJECT_NAME: str
    COMET_WORKSPACE: str
    
    # ZenML
    ZENML_API_KEY: str
    ZENML_USERNAME: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return self.ALLOWED_ORIGINS.split(",")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()