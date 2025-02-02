"""
Analysis Service for handling chat and scam detection functionality.
"""

from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.agent.scam_detection_graph import cyber_guard
from src.database.crud import ScamCRUD
from src.entity.request_ent import ChatRequest
from src.entity.response_ent import ChatResponse
from src.monitoring.opik import LLMMonitoring
from src.settings import settings
from src.components.text_processor import rate_limiter, infer_chat_message

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"]
)

class AnalysisService:
    def __init__(self, monitoring: Optional[LLMMonitoring] = None):
        self.monitoring = monitoring
        self.scam_crud = ScamCRUD()

    async def process_chat(
        self, 
        chat_request: ChatRequest,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ChatResponse:
        """
        Process chat messages through the scam detection graph.
        
        Args:
            chat_request: The chat request containing the user message
            thread_id: Optional thread ID for conversation continuity
            metadata: Optional metadata for the chat
            
        Returns:
            ChatResponse containing the AI's response
        """
        try:
            # Prepare the input for the cyber guard
            kwargs = {
                "input": {
                    "messages": [HumanMessage(content=chat_request.message)]
                },
                "config": RunnableConfig(
                    configurable={
                        "thread_id": thread_id,
                        "metadata": metadata or {}
                    }
                )
            }

            # Process through the cyber guard
            response = await cyber_guard.ainvoke(**kwargs)
            
            # Extract the last message
            last_message = infer_chat_message(response["messages"][-1])
            
            # Log to monitoring if enabled
            if self.monitoring:
                self.monitoring.log_interaction(
                    input_text=chat_request.message,
                    output_text=last_message.content,
                    metadata=metadata
                )

            return ChatResponse(
                message=last_message.content,
                message_type=last_message.type,
                thread_id=thread_id,
                metadata=response.get("metadata", {})
            )

        except Exception as e:
            if settings.DEBUG:
                raise HTTPException(
                    status_code=500,
                    detail=f"Chat processing error: {str(e)}"
                )
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your request"
            )

# Initialize service
analysis_service = AnalysisService()

@router.post("/chat", response_model=ChatResponse)
@rate_limiter
async def chat_endpoint(
    request: ChatRequest,
    thread_id: Optional[str] = None,
) -> ChatResponse:
    """
    Main chat endpoint for scam detection and analysis.
    
    Args:
        request: The chat request containing the user message
        thread_id: Optional thread ID for conversation continuity
        
    Returns:
        ChatResponse containing the AI's response
    """
    return await analysis_service.process_chat(
        chat_request=request,
        thread_id=thread_id,
        metadata=request.metadata
    )

@router.post("/analyze")
async def analyze_number(phone_number: str) -> Dict:
    """
    Analyze a phone number for potential scam history.
    
    Args:
        phone_number: The phone number to analyze
        
    Returns:
        Dict containing analysis results
    """
    try:
        results = await analysis_service.scam_crud.get_scam_reports(phone_number)
        return {
            "phone_number": phone_number,
            "scam_count": len(results),
            "is_reported": len(results) > 0,
            "last_reported": results[-1].created_at if results else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing phone number: {str(e)}"
        ) 