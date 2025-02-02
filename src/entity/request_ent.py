from dataclasses import dataclass
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="Message text to analyze")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ChatResponse(BaseModel):
    """Chat response model"""
    status: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")

@dataclass
class AnalysisRequest:
    text: str
    metadata: Dict[str, Any] = None

@dataclass
class ChatRequest:
    message: str
    metadata: Optional[Dict[str, Any]] = None 