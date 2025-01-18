import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from apscheduler.schedulers.background import BackgroundScheduler

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.sample")

app = FastAPI()

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
FILE_DIR = Path(os.getenv("FILE_DIR", "/files"))

def delete_files():
    """Delete all files in the data directory."""
    for file in DATA_DIR.iterdir():
        if file.is_file():
            print(f"Deleting {file}")
            os.remove(file)

scheduler = BackgroundScheduler()
scheduler.add_job(delete_files, 'interval', seconds=30)
scheduler.start()

@app.post("/data")
async def upload_data(file: UploadFile = File(...)):
    """Upload a file to the data directory."""
    with tracer.start_as_current_span("upload_data"):
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        save_path = DATA_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}

@app.post("/files")
async def upload_files(file: UploadFile = File(...)):
    """Upload a file to the data directory."""
    with tracer.start_as_current_span("upload_files"):
        if not FILE_DIR.exists():
            FILE_DIR.mkdir(parents=True, exist_ok=True)
        save_path = FILE_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}