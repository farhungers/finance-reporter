"""Provider-agnostic LLM wrapper (CLAUDE.md §C9, §D.5, §E.6).

Public API: generate(system, user, schema) -> GenerateResult.
Provider chosen by config.LLM_PROVIDER. Zero recurring cost — free tier only.

2026-08-24 (roadmap Phase 4.2): opt-in auto-failover. When config.LLM_AUTO_FAILOVER
is set and the primary fails with a retryable non-auth error (413 request too
large, 429 rate limit exhausted after in-provider retries), we try the fallback
provider (config.LLM_FALLBACK_PROVIDER, defaults to cerebras when primary is
groq). Auth failures (401) never trigger failover — those must reach the
operator so the key gets rotated (per Aug 2026 silent-failure incident).
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from src import config
from src.llm_providers.base import GenerateResult, Provider

log = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _get_provider(name: str) -> Provider:
    if name == "gemini":
        from src.llm_providers.gemini import GeminiProvider

        return GeminiProvider(api_key=config.GEMINI_API_KEY)
    if name == "groq":
        from src.llm_providers.groq import GroqProvider

        return GroqProvider(api_key=config.GROQ_API_KEY)
    if name == "cerebras":
        from src.llm_providers.cerebras import CerebrasProvider

        return CerebrasProvider(api_key=config.CEREBRAS_API_KEY)
    if name == "dummy":
        from src.llm_providers.dummy import DummyProvider

        return DummyProvider()
    raise ValueError(f"unknown LLM_PROVIDER: {name!r}")


def _is_failover_eligible(err: Exception) -> bool:
    """Return True if err is a retryable non-auth failure worth failing over.

    Failover triggers on: 413 (request too large — different provider may
    have different limits), 429 / rate-limit (rolling window may already be
    fresh on the fallback provider).

    Failover does NOT trigger on: 401 / auth / invalid key (Aug 2026 silent-
    failure incident — those must page the operator, not be papered over).
    """
    s = str(err).lower()
    if "401" in s or "invalid_api_key" in s or "invalid api key" in s or "unauthorized" in s:
        return False
    if "413" in s or "request too large" in s:
        return True
    if "429" in s or "rate limit" in s or "tokens per minute" in s or "quota" in s:
        return True
    return False


def generate(
    system: str,
    user: str,
    response_schema: dict[str, Any],
) -> GenerateResult:
    primary_name = config.LLM_PROVIDER
    primary = _get_provider(primary_name)
    try:
        return primary.generate(system, user, response_schema)
    except Exception as e:
        if not (config.LLM_AUTO_FAILOVER and config.LLM_FALLBACK_PROVIDER):
            raise
        if not _is_failover_eligible(e):
            raise
        fb_name = config.LLM_FALLBACK_PROVIDER
        if fb_name == primary_name:
            raise
        log.warning(
            "primary provider %s failed with retryable error (%s); failing over to %s",
            primary_name, type(e).__name__, fb_name,
        )
        try:
            fallback = _get_provider(fb_name)
        except Exception as ce:
            log.error("fallback provider %s init failed: %s", fb_name, ce)
            raise e  # re-raise the original — fallback isn't available
        return fallback.generate(system, user, response_schema)


_PING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
    "required": ["ok"],
}


def ping() -> None:
    """Cheap preflight — proves the primary provider credentials work. Raises on failure.

    Called at run_report entry so an invalid API key fails BEFORE the expensive
    generation path and the operator gets a specific alert instead of a generic
    'report failed'. Costs ~50 tokens per call, well under any free-tier budget.

    NOTE: preflight intentionally pings ONLY the primary provider — a stale
    fallback key surfaces the day it's needed rather than being papered over
    at preflight time. The operator rotates both keys during the same window.
    """
    _get_provider(config.LLM_PROVIDER).generate(
        "Respond with the literal JSON {\"ok\": true}. Nothing else.",
        "ping",
        _PING_SCHEMA,
    )
