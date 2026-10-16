"""FastAPI app and the POST /chat route.

Thin layer: parse the request, call the service/llm layer, return the response.
No business logic here.
"""


from fastapi import FastAPI, HTTPException

from app.llm import LLMError, ask_llm
from app.observability import calculate_cost_usd, log_usage
from app.schemas import ChatRequest, ChatResponse, Usage

app = FastAPI(title="SupportPilot")

@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Ask the LLM a question and return the answer."""
    try:
        result = await ask_llm(request.question)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail="The language model failed to respond.") from exc

    cost_usd = calculate_cost_usd(result.input_tokens, result.output_tokens)
    log_usage(request.question, result, cost_usd)

    return ChatResponse(
        answer=result.answer,
        model=result.model,
        usage=Usage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=cost_usd,
            latency_ms=result.latency_ms,
        ),
    )