from typing import Dict, Optional, ClassVar, Any
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun

from src.tools.base_tool import BaseScamTool, ToolResponse
from src.utils.validators import validate_phone_number, validate_description

class RegisterInput(BaseModel):
    """Input schema for register tool"""
    phone_number: str = Field(..., description="Scammer's phone number")
    scam_type: str = Field(..., description="Type of scam")
    description: str = Field(..., description="Description of the scam")
    confidence: float = Field(..., description="Confidence score of the report")
    reporter_id: Optional[int] = Field(None, description="ID of the reporter")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

class ScamRegisterTool(BaseScamTool):
    """Tool for registering new scam reports"""
    
    name: ClassVar[str] = "scam_register"
    description: ClassVar[str] = "Register a new scam report"
    args_schema: ClassVar[type] = RegisterInput
    
    async def _arun(
        self,
        phone_number: str,
        scam_type: str,
        description: str,
        confidence: float,
        reporter_id: Optional[int] = None,
        metadata: Dict = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> ToolResponse:
        """Async run of the register tool"""
        try:
            validated_number = validate_phone_number(phone_number)
            validated_description = validate_description(description)
            
            report_data = {
                "scammer_phone": validated_number,
                "scam_type": scam_type,
                "description": validated_description,
                "confidence_score": confidence,
                "reporter_id": reporter_id,
                **(metadata or {})
            }
            
            with self.get_db_manager() as db:
                new_report = await db.create_scam_report(report_data)
                
                return ToolResponse(
                    success=True,
                    data={
                        "report_id": new_report.id,
                        "status": "success",
                        "message": "Scam report registered successfully"
                    }
                )
            
        except Exception as e:
            return self._handle_error(e)