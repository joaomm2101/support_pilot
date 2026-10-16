import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import get_settings
from app.llm import LLMError, LLMResult

client = TestClient(main.app)


def make_result() -> LLMResult:
    return LLMResult(
        answer="FastAPI is a web framework.",
        model="test-model",
        input_tokens=1000,
        output_tokens=500,
        latency_ms=12.34,
    )


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_answer_and_usage(monkeypatch):
    async def fake_ask_llm(question):
        return make_result()

    monkeypatch.setattr(main, "ask_llm", fake_ask_llm)

    response = client.post("/chat", json={"question": "What is FastAPI?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "FastAPI is a web framework."
    assert body["usage"]["input_tokens"] == 1000
    assert body["usage"]["cost_usd"] == pytest.approx(0.002)


def test_chat_writes_usage_log(monkeypatch):
    async def fake_ask_llm(question):
        return make_result()

    monkeypatch.setattr(main, "ask_llm", fake_ask_llm)

    client.post("/chat", json={"question": "What is FastAPI?"})

    lines = Path(get_settings().usage_log_path).read_text().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["question_chars"] == len("What is FastAPI?")
    assert "question" not in record


def test_chat_rejects_empty_question():
    response = client.post("/chat", json={"question": "   "})
    assert response.status_code == 422


def test_chat_returns_502_when_llm_fails(monkeypatch):
    async def failing_ask_llm(question):
        raise LLMError("boom")

    monkeypatch.setattr(main, "ask_llm", failing_ask_llm)

    response = client.post("/chat", json={"question": "What is FastAPI?"})

    assert response.status_code == 502