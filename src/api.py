from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from typing import Optional, List
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from src.utils.file_utils import save_upload_file, TEMP_DIR
from src.services.script_generation import stream_langgraph_task
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://scriptai-taupe.vercel.app",
    "https://www.scriptioo.com",
    "https://scriptioo.com"
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

# Initialize the rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No global default
    storage_uri="memory://"
)

# Add the rate limiter middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Rate limit exceeded. Please try again later."}
))

def verify_api_key(request: Request):
    api_key = request.headers.get(API_KEY_HEADER)
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/generate-script")
@limiter.limit("10/minute;block=30 minutes")
async def generate_script(
    request: Request,
    topic: str = Form(...),
    tones: List[str] = Form(["professional"]),
    file_name: Optional[UploadFile] = File(None),
    platform: str = Form(...),
    _: None = Depends(verify_api_key)
):
    base_template_path = "template_scripts/"
    file_path = base_template_path + ("script-template-en.docx" if platform == "YouTube" else "short-script-en.docx")
    if file_name:
        file_path = await save_upload_file(file_name)

    async def event_stream():
        async for event in stream_langgraph_task(topic, tones, file_path, platform):
            print(json.dumps(event))
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/download-script")
async def download_script(
    file_path: str = Query(..., description="Path to the script file (from SSE event)"),
    _: None = Depends(verify_api_key)
):
    """
    Download a generated script file.
    
    The file_path should be obtained from the 'file_path' field in the 'completed' 
    SSE event from /generate-script endpoint.
    """
    # Validate that the file path is in the temp directory (security check)
    try:
        file_path_obj = Path(file_path).resolve()
        temp_dir_obj = Path(TEMP_DIR).resolve()
        
        # Ensure the file is within the temp directory
        if not str(file_path_obj).startswith(str(temp_dir_obj)):
            raise HTTPException(
                status_code=403, 
                detail="Invalid file path. File must be in the temporary directory."
            )
        
        # Check if file exists
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="Script file not found")
        
        # Check if it's a .docx file
        if file_path_obj.suffix.lower() != '.docx':
            raise HTTPException(status_code=400, detail="Invalid file type. Only .docx files are allowed.")
        
        # Extract filename for download
        filename = file_path_obj.name
        
        return FileResponse(
            path=str(file_path_obj),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error accessing file: {str(e)}")

@app.get("/health")
async def health_check(_: None = Depends(verify_api_key)):
    return {"status": "healthy"}
