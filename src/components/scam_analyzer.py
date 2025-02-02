from typing import Dict, Optional
from langchain_groq import ChatGroq
from src.constants import SCAM_TYPES, ANALYSIS_PROMPT

class ScamAnalyzer:
    """Component for analyzing scam reports"""
    
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.1
    ):
        self.model = ChatGroq(
            model_name=model_name,
            temperature=temperature
        )
        self.model_version = model_name
        
    async def analyze_scam(
        self,
        text: str
    ) -> Dict[str, float]:
        """Analyze text to determine scam type"""
        # Prepare prompt
        prompt = ANALYSIS_PROMPT.format(
            text=text,
            scam_types="\n".join(SCAM_TYPES)
        )
        
        # Get model prediction
        response = await self.model.apredict(prompt)
        
        # Parse response
        try:
            analysis = self._parse_response(response)
            return analysis
        except Exception as e:
            logger.error(f"Error parsing model response: {str(e)}")
            raise
            
    def _parse_response(
        self,
        response: str
    ) -> Dict[str, float]:
        """Parse model response into scam type and confidence"""
        # Implementation depends on model output format
        # This is a simplified example
        lines = response.strip().split("\n")
        result = {}
        
        for line in lines:
            if ":" in line:
                scam_type, confidence = line.split(":")
                result[scam_type.strip()] = float(confidence.strip())
                
        return result 