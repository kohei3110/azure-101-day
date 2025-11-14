import logging
import shutil
from pathlib import Path
from fastapi import UploadFile

class FileUploadService:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def upload_file(self, file: UploadFile, sub_dir: str) -> str:
        target_dir: Path = self.base_dir / sub_dir
        logging.debug(f"Uploading file {file.filename} to {target_dir}")
        if not target_dir.exists():
            logging.debug(f"Creating directory: {target_dir}")
            target_dir.mkdir(parents=True, exist_ok=True)
        save_path: Path = target_dir / file.filename
        try:
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logging.debug(f"File saved successfully to: {save_path}")
        except Exception as e:
            logging.error(f"Error saving file to {save_path}: {e}")
            raise Exception(e)
        return file.filename