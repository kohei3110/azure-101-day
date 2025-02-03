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
    code_interpreter_service: CodeInterpreterService = Depends(
        Provide[Container.code_interpreter_service]
    )
):
    with tracer.start_as_current_span("post_dynamic_sessions") as parent:
        parent.set_attributes(
            {
                "span_type": "GenAI",
                "gen_ai.operation.name": "chat",
                "gen_ai.system": "_OTHER",
                "gen_ai.request.model": "phi4",
            }
        )
        user_message = message
        code = await code_interpreter_service.process_message_only(file, user_message)
        if code.startswith("```") and code.endswith("```"):
            code = code[3:-3].strip()
            if code.startswith("python"):
                code = code[6:].strip()
        credential = DefaultAzureCredential()
        token = credential.get_token("https://dynamicsessions.io/.default")
        access_token = token.token
        print(f"Access token: {access_token}")
        REGION = os.getenv("REGION", "eastasia")
        SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
        RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
        ACA_DYNAMICSESSIONS_POOL_NAME = os.getenv(
            "ACA_DYNAMICSESSIONS_POOL_NAME", "pool-azure101day-demo-ce-001"
        )
        url = (
            f"https://{REGION}.dynamicsessions.io/subscriptions/{SUBSCRIPTION_ID}"
            f"/resourceGroups/{RESOURCE_GROUP}/sessionPools/{ACA_DYNAMICSESSIONS_POOL_NAME}"
        )

        session_id = str(uuid.uuid4())

        try:
            # Upload the file
            requests.post(
                url + f"/files/upload?api-version=2024-02-02-preview&identifier={session_id}",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                files={
                    "file": (file.filename, file.file, "application/octet-stream")
                }
            )
            file_path_pattern = r'/mnt/data/assistant-[\w-]+'
            file_path_replacement = f'/mnt/data/{file.filename}'
            code = re.sub(file_path_pattern, file_path_replacement, code)
            print(f"Code: {code}")
            # Execute the code
            requests.post(
                url + f"/code/execute?api-version=2024-02-02-preview&identifier={session_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "properties": {
                        "codeInputType": "inline",
                        "executionType": "synchronous",
                        "code": code
                    }
                }
            )
            return {"session_id": session_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))