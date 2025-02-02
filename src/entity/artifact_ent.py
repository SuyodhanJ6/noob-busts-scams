from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ScamReportArtifact:
    scammer_mobile: str
    scam_type: str
    description: str
    reporter_id: str
    created_at: datetime
    confidence_score: float
    model_version: str
    
@dataclass
class ModelArtifact:
    model_id: str
    version: str
    metrics: dict
    created_at: datetime
    parameters: dict
    
@dataclass
class PipelineArtifact:
    pipeline_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    artifacts: list[ScamReportArtifact]
