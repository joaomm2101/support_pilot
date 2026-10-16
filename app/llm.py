"""The ONLY module that imports the OpenAI SDK.

Knows nothing about FastAPI. Exposes a small function that takes a question and
returns the answer plus token usage, so tests can replace it with a fake.
"""


import time
from dataclasses import dataclass
from functools import lru_cache

from openai import AsyncOpenAI, OpenAIError

from app.config import get_settings

SYSTEM_PROMPT = (
    "You are SupportPilot, a helpful assistant that helps developers "
    "with questions about FastAPI. Answer clearly and concisely, and provide code examples when relevant. "
    "If you are not sure about the answer, say so. Do not make up answers."
)

class LLMError(Exception):
    """Raised when the LLM call fails."""



@dataclass(frozen=True)
class LLMResult:
    answer: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float

@lru_cache
def get_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.llm_timeout_seconds)

async def ask_llm(question: str) -> LLMResult:
    settings = get_settings()
    client = get_client()

    start = time.perf_counter()
    try:
        response = await client.responses.create(
            model=settings.llm_model,
            instructions=SYSTEM_PROMPT,
            input=question,
        )
    except OpenAIError as exc:
        raise LLMError("LLM provider call failed") from exc

    
    latency_ms = (time.perf_counter() - start) * 1000

    return LLMResult(
        answer=response.output_text,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=latency_ms,
    )

