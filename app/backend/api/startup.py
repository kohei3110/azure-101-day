import os
import logging
from pathlib import Path
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from controller import router as api_router
from tracing.tracing import tracer
from containers import Container

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
    container.wire(modules=["api.controller"])

    app = FastAPI()

    @app.on_event("startup")
    async def startup_event():
        # 必要な初期化処理をここに追加
        pass

    @app.on_event("shutdown")
    async def shutdown_event():
        # 必要なクリーンアップ処理をここに追加
        pass

    app.include_router(api_router)

    return app