from typing import List, Optional
from azure.ai.projects.models import CodeInterpreterTool


def create_code_interpreter_tool(file_ids: List[str]) -> CodeInterpreterTool:
    return CodeInterpreterTool(file_ids=file_ids)