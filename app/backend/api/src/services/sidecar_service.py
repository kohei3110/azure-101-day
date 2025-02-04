import os
import requests

class SidecarService:
    def __init__(self):
        self.url = os.getenv("SIDECAR_SLM_URL", "http://localhost:11434/api/generate")

    def post_slm(self, prompt: str) -> dict:
        response = requests.post(
            self.url,
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()