import logging
import os
import re
import requests
import uuid
from pathlib import Path

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, UploadFile
)
from fastapi.responses import FileResponse

from di.containers import Container
from models.prompt_request import PromptRequest
from services.dynamic_sessions_service import DynamicSessionsService
from services.sidecar_service import SidecarService
from services.code_interpreter_service import CodeInterpreterService
from services.file_upload_service import FileUploadService
from tracing.tracing import tracer
from dependency_injector.wiring import inject, Provide

from azure.identity import DefaultAzureCredential

router = APIRouter()


DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
FILE_DIR = Path(os.getenv("FILE_DIR", "/files"))


@router.post("/data")
@inject
async def upload_data(
    file: UploadFile = File(...),
    file_upload_service: FileUploadService = Depends(
        Provide[Container.file_upload_service]
    )
):
    """Upload a file to the data directory."""
    try:
        with tracer.start_as_current_span("upload_data"):
            filename = file_upload_service.upload_file(file, "data")
            return {"filename": filename}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.post("/files")
@inject
async def upload_files(
    file: UploadFile = File(...),                   
    file_upload_service: FileUploadService = Depends(
        Provide[Container.file_upload_service]
    )
):
    """Upload a file to the data directory."""
    try:
        with tracer.start_as_current_span("upload_files"):
            filename = file_upload_service.upload_file(file, "files")
            return {"filename": filename}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Failed to upload file")
        

@router.post("/code_interpreter")
@inject
async def post_code_interpreter(
    file: UploadFile = File(...),
    message: str = Form(...),
    code_interpreter_service: CodeInterpreterService = Depends(
        Provide[Container.code_interpreter_service]
    )
):
    try:
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
            file_name = await code_interpreter_service.process_file_and_message(
                file, user_message
            )
            return FileResponse(path=file_name, filename=file_name)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Failed to interpret code")


@router.post("/slm")
@inject
def post_slm(
    request_data: PromptRequest,
    sidecar_service: SidecarService = Depends(
        Provide[Container.sidecar_service]
    )
):
    try:
        with tracer.start_as_current_span("post_slm") as parent:
            parent.set_attributes(
                {
                    "span_type": "GenAI",
                    "gen_ai.operation.name": "chat",
                    "gen_ai.system": "_OTHER",
                    "gen_ai.request.model": "phi4",
                }
            )
            result = sidecar_service.post_slm(request_data.prompt)
            return result
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Failed to generate text")
    

@router.post("/dynamic_sessions")
@inject
async def post_dynamic_sessions(
    file: UploadFile = File(...),
    message: str = Form(...),
    code_interpreter_service: CodeInterpreterService = Depends(Provide[Container.code_interpreter_service]),
    dynamic_sessions_service: DynamicSessionsService = Depends(Provide[Container.dynamic_sessions_service])
):
    try:
        with tracer.start_as_current_span("post_dynamic_sessions") as parent:
            parent.set_attributes(
                {
                    "span_type": "GenAI",
                    "gen_ai.operation.name": "chat",
                    "gen_ai.system": "_OTHER",
                    "gen_ai.request.model": "phi3",
                }
            )
            user_message = message
        code = await code_interpreter_service.process_message_only(file, user_message)
        session_id = dynamic_sessions_service.process_dynamic_session(file, code)
        return {"session_id": session_id}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Failed to process dynamic session")