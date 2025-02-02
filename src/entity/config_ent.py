from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    model_name: str
    temperature: float
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 5
    max_overflow: int = 10

@dataclass
class MonitoringConfig:
    comet_api_key: str
    comet_workspace: str
    comet_project: str
    enable_monitoring: bool = True

@dataclass
class AppConfig:
    debug: bool
    api_v1_prefix: str
    project_name: str
    allowed_origins: list[str]
    model_config: ModelConfig
    db_config: DatabaseConfig
    monitoring_config: MonitoringConfig
