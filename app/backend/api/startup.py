import os
import logging
from pathlib import Path
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

import controller
from services.code_interpreter_service import CodeInterpreterService
from tracing.tracing import tracer
from .containers import Container

logging.basicConfig(
    level=logging.DEBUG
)

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

def create_app() -> FastAPI:
    container = Container()
    app = FastAPI()
    app.include_router(controller.router)
    return app

app = create_app()

project_client: AIProjectClient = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

code_interpreter_service = CodeInterpreterService(project_client)