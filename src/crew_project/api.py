from datetime import datetime
import shutil
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from .crew import YouTubeScript
import uuid
from enum import Enum
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Create temp directory if it doesn't exist
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

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

class ScriptResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save the uploaded file to a temporary location and return the path"""
    try:
        # Create a unique filename
        file_extension = Path(upload_file.filename).suffix
        if file_extension.lower() != '.docx':
            raise HTTPException(status_code=400, detail="Only .docx files are allowed")
            
        temp_file_path = TEMP_DIR / f"{uuid.uuid4()}{file_extension}"
        
        # Save the file
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return str(temp_file_path)
    finally:
        upload_file.file.close()

async def run_crew_task(task_id: str, topic: str, tones: List[str], file_path: Optional[str]):
    try:
        tasks[task_id]["status"] = TaskStatus.RUNNING
        crew_instance = YouTubeScript().crew()
        result = await crew_instance.kickoff_async(inputs={
            "topic": topic, 
            "current_year": str(datetime.now().year),
            "tones": ", ".join(tones),  # Join tones into a comma-separated string
            "file_path": file_path
        })
        tasks[task_id].update({
            "status": TaskStatus.COMPLETED,
            "result": result.tasks_output[1].raw
        })
    except Exception as e:
        breakpoint()
        tasks[task_id].update({
            "status": TaskStatus.FAILED,
            "error": str(e)
        })
    finally:
        # Clean up the temporary file if it exists and is not the default path
        if file_path and file_path != "/Users/danielerazo/Documents/yt-scripts/script-template-en.docx":
            try:
                os.remove(file_path)
            except:
                pass  # Ignore errors during cleanup

@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(
    topic: str = Form(...),
    tones: List[str] = Form(["professional"]),
    file_name: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None
    }

    file_path = "/Users/danielerazo/Documents/yt-scripts/script-template-en.docx"
    if file_name:
        file_path = await save_upload_file(file_name)
    background_tasks.add_task(run_crew_task, task_id, topic, tones, file_path)

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
