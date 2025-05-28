from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from .crew import YouTubeScript
import uuid
from enum import Enum
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(
    title="YouTube Script Generator API",
    description="API for generating YouTube scripts using CrewAI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# In-memory task store
tasks = {}

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ScriptRequest(BaseModel):
    topic: str
    tones: List[str] = ["professional"]  # Default to professional tone
    additional_context: Optional[Dict[str, Any]] = None

class ScriptResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None

async def run_crew_task(task_id: str, topic: str, tones: List[str]):
    try:
        tasks[task_id]["status"] = TaskStatus.RUNNING
        crew_instance = YouTubeScript().crew()
        result = await crew_instance.kickoff_async(inputs={
            "topic": topic, 
            "current_year": str(datetime.now().year),
            "tones": ", ".join(tones)  # Join tones into a comma-separated string
        })
        tasks[task_id].update({
            "status": TaskStatus.COMPLETED,
            "result": result.tasks_output[1].raw
        })
    except Exception as e:
        tasks[task_id].update({
            "status": TaskStatus.FAILED,
            "error": str(e)
        })

@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None
    }
    
    background_tasks.add_task(run_crew_task, task_id, request.topic, request.tones)
    
    return ScriptResponse(
        task_id=task_id,
        status=TaskStatus.PENDING
    )

@app.get("/task/{task_id}", response_model=ScriptResponse)
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return ScriptResponse(
        task_id=task_id,
        status=task["status"],
        result=task["result"],
        error=task["error"]
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}