from typing import Dict, Optional
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from src.constants import SCAM_TYPES, ANALYSIS_PROMPT
from src.settings import settings
from src.logger import logger

class ScamAnalyzer:
    """Component for analyzing scam reports"""
    
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.1
    ):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.model = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=model_name,
            temperature=temperature,
            max_tokens=1024
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

    async def analyze_message(self, message: str) -> str:
        """
        Analyze a message for potential scam indicators using Langchain's Groq integration
        """
        try:
            # Create the prompt for scam analysis
            prompt = f"""
            Analyze the following message or phone number for potential scam indicators:
            
            Message: {message}
            
            Please provide a detailed analysis including:
            1. Whether this appears to be a potential scam
            2. Any red flags or warning signs
            3. Recommended actions
            """
            
            # Create message for Langchain
            messages = [HumanMessage(content=prompt)]
            
            # Get response from the model
            response = await self.model.ainvoke(messages)
            
            return response.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to analyze message: {str(e)}") 