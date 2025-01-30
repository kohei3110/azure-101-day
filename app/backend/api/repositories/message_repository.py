from azure.ai.projects import AIProjectClient

class MessageRepository:
    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client

    def list_messages(self, thread_id: str):
        return self.project_client.agents.list_messages(thread_id=thread_id)