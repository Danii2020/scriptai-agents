from langchain_openai import ChatOpenAI
from ..utils.prompt_builders import build_prompt, build_task_prompt
from ..utils.tool_registry import get_tools_for_agent
from ..utils.config_loader import load_yaml_config
from src.utils.model_constants import AI_MODEL

AGENTS_CONFIG = load_yaml_config('config/agents.yaml')
TASKS_CONFIG = load_yaml_config('config/tasks.yaml')

def screenwrite_node(state):
    """Screenwriting node that creates the final script."""
    print("---Screenwriting Node---")
    llm = ChatOpenAI(model=AI_MODEL)
    input_vars = {
        'topic': state['topic'],
        'tones': state['tones'],
        'file_path': state['file_path'],
        'current_year': state['current_year'],
        'research_results': state.get('research_results', ''),
    }
    screenwriter_prompt = build_prompt(AGENTS_CONFIG['screenwriter'], input_vars) + '\n' + build_task_prompt(TASKS_CONFIG['screenwriting_task'], input_vars)
    from langgraph.prebuilt import create_react_agent
    screenwriter_agent = create_react_agent(
        model=llm,
        tools=get_tools_for_agent('screenwriter'),
        prompt=screenwriter_prompt,
        name="ScreenwriterAgent"
    )
    message_content = f"""
    Create a YouTube script for the topic: {state['topic']}
    Desired tones: {state['tones']}
    Research results: {state.get('research_results', 'No research available')}
    File path for reference: {state['file_path']}
    """
    result = screenwriter_agent.invoke({"messages": [{"role": "user", "content": message_content}]})
    if result and "messages" in result:
        final_script = result["messages"][-1].content if result["messages"] else "No script generated"
    else:
        final_script = "No script generated"
    return {"final_script": final_script} 