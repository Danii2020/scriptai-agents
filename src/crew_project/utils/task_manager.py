from enum import Enum
from typing import Dict, Any

tasks: Dict[str, Dict[str, Any]] = {}

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

def get_task(task_id: str) -> Dict[str, Any]:
    return tasks.get(task_id)

def set_task(task_id: str, task_data: Dict[str, Any]):
    tasks[task_id] = task_data

def update_task(task_id: str, updates: Dict[str, Any]):
    if task_id in tasks:
        tasks[task_id].update(updates) 