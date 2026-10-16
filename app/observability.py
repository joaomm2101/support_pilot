"""Tokens in/out, estimated cost and latency per call.

Appends one JSON line per call to logs/usage.jsonl.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import get_settings
from app.llm import LLMResult


def calculate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    settings = get_settings()
    return (
        input_tokens * settings.price_input_per_1m
        + output_tokens * settings.price_output_per_1m
    ) / 1_000_000

def log_usage(question: str, result: LLMResult, cost_usd: float) -> None:
    path = Path(get_settings().usage_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question_chars": len(question),
        "model": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "cost_usd": cost_usd,
        "latency_ms": round(result.latency_ms, 1),
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")