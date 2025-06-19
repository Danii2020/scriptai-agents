import asyncio
import os
from src.crew_project.utils.task_manager import update_task, TaskStatus
from src.crew_project.utils.file_utils import create_script_docx
from src.crew_project.langgraph_workflow import run_youtube_script_workflow

async def run_langgraph_task(task_id: str, topic: str, tones: list, file_path: str):
    try:
        update_task(task_id, {"status": TaskStatus.RUNNING})
        script_content = await asyncio.to_thread(
            run_youtube_script_workflow,
            topic=topic,
            tones=", ".join(tones),
            file_path=file_path,
            current_year=None
        )
        docx_path = create_script_docx(script_content, topic)
        update_task(task_id, {
            "status": TaskStatus.COMPLETED,
            "result": script_content,
            "file_path": docx_path
        })
    except Exception as e:
        update_task(task_id, {
            "status": TaskStatus.FAILED,
            "error": str(e)
        })
    finally:
        if file_path and file_path != "/Users/danielerazo/Documents/yt-scripts/script-template-en.docx":
            try:
                os.remove(file_path)
            except:
                pass 