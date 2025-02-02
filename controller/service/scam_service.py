from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from src.components.scam_analyzer import ScamAnalyzer
from src.entity.artifact_ent import ScamReportArtifact
from src.monitoring.opik import log_prediction
from src.utils.validators import validate_phone_number

router = APIRouter(prefix="/scams", tags=["scams"])

class ScamReport(BaseModel):
    scammer_phone: str
    description: str
    reporter_email: EmailStr
    reporter_phone: Optional[str] = None

class ScamService(BaseService):
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.analyzer = ScamAnalyzer(config.model_config)

    @router.post("/report")
    @rate_limit(max_requests=100, window_seconds=3600)
    async def report_scam(self, report: ScamReport):
        """Report a new scam"""
        try:
            # Validate phone numbers
            scammer_phone = validate_phone_number(report.scammer_phone)
            if report.reporter_phone:
                reporter_phone = validate_phone_number(report.reporter_phone)
            
            # Analyze scam type and description
            analysis = await self.analyzer.analyze_scam(report.description)
            
            # Create artifact
            artifact = ScamReportArtifact(
                scammer_mobile=scammer_phone,
                scam_type=analysis.scam_type,
                description=analysis.processed_description,
                reporter_id=report.reporter_email,
                created_at=datetime.utcnow(),
                confidence_score=analysis.confidence,
                model_version=self.analyzer.model_version
            )
            
            # Log to monitoring
            log_prediction(
                input_text=report.description,
                prediction=analysis.scam_type,
                confidence=analysis.confidence
            )
            
            return {"status": "success", "report_id": artifact.id}
            
        except Exception as e:
            logger.error(f"Error processing scam report: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 