from typing import Dict, Tuple
from zenml import step
from zenml.integrations.groq.model_deployers import GroqModelDeployer

from src.components.text_processor import TextProcessor
from src.components.scam_analyzer import ScamAnalyzer
from src.entity.artifact_ent import ScamReportArtifact

@step
def preprocess_text(text: str) -> str:
    """Preprocess and clean the input text"""
    processor = TextProcessor()
    return processor.clean_text(text)

@step(enable_cache=False)
def analyze_scam_type(
    text: str,
    model_name: str
) -> Dict[str, float]:
    """Analyze text to determine scam type"""
    analyzer = ScamAnalyzer(model_name=model_name)
    return analyzer.analyze(text)

@step
def validate_analysis(
    analysis: Dict[str, float]
) -> Tuple[str, float]:
    """Validate the analysis results"""
    # Get the highest confidence prediction
    scam_type = max(analysis.items(), key=lambda x: x[1])
    return scam_type

@step
def store_results(
    results: Tuple[str, float]
) -> ScamReportArtifact:
    """Store the analysis results"""
    scam_type, confidence = results
    return ScamReportArtifact(
        scam_type=scam_type,
        confidence_score=confidence
    )
