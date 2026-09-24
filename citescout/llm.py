"""Minimal client for any OpenAI-compatible chat endpoint (Groq by default).

Kept deliberately small: one function that asks for a JSON object and parses it, with a
retry on malformed output and an automatic fall back to a smaller model on rate limits.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

import httpx


class LLMError(RuntimeError):
    pass


class LLM:
    def __init__(self, api_key: str, base_url: str, model: str, fallback_model: str | None = None,
                 timeout: float = 90.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback_model = fallback_model
        self.used_model: str | None = None
        self._client = httpx.Client(timeout=timeout, headers={"Authorization": f"Bearer {api_key}"})

    def _call(self, model: str, messages: list[dict[str, str]], temperature: float) -> str:
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        r = self._client.post(f"{self.base_url}/chat/completions", json=body)
        if r.status_code == 429:
            raise _RateLimited(r.headers.get("retry-after", "?"))
        if r.status_code >= 400:
            raise LLMError(f"{r.status_code}: {r.text[:300]}")
        return r.json()["choices"][0]["message"]["content"] or ""

    def json(self, system: str, user: str, temperature: float = 0.2, attempts: int = 3) -> dict[str, Any]:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        models = [self.model] + ([self.fallback_model] if self.fallback_model else [])
        last_err: Exception | None = None
        for model in models:
            for attempt in range(attempts):
                try:
                    text = self._call(model, messages, temperature)
                    self.used_model = model
                    return parse_json(text)
                except _RateLimited as e:
                    last_err = e
                    break  # move to the fallback model right away
                except (LLMError, ValueError, httpx.HTTPError) as e:
                    last_err = e
                    time.sleep(1.5 * (attempt + 1))
        raise LLMError(f"LLM call failed: {last_err}")


class _RateLimited(Exception):
    pass


def parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start : end + 1])
