"""
Scam Detection Graph using LangGraph for agent orchestration.
"""

from typing import Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import (
    RunnableConfig,
    RunnableLambda,
    RunnableSerializable,
)
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from src.agent.nodes import register_scam, search_scam
from src.settings import settings

# Initialize LLM
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    temperature=settings.TEMPERATURE,
    streaming=False
)

# Define available tools
tools = [register_scam, search_scam]

# System instructions for the agent
SYSTEM_INSTRUCTIONS = """
You are a scam detection and reporting assistant. Your role is to:
1. Help users report potential scams
2. Search for reported scammer phone numbers
3. Provide guidance on avoiding scams

Guidelines:
- Always verify phone numbers are in international format (+XX-XXXXXXXXXX)
- Collect necessary details before registering a scam
- Be concise and clear in your responses
- Maintain user privacy and data security
"""

class AgentState(MessagesState, total=False):
    """State management for the agent conversation."""
    metadata: Dict[str, Any]

def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    """
    Wraps the LLM with tools and system instructions.
    
    Args:
        model: Base chat model to wrap
        
    Returns:
        Wrapped model with tools and instructions
    """
    model_with_tools = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=SYSTEM_INSTRUCTIONS)] + state["messages"],
        name="StatePreprocessor",
    )
    return preprocessor | model_with_tools

async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Asynchronously processes messages through the model.
    
    Args:
        state: Current agent state
        config: Runtime configuration
        
    Returns:
        Updated agent state
    """
    model_runnable = wrap_model(llm)
    response = await model_runnable.ainvoke(state, config)
    return {"messages": [response]}

def create_scam_detection_graph() -> StateGraph:
    """
    Create and compile the scam detection graph.
    
    Returns:
        Compiled StateGraph instance
    """
    # Build the graph
    agent = StateGraph(AgentState)

    # Add nodes
    agent.add_node("model", acall_model)
    agent.add_node("tools", ToolNode(tools))

    # Set entry point
    agent.set_entry_point("model")

    # Add edges
    agent.add_edge("model", "tools")
    agent.add_edge("tools", END)

    # Compile the graph
    return agent.compile(checkpointer=MemorySaver())

def create_agent_state(metadata: Dict[str, Any] = None) -> AgentState:
    """
    Create a new agent state with optional metadata.
    
    Args:
        metadata: Optional metadata for the state
        
    Returns:
        Initialized AgentState instance
    """
    return AgentState(metadata=metadata or {})

# Initialize the cyber_guard using the graph creation function
cyber_guard = create_scam_detection_graph() 