import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dependency_injector import containers, providers
from repositories.file_repository import FileRepository
from repositories.message_repository import MessageRepository
from services.code_interpreter_service import CodeInterpreterService
from services.file_upload_service import FileUploadService
from utils.file_handler import FileHandler

class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        modules=["controller"]
    )

    base_dir = providers.Singleton(Path, "/")

    ai_project_info = os.getenv("PROJECT_CONNECTION_STRING", "")
    endpoint, subscription_id, resource_group_name, project_name = ai_project_info.split(';')

    project_client = providers.Singleton(
        AIProjectClient,
        endpoint=f"https://{endpoint}",
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        project_name=project_name,
        credential=DefaultAzureCredential()
    )

    file_handler = providers.Factory(FileHandler)
    file_repository = providers.Factory(
        FileRepository,
        file_handler=file_handler
    )
    message_repository = providers.Factory(
        MessageRepository,
        project_client=project_client
    )

    code_interpreter_service = providers.Factory(
        CodeInterpreterService,
        project_client=project_client,
        file_repository=file_repository,
        message_repository=message_repository
    )
    file_upload_service = providers.Factory(
        FileUploadService,
        base_dir=base_dir
    )
    file_handler = providers.Factory(FileHandler)