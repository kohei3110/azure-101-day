from typing import List, Optional
from azure.ai.projects.models import CodeInterpreterTool


def create_code_interpreter_tool(file_ids: Optional[List[str]] = None) -> CodeInterpreterTool:
    if file_ids is None or not file_ids:
        return CodeInterpreterTool()
    return CodeInterpreterTool(file_ids=file_ids)