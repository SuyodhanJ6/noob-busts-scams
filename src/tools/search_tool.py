from typing import Dict, List, Optional, ClassVar, Any
from pydantic import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from sqlalchemy import select

from src.tools.base_tool import BaseScamTool, ToolResponse
from src.utils.validators import validate_phone_number
from src.database.models import ScamReport

class SearchInput(BaseModel):
    """Input schema for search tool"""
    phone_number: str = Field(..., description="Phone number to search for")
    include_details: bool = Field(default=True, description="Include detailed reports")

class ScamSearchTool(BaseScamTool):
    """Tool for searching scam reports"""
    
    name: ClassVar[str] = "scam_search"
    description: ClassVar[str] = "Search for reported scams by phone number"
    args_schema: ClassVar[type] = SearchInput
    
    async def execute(self, **kwargs) -> ToolResponse:
        """
        Search for scam reports.
        
        Args:
            phone_number: Phone number to search
            
        Returns:
            ToolResponse containing search results
        """
        phone_number = kwargs.get("phone_number")
        if not phone_number:
            return ToolResponse(
                success=False,
                message="Phone number is required",
                error="missing_parameter"
            )
            
        try:
            db = await self.get_async_db()
            query = select(ScamReport).where(
                ScamReport.scammer_phone == phone_number
            ).order_by(ScamReport.created_at.desc())
            
            result = await db.execute(query)
            reports = result.scalars().all()
            
            response = ToolResponse(
                success=True,
                message=f"Found {len(reports)} reports for {phone_number}",
                data={"reports": [report.__dict__ for report in reports]}
            )
            
            self.log_execution(kwargs, response)
            return response
            
        except Exception as e:
            error_response = ToolResponse(
                success=False,
                message=f"Error searching for scam reports: {str(e)}",
                error="search_error"
            )
            self.log_execution(kwargs, error_response)
            return error_response
    
    def _get_dominant_scam_type(self, reports: List[Dict]) -> str:
        """Get the most common scam type from reports"""
        if not reports:
            return "UNKNOWN"
        
        type_counts = {}
        for report in reports:
            scam_type = report.get("scam_type", "UNKNOWN")
            type_counts[scam_type] = type_counts.get(scam_type, 0) + 1
            
        return max(type_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence(self, reports: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not reports:
            return 0.0
            
        total_confidence = sum(report.get("confidence", 0) for report in reports)
        return total_confidence / len(reports)