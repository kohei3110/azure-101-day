from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from services.code_interpreter_service import CodeInterpreterService
from utils.file_handler import FileHandler
from startup import code_interpreter_service

router = APIRouter()

def get_file_handler():
    return FileHandler()

@router.post("/code_interpreter")
async def post_code_interpreter(
    file: UploadFile = File(...), 
    message: str = Form(...),
    file_handler: FileHandler = Depends(get_file_handler),
    code_interpreter_service: CodeInterpreterService = Depends(lambda: code_interpreter_service)
):
    user_message = message
    file_name = await code_interpreter_service.process_code_interpreter(file, user_message, file_handler)
    return FileResponse(path=file_name, filename=file_name)