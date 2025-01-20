import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from services.code_interpreter_service import CodeInterpreterService
from utils.file_handler import FileHandler
from startup import code_interpreter_service
from tracing.tracing import tracer

router = APIRouter()

def get_file_handler():
    return FileHandler()

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
FILE_DIR = Path(os.getenv("FILE_DIR", "/files"))

@router.post("/data")
async def upload_data(file: UploadFile = File(...)):
    """Upload a file to the data directory."""
    with tracer.start_as_current_span("upload_data"):
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        save_path = DATA_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}

@router.post("/files")
async def upload_files(file: UploadFile = File(...)):
    """Upload a file to the data directory."""
    with tracer.start_as_current_span("upload_files"):
        if not FILE_DIR.exists():
            FILE_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FILE_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}

@router.post("/code_interpreter")
async def post_code_interpreter(
    file: UploadFile = File(...), 
    message: str = Form(...),
    file_handler: FileHandler = Depends(get_file_handler),
    code_interpreter_service: CodeInterpreterService = Depends(lambda: code_interpreter_service)
):
    with tracer.start_as_current_span("post_code_interpreter") as parent:
        parent.set_attributes(
            {
                "span_type": "GenAI",
                "inputs": {
                    "messages": [
                        {
                            "content": message
                        }
                    ]
                },
                "gen_ai.operation.name": "chat",
                "gen_ai.system": "az.ai.inference",
                "gen_ai.request.model": "gpt-4o",

            }
        )
        user_message = message
        file_name = await code_interpreter_service.process_code_interpreter(file, user_message, file_handler)
        return FileResponse(path=file_name, filename=file_name)