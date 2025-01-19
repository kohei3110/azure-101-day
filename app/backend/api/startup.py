import os
import logging
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from apscheduler.schedulers.background import BackgroundScheduler

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

from services.code_interpreter_service import CodeInterpreterService
from .tracing import tracer

logging.basicConfig(
    level=logging.DEBUG
)

app = FastAPI()

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))

def delete_files():
    """Delete all files in the data directory."""
    with tracer.start_as_current_span("delete_files"):
        for file in DATA_DIR.iterdir():
            if file.is_file():
                print(f"Deleting {file}")
                os.remove(file)

scheduler = BackgroundScheduler()
scheduler.add_job(delete_files, 'interval', seconds=30)
scheduler.start()

project_client: AIProjectClient = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

code_interpreter_service = CodeInterpreterService(project_client)

import controller
app.include_router(controller.router)