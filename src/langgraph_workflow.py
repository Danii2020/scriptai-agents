from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from src.nodes.research import research_node
from src.nodes.screenwrite import screenwrite_node

# Define the state schema
class WorkflowState(TypedDict):
    """
    Represents the state of the YouTube script workflow.
    """
    topic: str
    tones: str
    file_path: str
    current_year: str
    research_results: str
    final_script: str
    platform: str
    needs_more_research: bool  # New field to control iterative research

def run_youtube_script_workflow(
    topic: str,
    tones: str,
    file_path: str,
    current_year: str = None,
    platform: str = "YouTube",
    return_state: bool = False,
) -> dict:
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
    workflow = StateGraph(WorkflowState)
    workflow.add_node("research", research_node)
    workflow.add_node("screenwrite", screenwrite_node)
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "screenwrite")

    # Router function for conditional edge
    def screenwrite_router(state):
        # If the screenwriter signals more research is needed, go to research, else END
        if state.get("needs_more_research", False):
            return "research"
        return END

    workflow.add_conditional_edges("screenwrite", screenwrite_router, path_map=["research", END])

    graph = workflow.compile()
    initial_state = {
        "topic": topic,
        "tones": tones,
        "file_path": file_path,
        "current_year": current_year or '2025',
        "research_results": "",
        "final_script": "",
        "platform": platform,
        "needs_more_research": False  # Start with no extra research needed
    }
    result = graph.invoke(initial_state)
    if return_state:
        return result
    return result.get("final_script", "No script generated")