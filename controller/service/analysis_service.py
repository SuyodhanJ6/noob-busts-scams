from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

from controller.service import BaseService
from src.components.scam_analyzer import ScamAnalyzer
from src.monitoring.opik import LLMMonitoring
from src.settings import settings
from src.logger import logger
router = APIRouter(prefix="/analysis", tags=["analysis"])

class AnalysisRequest(BaseModel):
    text: str
    metadata: dict = {}

class AnalysisResponse(BaseModel):
    scam_type: str
    confidence: float
    analysis_time: float
    token_usage: dict

@router.post("/analyze")
async def analyze_text(request: AnalysisRequest):
    """Analyze text for scam detection"""
    try:
        start_time = time.time()
        
        # Initialize components
        analyzer = ScamAnalyzer(
            model_name=settings.GROQ_MODEL,
            temperature=0.1
        )
        monitor = LLMMonitoring(settings.get_app_config.monitoring_config)
        
        # Analyze text
        analysis = await analyzer.analyze_scam(request.text)
        
        # Calculate metrics
        duration = time.time() - start_time
        token_usage = analyzer.get_token_usage()
        
        # Log to monitoring
        monitor.log_llm_request(
            prompt=request.text,
            completion=str(analysis),
            model=settings.GROQ_MODEL,
            tokens=token_usage,
            duration=duration,
            metadata=request.metadata
        )
        
        return AnalysisResponse(
            scam_type=analysis["scam_type"],
            confidence=analysis["confidence"],
            analysis_time=duration,
            token_usage=token_usage
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """Get analysis metrics"""
    monitor = LLMMonitoring(settings.get_app_config.monitoring_config)
    return {
        "total_requests": monitor.experiment.get_metric("total_requests"),
        "avg_response_time": monitor.experiment.get_metric("avg_response_time"),
        "token_usage": monitor.experiment.get_metric("total_tokens")
    } 