from typing import List
from langchain_core.tools import BaseTool

from src.tools.search_tool import ScamSearchTool
from src.tools.register_tool import ScamRegisterTool
from src.tools.analyze_tool import ScamAnalyzeTool

def get_available_tools() -> List[BaseTool]:
    """Get all available tools"""
    return [
        ScamSearchTool(),
        ScamRegisterTool(),
        ScamAnalyzeTool()
    ] 