"""Runtime configuration, read from the environment (and an optional .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when a required setting is missing."""


@dataclass(frozen=True)
class Settings:
    serpapi_api_key: str | None
    llm_api_key: str | None
    llm_base_url: str
    llm_model: str
    llm_fallback_model: str | None
    max_searches: int
    cache_dir: Path
    offline: bool = False
    cache_max_age_hours: float | None = None  # SerpApi cache expiry; None = never (diff sets 24h)
    followups: int = 2  # round-2 searches aimed at the draft's gaps (0 = single pass)

    def require_serpapi(self) -> str:
        if not self.serpapi_api_key and not self.offline:
            raise ConfigError(
                "SERPAPI_API_KEY is not set. Get a free key at https://serpapi.com/manage-api-key "
                "and put it in .env (see .env.example)."
            )
        return self.serpapi_api_key or ""

    def require_llm(self) -> str:
        if not self.llm_api_key:
            raise ConfigError(
                "LLM_API_KEY is not set. Any OpenAI-compatible endpoint works; the default is Groq "
                "(https://console.groq.com/keys)."
            )
        return self.llm_api_key


def load_settings(*, offline: bool = False, max_searches: int | None = None,
                  followups: int | None = None) -> Settings:
    load_dotenv(Path.cwd() / ".env", override=False)
    return Settings(
        serpapi_api_key=os.getenv("SERPAPI_API_KEY") or None,
        llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or None,
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-oss-120b"),
        llm_fallback_model=os.getenv("LLM_FALLBACK_MODEL", "openai/gpt-oss-20b") or None,
        max_searches=max_searches or int(os.getenv("CITESCOUT_MAX_SEARCHES", "8")),
        cache_dir=Path(os.getenv("CITESCOUT_CACHE_DIR", ".citescout_cache")),
        offline=offline,
        followups=max(0, min(3, followups if followups is not None else int(os.getenv("CITESCOUT_FOLLOWUPS", "2")))),
    )
