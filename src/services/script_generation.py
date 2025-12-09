import asyncio
import os
from src.utils.file_utils import create_script_docx
from src.langgraph_workflow import run_youtube_script_workflow


async def stream_langgraph_task(topic: str, tones: list, file_path: str, platform: str):
    """
    Async generator that streams workflow progress and results as SSE-friendly events.
    """
    yield {"status": "started"}
    try:
        state = await asyncio.to_thread(
            run_youtube_script_workflow,
            topic=topic,
            tones=", ".join(tones),
            file_path=file_path,
            current_year=None,
            platform=platform,
            return_state=True,
        )

        # Emit research results once available
        research_results = state.get("research_results", "")
        if research_results:
            yield {"status": "research_completed", "research_results": research_results}

        final_script = state.get("final_script", "No script generated")
        docx_path = create_script_docx(final_script, topic)

        yield {
            "status": "completed",
            "final_script": final_script,
            "file_path": docx_path,
        }
    except Exception as e:
        yield {"status": "failed", "error": str(e)}
    finally:
        if file_path and file_path != "template_scripts/script-template-en.docx":
            try:
                os.remove(file_path)
            except Exception:
                # Silently ignore cleanup errors
                pass