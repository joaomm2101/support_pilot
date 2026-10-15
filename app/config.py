"""Settings loaded from the environment (.env): API key, model name, token prices.

Fail loudly at startup if a required value is missing.
"""


from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


    openai_api_key: str
    llm_model: str
    price_input_per_1m: float
    price_output_per_1m: float
    llm_timeout_seconds: float = 30.0  # Default timeout for LLM requests in seconds
    usage_log_path: str = "logs/usage.jsonl"  # Default path for usage log file


@lru_cache
def get_settings() -> Settings:
    """Get settings from the environment, cached for performance."""
    return Settings()