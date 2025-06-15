import yaml
from pathlib import Path
from typing import Dict, Any
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from .tools.notion_tool import NotionTool
from .tools.docx_read_tool_langgraph import docx_read_tool_langgraph
from .tools.notion_tool_langgraph import notion_create_page_langgraph

# Define the state schema
class WorkflowState(TypedDict):
    """
    Represents the state of the YouTube script workflow.
    
    Attributes:
        topic: The topic for the script
        tones: The desired tones for the script
        file_path: Path to any reference file
        current_year: Current year for context
        research_results: Results from the research phase
        final_script: The completed script
    """
    topic: str
    tones: str
    file_path: str
    current_year: str
    research_results: str
    final_script: str

# Load agent and task configs
def load_yaml_config(path: str) -> dict:
    with open(Path(__file__).parent / path, 'r') as f:
        return yaml.safe_load(f)

AGENTS_CONFIG = load_yaml_config('config/agents.yaml')
TASKS_CONFIG = load_yaml_config('config/tasks.yaml')

def build_prompt(agent_key: str, input_vars: Dict[str, Any]) -> str:
    agent = AGENTS_CONFIG[agent_key]
    prompt = f"""
        Role: {agent['role']}
        Goal: {agent['goal']}
        Backstory: {agent['backstory']}
    """
    for k, v in input_vars.items():
        prompt = prompt.replace(f'{{{k}}}', str(v))
    return prompt

def build_task_prompt(task_key: str, input_vars: Dict[str, Any]) -> str:
    task = TASKS_CONFIG[task_key]
    prompt = f"""
        Task: {task['description']}
        Expected Output: {task['expected_output']}
    """
    for k, v in input_vars.items():
        prompt = prompt.replace(f'{{{k}}}', str(v))
    return prompt

# Define tools
tavily_tool = TavilySearch(max_results=2)

def get_tools_for_agent(agent_key: str):
    if agent_key == 'researcher':
        return [tavily_tool] if tavily_tool else []
    if agent_key == 'screenwriter':
        return [docx_read_tool_langgraph, notion_create_page_langgraph]
    return []

# Define node functions that work with the state
def research_node(state: WorkflowState) -> Dict[str, Any]:
    """Research node that performs research and updates the state."""
    print("---Research Node---")
    
    # Build the LLM with proper model format
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    # Build the prompt for research
    input_vars = {
        'topic': state['topic'],
        'tones': state['tones'],
        'file_path': state['file_path'],
        'current_year': state['current_year'],
    }
    
    researcher_prompt = build_prompt('researcher', input_vars) + '\n' + build_task_prompt('research_task', input_vars)
    
    # Create the researcher agent
    researcher_agent = create_react_agent(
        model=llm,
        tools=get_tools_for_agent('researcher'),
        prompt=researcher_prompt,
        name="ResearcherAgent"
    )
    
    # Invoke the researcher agent
    result = researcher_agent.invoke({"messages": [{"role": "user", "content": f"Research the topic: {state['topic']} with tones: {state['tones']}"}]})
    
    # Extract the research results
    if result and "messages" in result:
        research_results = result["messages"][-1].content if result["messages"] else "No research results"
    else:
        research_results = "No research results"
    
    return {"research_results": research_results}

def screenwrite_node(state: WorkflowState) -> Dict[str, Any]:
    """Screenwriting node that creates the final script."""
    print("---Screenwriting Node---")
    
    # Build the LLM with proper model format
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    # Build the prompt for screenwriting
    input_vars = {
        'topic': state['topic'],
        'tones': state['tones'],
        'file_path': state['file_path'],
        'current_year': state['current_year'],
        'research_results': state.get('research_results', ''),
    }
    
    screenwriter_prompt = build_prompt('screenwriter', input_vars) + '\n' + build_task_prompt('screenwriting_task', input_vars)
    
    # Create the screenwriter agent
    screenwriter_agent = create_react_agent(
        model=llm,
        tools=get_tools_for_agent('screenwriter'),
        prompt=screenwriter_prompt,
        name="ScreenwriterAgent"
    )
    
    # Create the message content including research results
    message_content = f"""
    Create a YouTube script for the topic: {state['topic']}
    Desired tones: {state['tones']}
    Research results: {state.get('research_results', 'No research available')}
    File path for reference: {state['file_path']}
    """
    
    # Invoke the screenwriter agent
    result = screenwriter_agent.invoke({"messages": [{"role": "user", "content": message_content}]})
    
    # Extract the final script
    if result and "messages" in result:
        final_script = result["messages"][-1].content if result["messages"] else "No script generated"
    else:
        final_script = "No script generated"
    
    return {"final_script": final_script}

def run_youtube_script_workflow(topic: str, tones: str, file_path: str, current_year: str = None) -> str:
    """
    Run the YouTube script workflow.
    
    Args:
        topic: The topic for the script
        tones: The desired tones for the script
        file_path: Path to any reference file
        current_year: Current year for context
        
    Returns:
        The final generated script
    """
    # Build workflow graph with proper state schema
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("screenwrite", screenwrite_node)
    
    # Add edges
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "screenwrite")
    workflow.add_edge("screenwrite", END)
    
    # Compile the workflow
    graph = workflow.compile()
    
    # Prepare initial state
    initial_state = {
        "topic": topic,
        "tones": tones,
        "file_path": file_path,
        "current_year": current_year or '2025',
        "research_results": "",
        "final_script": ""
    }
    
    # Run the workflow
    result = graph.invoke(initial_state)
    
    # Return the final script
    return result.get("final_script", "No script generated")