from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dependency_injector import containers, providers
from services.code_interpreter_service import CodeInterpreterService
from services.file_upload_service import FileUploadService
from utils.file_handler import FileHandler

class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=["controller"]
    )

    base_dir = providers.Singleton(Path, "/")
    project_client = providers.Singleton(AIProjectClient, credential=DefaultAzureCredential())

    code_interpreter_service = providers.Factory(
        CodeInterpreterService,
        project_client=project_client
    )
    file_upload_service = providers.Factory(
        FileUploadService,
        base_dir=base_dir
    )
    file_handler = providers.Factory(FileHandler)