from pydantic import BaseModel
from typing import Optional
from src.crew_project.utils.task_manager import TaskStatus

class ScriptResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    file_path: Optional[str] = None 