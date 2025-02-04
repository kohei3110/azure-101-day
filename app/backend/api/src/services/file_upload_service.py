import logging
import shutil
from pathlib import Path
from fastapi import UploadFile

class FileUploadService:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def upload_file(self, file: UploadFile, sub_dir: str) -> str:
        target_dir: Path = self.base_dir / sub_dir
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
        save_path: Path = target_dir / file.filename
        try:
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logging.error(e)
            raise Exception(e)
        return file.filename