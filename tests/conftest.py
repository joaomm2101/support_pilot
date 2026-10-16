"""Shared pytest fixtures, including a fake LLM (no real API calls in tests)."""

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def test_settings(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("PRICE_INPUT_PER_1M", "1.0")
    monkeypatch.setenv("PRICE_OUTPUT_PER_1M", "2.0")
    monkeypatch.setenv("USAGE_LOG_PATH", str(tmp_path / "usage.jsonl"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()