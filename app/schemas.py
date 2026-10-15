"""Pydantic request/response models for the API."""
from pydantic import BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=4000)

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float

class ChatResponse(BaseModel):
    answer: str
    model: str
    usage: Usage