from zenml import pipeline
from zenml.config import DockerSettings
from zenml.integrations.constants import GROQ

@pipeline(
    settings={
        "docker": DockerSettings(required_integrations=[GROQ])
    }
)
def scam_analysis_pipeline(
    text: str,
    model_name: str = "llama-3-70b",
):
    """Pipeline for analyzing scam reports"""
    # Import steps here to avoid circular imports
    from src.steps import (
        preprocess_text,
        analyze_scam_type,
        validate_analysis,
        store_results
    )
    
    # Execute pipeline steps
    cleaned_text = preprocess_text(text)
    analysis = analyze_scam_type(cleaned_text, model_name)
    validated_results = validate_analysis(analysis)
    final_results = store_results(validated_results)
    
    return final_results
