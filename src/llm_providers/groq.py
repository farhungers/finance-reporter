"""Groq openai/gpt-oss-20b provider with STRICT JSON schema mode.

Model history:
  • llama-3.3-70b-versatile — deprecated by Groq 2026-08-17 (404).
  • openai/gpt-oss-120b — 2026-08-18: 413 rate_limit_exceeded every run (8K TPM
    org cap on free tier applies per-model; 120b prompt = ~10.8K tokens).
  • openai/gpt-oss-20b + json_object mode — 2026-08-18: json_validate_failed
    on nested trade schema (small model can't reliably emit valid JSON at scale).
  • openai/gpt-oss-20b + STRICT json_schema mode (current) — Groq's constrained
    decoding guarantees schema compliance mathematically. Root-cause fix for
    the json_validate_failed loop.

Design notes:
  • `_make_strict(schema)` transforms our schemas to satisfy Groq strict-mode
    rules: additionalProperties=false on every object AND every property listed
    in `required`. Optional fields become required-but-nullable via string|null.
  • System prompt no longer inlines the schema (constrained decoder enforces
    it); saves ~300-500 tokens per call.

Switch by setting LLM_PROVIDER=groq in .env. 429s handled via retry-after.
"""
from __future__ import annotations

import copy
import json
import logging
import re
import time
from typing import Any

from src.llm_providers.base import GenerateResult, Provider

log = logging.getLogger(__name__)

_MODEL_NAME = "openai/gpt-oss-20b"


def _make_strict(schema: dict[str, Any]) -> dict[str, Any]:
    """Transform a JSON schema into Groq strict-mode-compatible form.

    Groq strict mode (2026-08 docs) requires:
      1. `additionalProperties: false` on every object
      2. Every property key listed in `required`
      3. Optional fields expressed as nullable via union type

    We deep-copy so the input schema (used by other providers + tests) is not
    mutated. Recursively descend into properties + items + $defs.

    Fields that our downstream code treats as optional (low_star_warning,
    earnings_direction_expectation, rough_entry_hint) get made nullable so the
    model can emit `null` when the criterion doesn't apply — semantically
    equivalent to omission, and our .get() calls handle both."""
    s = copy.deepcopy(schema)
    _strictify(s)
    return s


_NULLABLE_KEYS = {
    "low_star_warning",
    "earnings_direction_expectation",
    "rough_entry_hint",
}


def _strictify(node: Any) -> None:
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "object":
        props = node.get("properties") or {}
        # All properties become required in strict mode
        node["required"] = list(props.keys())
        node["additionalProperties"] = False
        for key, prop in props.items():
            # Make nullable-optional fields explicitly nullable
            if key in _NULLABLE_KEYS and isinstance(prop, dict) and "type" in prop:
                pt = prop["type"]
                if isinstance(pt, str):
                    prop["type"] = [pt, "null"]
            _strictify(prop)
    elif t == "array":
        items = node.get("items")
        if isinstance(items, dict):
            _strictify(items)
    # Recurse into any nested dict values (e.g. $defs)
    for v in node.values():
        if isinstance(v, dict):
            _strictify(v)
        elif isinstance(v, list):
            for item in v:
                _strictify(item)
_MAX_RATE_LIMIT_SLEEP = 90  # cap in seconds — protects the 10-min workflow timeout


def _parse_retry_after(err: Exception) -> float | None:
    """Extract the retry-after hint from a Groq rate-limit error.

    Groq surfaces this either as an HTTP header on the exception's response
    or embedded in the error message ("Please try again in Xs"). Return None
    if we can't find it; caller uses a default backoff."""
    resp = getattr(err, "response", None)
    if resp is not None:
        headers = getattr(resp, "headers", None) or {}
        for k in ("retry-after", "Retry-After", "x-ratelimit-reset-tokens", "x-ratelimit-reset-requests"):
            v = headers.get(k) if hasattr(headers, "get") else None
            if v:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    m = re.search(r"([\d.]+)s?", str(v))
                    if m:
                        return float(m.group(1))
    m = re.search(r"try again in ([\d.]+)\s*s", str(err))
    if m:
        return float(m.group(1))
    return None


class GroqProvider(Provider):
    name = "groq"

    def __init__(self, api_key: str, model: str = _MODEL_NAME):
        if not api_key:
            raise ValueError("GROQ_API_KEY missing")
        from groq import Groq

        self._client = Groq(api_key=api_key)
        self._model = model

    def generate(
        self,
        system: str,
        user: str,
        response_schema: dict[str, Any],
    ) -> GenerateResult:
        # Strict json_schema mode — Groq's constrained decoder guarantees the
        # output matches. No need to inline schema in the system prompt.
        strict_schema = _make_strict(response_schema)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": strict_schema,
            },
        }
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    response_format=response_format,
                    # Low temperature keeps constrained-decoding stable; some
                    # thesis-prose variety loss is worth the reliability win.
                    temperature=0.15,
                    # Explicit output budget — Groq's per-org 8K TPM cap counts
                    # REQUESTED tokens (prompt + max_completion_tokens reserved),
                    # NOT consumed. Actual prompt runs ~4800 tokens after our
                    # trims. 2500 reserve keeps us at ~7300 < 8000 with margin
                    # for prompt drift. Still ~1900 words of output = enough for
                    # 2 pitches with tight thesis prose.
                    max_completion_tokens=2500,
                )
                text = resp.choices[0].message.content or ""
                parsed = json.loads(text)
                usage = resp.usage
                return GenerateResult(
                    parsed=parsed,
                    tokens_in=getattr(usage, "prompt_tokens", 0) or 0,
                    tokens_out=getattr(usage, "completion_tokens", 0) or 0,
                    raw_text=text,
                    provider=self.name,
                )
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                # 413 "Request too large" is NOT retryable — sleeping doesn't
                # shrink the request. Bail immediately so the operator gets
                # the alert fast instead of after 3 × 60s sleeps.
                if "request too large" in err_str or "413" in err_str:
                    log.warning("groq request too large (non-retryable): %s", e)
                    break
                # 429/rolling-window rate limit — sleeping DOES help.
                is_rate_limit = "429" in err_str or "tokens per minute" in err_str
                if is_rate_limit and attempt < 2:
                    hint = _parse_retry_after(e)
                    sleep_s = min(_MAX_RATE_LIMIT_SLEEP, max(60.0, hint or 60.0))
                    log.warning(
                        "groq rate-limited (attempt %d); sleeping %.1fs before retry",
                        attempt + 1,
                        sleep_s,
                    )
                    time.sleep(sleep_s)
                    continue
                log.warning("groq attempt %d failed: %s", attempt + 1, e)
        raise RuntimeError(f"groq failed after retries: {last_error}")
