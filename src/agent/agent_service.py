from typing import Dict, Any, Optional
from pydantic import BaseModel

from src.logger import logger
from src.agent.scam_detection_graph import create_scam_detection_graph, create_agent_state

class AgentService:
    """Service for handling agent interactions"""
    
    def __init__(self):
        self.graph = create_scam_detection_graph()
    
    async def process_chat(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a chat message through the agent graph
        
        Args:
            message: The user's message
            metadata: Optional metadata for the request
            
        Returns:
            Dict containing the agent's response
        """
        try:
            # Create initial state
            state = create_agent_state(
                message=message,
                metadata=metadata or {}
            )
            
            # Process through graph
            result = await self.graph.ainvoke(state)
            
            return {
                "success": True,
                "data": result,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Agent processing failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
