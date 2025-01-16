from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

MOUNT_PATH = "/mnt/storage"

class FileRequest(BaseModel):
    filename: str
    content: str

@app.post("/write")
def write_file(request: FileRequest):
    file_path = os.path.join(MOUNT_PATH, request.filename)
    try:
        with open(file_path, "w") as file:
            file.write(request.content)
        return {"message": "File written successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read/{filename}")
def read_file(filename: str):
    file_path = os.path.join(MOUNT_PATH, filename)
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return {"filename": filename, "content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
