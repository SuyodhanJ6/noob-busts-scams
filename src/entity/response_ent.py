from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from .artifact_ent import ScamReportArtifact

@dataclass
class ChatResponse:
    response: str
    metadata: Dict[str, Any] = None
    artifact: Optional[ScamReportArtifact] = None
    timestamp: datetime = datetime.utcnow()

@dataclass
class AnalysisResponse:
    is_scam: bool
    confidence_score: float
    scam_type: Optional[str] = None
    description: Optional[str] = None
    model_version: Optional[str] = None
    metadata: Dict[str, Any] = None 