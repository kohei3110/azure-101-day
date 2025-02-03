import os
import re
import uuid
import requests
from azure.identity import DefaultAzureCredential

class DynamicSessionsRepository:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.access_token = self._get_access_token()
        self.region = os.getenv("REGION", "eastasia")
        self.subscription_id = os.getenv("SUBSCRIPTION_ID")
        self.resource_group = os.getenv("RESOURCE_GROUP")
        self.pool_name = os.getenv("ACA_DYNAMICSESSIONS_POOL_NAME", "pool-azure101day-demo-ce-001")
        self.base_url = (
            f"https://{self.region}.dynamicsessions.io/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}/sessionPools/{self.pool_name}"
        )

    def _get_access_token(self) -> str:
        token = self.credential.get_token("https://dynamicsessions.io/.default")
        return token.token

    def upload_file(self, session_id: str, file) -> None:
        url = f"{self.base_url}/files/upload?api-version=2024-02-02-preview&identifier={session_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        files = {"file": (file.filename, file.file, "application/octet-stream")}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()  # 例外発生時は上位でキャッチ

    def execute_code(self, session_id: str, code: str) -> None:
        url = f"{self.base_url}/code/execute?api-version=2024-02-02-preview&identifier={session_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "properties": {
                "codeInputType": "inline",
                "executionType": "synchronous",
                "code": code
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()