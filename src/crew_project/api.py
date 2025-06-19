from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv
from src.crew_project.utils.file_utils import save_upload_file
from src.crew_project.utils.task_manager import tasks, TaskStatus, get_task, set_task
from src.crew_project.models.response_models import ScriptResponse
from src.crew_project.services.script_generation import run_langgraph_task

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

@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(
    topic: str = Form(...),
    tones: List[str] = Form(["professional"]),
    file_name: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    task_id = str(uuid.uuid4())
    set_task(task_id, {
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None
    })

    file_path = "/Users/danielerazo/Documents/yt-scripts/script-template-en.docx"
    if file_name:
        file_path = await save_upload_file(file_name)
    background_tasks.add_task(run_langgraph_task, task_id, topic, tones, file_path)

    return ScriptResponse(
        task_id=task_id,
        status=TaskStatus.PENDING
    )

@app.get("/task/{task_id}", response_model=ScriptResponse)
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return ScriptResponse(
        task_id=task_id,
        status=task["status"],
        result=task["result"],
        error=task["error"],
        file_path=task.get("file_path")
    )

@app.get("/download-script/{task_id}")
async def download_script(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != TaskStatus.COMPLETED or not task.get("file_path"):
        raise HTTPException(status_code=400, detail="Script not ready for download")
    file_path = task["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Script file not found")
    return FileResponse(
        path=file_path,
        filename=f"script_{task_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
