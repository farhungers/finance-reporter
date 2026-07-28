"""Provider-agnostic LLM wrapper (CLAUDE.md §C9, §D.5, §E.6).

Public API: generate(system, user, schema) -> GenerateResult.
Provider chosen by config.LLM_PROVIDER. Zero recurring cost — free tier only.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from src import config
from src.llm_providers.base import GenerateResult, Provider


@lru_cache(maxsize=1)
def _get_provider() -> Provider:
    name = config.LLM_PROVIDER
    if name == "gemini":
        from src.llm_providers.gemini import GeminiProvider

        return GeminiProvider(api_key=config.GEMINI_API_KEY)
    if name == "groq":
        from src.llm_providers.groq import GroqProvider

        return GroqProvider(api_key=config.GROQ_API_KEY)
    if name == "dummy":
        from src.llm_providers.dummy import DummyProvider

        return DummyProvider()
    raise ValueError(f"unknown LLM_PROVIDER: {name!r}")


def generate(
    system: str,
    user: str,
    response_schema: dict[str, Any],
) -> GenerateResult:
    return _get_provider().generate(system, user, response_schema)
