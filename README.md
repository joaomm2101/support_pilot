# SupportPilot

A developer-support assistant that answers questions about the FastAPI documentation, built step by step to learn RAG, tool calling, evaluation and observability by hand (no LangChain at first).

## Status

**v0 done: baseline chat endpoint.** The API answers questions with a plain LLM call and reports tokens, estimated cost and latency for every request. **Next: RAG over the FastAPI docs (v1).**

## Architecture

```
POST /chat  { "question": "..." }
    │
    ▼
app/main.py            validate request (schemas.py)
    │
    ▼
app/llm.py             call the LLM, measure latency, read token usage
    │
    ▼
app/observability.py   estimate cost, append a line to logs/usage.jsonl
    │
    ▼
response  { "answer", "model", "usage": { input_tokens, output_tokens, cost_usd, latency_ms } }
```

| File | Role |
|---|---|
| `app/main.py` | FastAPI app, `POST /chat` and `GET /health`. Thin: no business logic. |
| `app/config.py` | Settings read from the environment (`.env`); fails at startup if a required value is missing. |
| `app/llm.py` | The only module that imports the OpenAI SDK. Returns the answer plus usage. |
| `app/observability.py` | Cost calculation and the JSONL usage log. |
| `app/schemas.py` | Pydantic request/response models. |
| `tests/` | pytest suite that uses a fake LLM, so no test calls the real API. |
| `docs/decisions.md` | Longer record of design decisions. |

## Design decisions

- **LLM isolated in one module.** Only `llm.py` knows the provider, so it can be swapped or faked without touching the routes.
- **OpenAI Responses API.** It is the current API for new projects and returns token usage directly.
- **Configuration from the environment.** Keys, model name and prices live in `.env` (gitignored), never in code; a blank `.env.example` documents what is needed.
- **The log stores the question length, not the question.** Usage data is useful for cost analysis without keeping user text on disk.
- **Provider errors become a 502.** Internal failures are not leaked to the client; the route returns a generic message.
- **uv for dependencies.** Fast, reproducible installs from a lock file.
- **Tests use a fake LLM.** They are fast, free and deterministic, and they cover the endpoint behaviour rather than the model.

## How to run

```bash
uv sync
cp .env.example .env        # then fill in your API key, model and prices
uv run uvicorn app.main:app --reload
uv run pytest
```

Try it:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I declare a query parameter in FastAPI?"}'
```

## Baseline numbers

Measured from `logs/usage.jsonl` with the plain LLM (no documentation, no retrieval). This is the reference point to compare against once RAG is added.

| Metric | Value |
|---|---|
| Requests measured | 2 |
| Model | `gpt-6-luna` |
| Average input tokens | 66.5 |
| Average output tokens | 25.5 |
| Average cost per question | about $0.000019 |
| Typical latency | about 3.2 s (3.08 s to 3.22 s) |

Caveat: this is a sample of two short questions (about 30 characters each), so treat it as an order of magnitude, not a benchmark. It will be re-measured on a larger question set in the evaluation step (v3).

## Limitations

- It does not use the FastAPI documentation yet, so answers come from the model's own training data and may be outdated.
- It can invent answers; the prompt asks it not to, but nothing verifies the output.
- No conversation memory: every request is independent.
- No sources are cited.
- No authentication or rate limiting on the API.

## Roadmap

- **v1:** ingest the FastAPI docs, chunk by headings, embed them into pgvector, and answer with cited sources (or say it was not found).
- **v2:** tool calling: search and open issues on a fake issues database, check package versions via the PyPI API, with structured JSON outputs.
- **v3:** an evaluation dataset of 50 to 100 questions; measure retrieval quality and answer faithfulness.
- **v4:** prompt-injection and poisoned-document tests, a cost/latency dashboard, Docker Compose, deploy.
