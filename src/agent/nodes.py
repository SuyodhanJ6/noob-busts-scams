from typing import Dict, List, Annotated, TypeVar, cast
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import Graph, StateGraph, END
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.tools import get_available_tools
from src.logger import logger
from src.settings import settings
from langchain_core.tools import tool
from typing import Optional

from src.database.crud import ScamCRUD
from src.components.text_processor import validate_phone_number

class AgentState(BaseModel):
    """State maintained between agent steps"""
    messages: List[BaseMessage] = Field(default_factory=list)
    current_step: str = Field(default="START")
    scratchpad: Dict = Field(default_factory=dict)
    tool_output: Dict = Field(default_factory=dict)
    error: str = Field(default="")

class ScamAgentGraph:
    """LangGraph-based Scam Detection Agent"""
    
    def __init__(self):
        self.tools = get_available_tools()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Graph:
        """Build the agent's workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("search_scam", self._search_scam)
        workflow.add_node("register_scam", self._register_scam)
        workflow.add_node("analyze_scam", self._analyze_scam)
        workflow.add_node("format_response", self._format_response)
        
        # Add conditional edges with proper routing
        workflow.add_conditional_edges(
            "classify_intent",
            lambda x: "search_scam" if self._should_search(x) else
                     "register_scam" if self._should_register(x) else
                     "analyze_scam",
            {
                "search_scam": "search_scam",
                "register_scam": "register_scam",
                "analyze_scam": "analyze_scam"
            }
        )
        
        # Connect all operation nodes to response formatter
        workflow.add_edge("search_scam", "format_response")
        workflow.add_edge("register_scam", "format_response")
        workflow.add_edge("analyze_scam", "format_response")
        
        # Add edge from format_response to END
        workflow.add_edge("format_response", END)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        return workflow.compile()
    
    async def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent using LLM"""
        try:
            last_message = state.messages[-1].content
            # Use LLM to classify intent
            intent = await self._analyze_with_llm(last_message)
            state.scratchpad["intent"] = intent
            return state
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            state.error = str(e)
            return state
    
    async def _search_scam(self, state: AgentState) -> AgentState:
        """Execute scam search"""
        try:
            search_tool = next(t for t in self.tools if t.name == "scam_search")
            phone_number = state.scratchpad["intent"].get("phone_number")
            result = await search_tool._arun(phone_number=phone_number)
            state.tool_output["search"] = result
            return state
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            state.error = str(e)
            return state
    
    async def _register_scam(self, state: AgentState) -> AgentState:
        """Execute scam registration"""
        try:
            register_tool = next(t for t in self.tools if t.name == "scam_register")
            intent_data = state.scratchpad["intent"]
            result = await register_tool._arun(**intent_data)
            state.tool_output["register"] = result
            return state
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            state.error = str(e)
            return state
    
    async def _analyze_scam(self, state: AgentState) -> AgentState:
        """Execute scam analysis"""
        try:
            analyze_tool = next(t for t in self.tools if t.name == "scam_analyze")
            text = state.messages[-1].content
            result = await analyze_tool._arun(text=text)
            state.tool_output["analyze"] = result
            return state
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            state.error = str(e)
            return state
    
    async def _format_response(self, state: AgentState) -> AgentState:
        """Format the final response"""
        try:
            if state.error:
                response = f"An error occurred: {state.error}"
            elif "search" in state.tool_output:
                result = state.tool_output["search"]
                response = self._format_search_response(result)
            elif "register" in state.tool_output:
                result = state.tool_output["register"]
                response = self._format_register_response(result)
            elif "analyze" in state.tool_output:
                result = state.tool_output["analyze"]
                response = self._format_analyze_response(result)
            else:
                response = "I couldn't process your request. Please try again."
                
            state.messages.append(AIMessage(content=response))
            return state
        except Exception as e:
            logger.error(f"Response formatting error: {str(e)}")
            state.error = str(e)
            return state
    
    def _should_search(self, state: AgentState) -> bool:
        """Determine if search is needed"""
        return state.scratchpad.get("intent", {}).get("action") == "search"
    
    def _should_register(self, state: AgentState) -> bool:
        """Determine if registration is needed"""
        return state.scratchpad.get("intent", {}).get("action") == "register"
    
    def _should_analyze(self, state: AgentState) -> bool:
        """Determine if analysis is needed"""
        return state.scratchpad.get("intent", {}).get("action") == "analyze"
    
    async def _analyze_with_llm(self, message: str) -> Dict:
        """Analyze message using LLM to determine intent"""
        # Implement LLM analysis here
        # For now, returning mock implementation
        if "search" in message.lower():
            return {"action": "search", "phone_number": self._extract_phone(message)}
        elif "register" in message.lower():
            return {"action": "register", "phone_number": self._extract_phone(message)}
        else:
            return {"action": "analyze"}
    
    def _extract_phone(self, message: str) -> str:
        """Extract phone number from message"""
        # Implement phone extraction logic
        # For now, returning mock implementation
        import re
        pattern = r'\+\d{1,3}-\d{6,14}'
        match = re.search(pattern, message)
        return match.group(0) if match else ""
    
    def _format_search_response(self, result: Dict) -> str:
        """Format search results into response"""
        if not result.get("success"):
            return f"Search failed: {result.get('error')}"
        data = result.get("data", {})
        return f"Found {data.get('report_count', 0)} reports for {data.get('phone_number')}"
    
    def _format_register_response(self, result: Dict) -> str:
        """Format registration result into response"""
        if not result.get("success"):
            return f"Registration failed: {result.get('error')}"
        return "Scam report registered successfully"
    
    def _format_analyze_response(self, result: Dict) -> str:
        """Format analysis result into response"""
        if not result.get("success"):
            return f"Analysis failed: {result.get('error')}"
        data = result.get("data", {}).get("analysis", {})
        return f"Analysis: {data.get('scam_type')} (Confidence: {data.get('confidence')})"

scam_crud = ScamCRUD()

@tool
async def register_scam(
    scammer_phone: str,
    description: str,
    reporter_phone: Optional[str] = None,
    reporter_email: Optional[str] = None,
    scam_type: Optional[str] = None
) -> str:
    """
    Register a new scam report.
    
    Args:
        scammer_phone: Phone number of the alleged scammer
        description: Description of the scam
        reporter_phone: Optional reporter's phone number
        reporter_email: Optional reporter's email
        scam_type: Optional type of scam
        
    Returns:
        Confirmation message
    """
    # Validate phone number
    scammer_phone = validate_phone_number(scammer_phone)
    if reporter_phone:
        reporter_phone = validate_phone_number(reporter_phone)
        
    try:
        await scam_crud.create_scam_report(
            scammer_phone=scammer_phone,
            description=description,
            reporter_phone=reporter_phone,
            reporter_email=reporter_email,
            scam_type=scam_type
        )
        return f"Successfully registered scam report for {scammer_phone}"
    except Exception as e:
        return f"Failed to register scam: {str(e)}"

@tool
async def search_scam(phone_number: str) -> str:
    """
    Search for existing scam reports for a phone number.
    
    Args:
        phone_number: Phone number to search
        
    Returns:
        Search results message
    """
    try:
        phone_number = validate_phone_number(phone_number)
        reports = await scam_crud.get_scam_reports(phone_number)
        
        if not reports:
            return f"No scam reports found for {phone_number}"
            
        return f"Found {len(reports)} scam reports for {phone_number}"
    except Exception as e:
        return f"Error searching for scam reports: {str(e)}"
