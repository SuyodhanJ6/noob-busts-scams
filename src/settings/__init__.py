from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.entity.config_ent import AppConfig, DatabaseConfig, ModelConfig, MonitoringConfig

class Settings(BaseSettings):
    # API Settings
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Noob Busts Scams"
    
    # CORS
    ALLOWED_ORIGINS: str = "*"
    
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
    
    @property
    def get_app_config(self) -> AppConfig:
        """Get application configuration using entity models"""
        return AppConfig(
            debug=self.DEBUG,
            api_v1_prefix=self.API_V1_PREFIX,
            project_name=self.PROJECT_NAME,
            allowed_origins=self.CORS_ORIGINS,
            model_config=ModelConfig(
                model_name=self.GROQ_MODEL,
                temperature=0.1
            ),
            db_config=DatabaseConfig(
                url=self.DATABASE_URL
            ),
            monitoring_config=MonitoringConfig(
                comet_api_key=self.COMET_API_KEY,
                comet_workspace=self.COMET_WORKSPACE,
                comet_project=self.COMET_PROJECT_NAME
            )
        )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Using direct settings
db_url = settings.DATABASE_URL
origins = settings.CORS_ORIGINS

# Using entity-based config
app_config = settings.get_app_config
model_name = app_config.model_config.model_name
db_config = app_config.db_config