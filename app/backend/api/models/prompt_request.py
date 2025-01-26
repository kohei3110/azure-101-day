from pydantic import BaseModel


class PromptRequest(BaseModel):
    """
    Request model for SLM prompt.
    """
    prompt: str