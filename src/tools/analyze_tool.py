from typing import Dict, Optional, ClassVar, Any
from pydantic import BaseModel, Field, PrivateAttr
from langchain_core.callbacks import CallbackManagerForToolRun

from src.tools.base_tool import BaseScamTool, ToolResponse
from src.components.scam_analyzer import ScamAnalyzer
from src.settings import settings

class AnalyzeInput(BaseModel):
    """Input schema for analyze tool"""
    text: str = Field(..., description="Text to analyze")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

class ScamAnalyzeTool(BaseScamTool):
    """Tool for analyzing potential scams"""
    
    name: ClassVar[str] = "scam_analyze"
    description: ClassVar[str] = "Analyze text for potential scams"
    args_schema: ClassVar[type] = AnalyzeInput
    
    # Use PrivateAttr for non-serializable instances
    _analyzer: ScamAnalyzer = PrivateAttr()
    
    def __init__(self, **data):
        super().__init__(**data)
        self._analyzer = ScamAnalyzer(
            model_name=settings.GROQ_MODEL,
            temperature=0.1
        )
    
    async def _arun(
        self,
        text: str,
        metadata: Dict = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> ToolResponse:
        """Async run of the analyze tool"""
        try:
            analysis = await self._analyzer.analyze_scam(text)
            token_usage = self._analyzer.get_token_usage()
            
            return ToolResponse(
                success=True,
                data={
                    "analysis": analysis,
                    "token_usage": token_usage,
                    "metadata": metadata
                }
            )
            
        except Exception as e:
            return self._handle_error(e)