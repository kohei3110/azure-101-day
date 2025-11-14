import os
import logging
from pathlib import Path
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from controller import router as api_router
from tracing.tracing import tracer
from di.containers import Container

# Determine environment (defaults to 'production')
ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("ENV", "production")).lower()

# Configure logging based on environment
if ENVIRONMENT in ("development", "dev", "local"):
    # Development mode: Detailed debug logging with more context
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info(f"Running in {ENVIRONMENT} mode with DEBUG logging enabled")
else:
    # Production mode: Only INFO and above
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info(f"Running in {ENVIRONMENT} mode with INFO logging enabled")

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
    container.wire(modules=["controller"])

    app = FastAPI()
    app.include_router(api_router)

    return app