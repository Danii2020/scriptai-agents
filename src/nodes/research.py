from langchain_openai import ChatOpenAI
from ..utils.prompt_builders import build_prompt, build_task_prompt
from ..utils.tool_registry import get_tools_for_agent
from ..utils.config_loader import load_yaml_config
from pathlib import Path
from src.utils.model_constants import AI_MODEL

AGENTS_CONFIG = load_yaml_config('config/agents.yaml')
TASKS_CONFIG = load_yaml_config('config/tasks.yaml')

def research_node(state):
    """Research node that performs research and updates the state."""
    print("---Research Node---")
    llm = ChatOpenAI(model=AI_MODEL)
    input_vars = {
        'topic': state['topic'],
        'tones': state['tones'],
        'file_path': state['file_path'],
        'current_year': state['current_year'],
    }
    researcher_prompt = build_prompt(AGENTS_CONFIG['researcher'], input_vars) + '\n' + build_task_prompt(TASKS_CONFIG['research_task'], input_vars)
    from langgraph.prebuilt import create_react_agent
    researcher_agent = create_react_agent(
        model=llm,
        tools=get_tools_for_agent('researcher'),
        prompt=researcher_prompt,
        name="ResearcherAgent"
    )
    result = researcher_agent.invoke({"messages": [{"role": "user", "content": f"Research the topic: {state['topic']} with tones: {state['tones']}"}]})
    if result and "messages" in result:
        research_results = result["messages"][-1].content if result["messages"] else "No research results"
    else:
        research_results = "No research results"
    return {"research_results": research_results} 