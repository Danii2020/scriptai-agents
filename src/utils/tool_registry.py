from ..tools.docx_read_tool_langgraph import docx_read_tool_langgraph
from ..tools.notion_tool_langgraph import notion_create_page_langgraph
from langchain_tavily import TavilySearch

tavily_tool = TavilySearch(max_results=2)

def get_tools_for_agent(agent_key: str):
    if agent_key == 'researcher':
        return [tavily_tool] if tavily_tool else []
    if agent_key == 'screenwriter':
        return [docx_read_tool_langgraph]
    return [] 