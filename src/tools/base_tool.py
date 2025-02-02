"""
Base tool implementation for scam detection tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

from src.database.db_session import get_db, get_async_session
from src.monitoring.opik import LLMMonitoring

class ToolResponse(BaseModel):
    """Standard response format for tools."""
    
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BaseScamTool(ABC):
    """Base class for all scam detection tools."""
    
    def __init__(self, monitoring: Optional[LLMMonitoring] = None):
        self.monitoring = monitoring
        self._db = None
        self._async_db = None
    
    @property
    def db(self):
        """Get synchronous database session."""
        if not self._db:
            self._db = next(get_db())
        return self._db
    
    async def get_async_db(self):
        """Get asynchronous database session."""
        if not self._async_db:
            self._async_db = await anext(get_async_session())
        return self._async_db
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """
        Execute the tool's main functionality.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResponse containing the result
        """
        pass
    
    def log_execution(self, input_data: Dict[str, Any], output: ToolResponse):
        """
        Log tool execution if monitoring is enabled.
        
        Args:
            input_data: Tool input parameters
            output: Tool execution result
        """
        if self.monitoring:
            self.monitoring.log_tool_execution(
                tool_name=self.__class__.__name__,
                input_data=input_data,
                output_data=output.dict(),
                success=output.success
            )