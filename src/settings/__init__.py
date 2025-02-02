"""
Application settings and configuration.
"""

from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # App Config
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Noob Busts Scams"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_VERSION: str = "0.0.1"
    CORS_ORIGINS: str = "*"
    # Security
    SECRET_KEY: str
    API_TOKEN: str
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str
    DB_NAME: str = "noob_busts_scams"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.7
    
    # Monitoring
    COMET_API_KEY: str
    COMET_PROJECT_NAME: str = "noob-busts-scams"
    COMET_WORKSPACE: str
    
    # ZenML
    ZENML_API_KEY: str
    ZENML_USERNAME: str
    
    # OPIK
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str
    
    # CORS
    ALLOWED_ORIGINS: str = "*"
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour in seconds
    
    # Monitoring Config
    MONITORING_CONFIG: Dict[str, Any] = {
        "comet_api_key": COMET_API_KEY,
        "comet_project_name": COMET_PROJECT_NAME,
        "comet_workspace": COMET_WORKSPACE,
    }
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct database URL from components.
        Using aiomysql for async MySQL support.
        """
        return (
            f"mysql+aiomysql://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Convert ALLOWED_ORIGINS string to list."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.ENVIRONMENT.lower() == "production"

    def get_app_config(self) -> Dict[str, Any]:
        """
        Return a dictionary of the application configuration.
        
        Returns:
            A dictionary containing key configuration details
        """
        return {
            "project_name": self.PROJECT_NAME,
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "api_prefix": self.API_V1_PREFIX,
            "allowed_hosts": self.ALLOWED_HOSTS,
            "monitoring_config": self.MONITORING_CONFIG,
        }

# Create settings instance
settings = Settings()