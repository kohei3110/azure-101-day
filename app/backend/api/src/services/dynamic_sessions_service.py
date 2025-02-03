import uuid
import re
from repositories.dynamic_sessions_repository import DynamicSessionsRepository

class DynamicSessionsService:
    def __init__(self, repository: DynamicSessionsRepository):
        self.repository = repository

    def process_dynamic_session(self, file, code: str) -> str:
        session_id = str(uuid.uuid4())
        self.repository.upload_file(session_id, file)
        file_path_pattern = r'/mnt/data/assistant-[\w-]+'
        file_path_replacement = f'/mnt/data/{file.filename}'
        code = re.sub(file_path_pattern, file_path_replacement, code)
        self.repository.execute_code(session_id, code)
        return session_id