from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv
from src.utils.file_utils import save_upload_file
from src.utils.task_manager import TaskStatus, get_task, set_task
from src.models.response_models import ScriptResponse
from src.services.script_generation import run_langgraph_task

# Load environment variables
load_dotenv()

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://scriptai-taupe.vercel.app"
]

# Create temp directory if it doesn't exist

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
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

API_KEY = os.getenv("HEADER_API_KEY", "changeme")
API_KEY_HEADER = "X-API-KEY"

def verify_api_key(request: Request):
    api_key = request.headers.get(API_KEY_HEADER)
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(
    topic: str = Form(...),
    tones: List[str] = Form(["professional"]),
    file_name: Optional[UploadFile] = File(None),
    platform: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    _: None = Depends(verify_api_key)
):
    task_id = str(uuid.uuid4())
    set_task(task_id, {
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None
    })
    base_template_path = "template_scripts/"
    file_path = base_template_path + ("script-template-en.docx" if platform == "youtube" else "short-script-en.docx")
    if file_name:
        file_path = await save_upload_file(file_name)
    background_tasks.add_task(run_langgraph_task, task_id, topic, tones, file_path, platform)

    return ScriptResponse(
        task_id=task_id,
        status=TaskStatus.PENDING
    )

@app.get("/task/{task_id}", response_model=ScriptResponse)
async def get_task_status(task_id: str, _: None = Depends(verify_api_key)):
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
async def download_script(task_id: str, _: None = Depends(verify_api_key)):
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
async def health_check(_: None = Depends(verify_api_key)):
    return {"status": "healthy"}
