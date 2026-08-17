"""Groq openai/gpt-oss-20b provider — config swap only.

Model history:
  • llama-3.3-70b-versatile — deprecated by Groq 2026-08-17 (404).
  • openai/gpt-oss-120b — tried 2026-08-18; free-tier TPM cap is 8K, pitch
    prompt requests ~10.8K → 413 every run. Unusable without paid tier.
  • openai/gpt-oss-20b — free-tier TPM 30K (comfortable headroom over our
    largest single call ~11K). Smaller model, some prose quality loss vs 70B,
    but reliably shippable at zero cost — §C9 "everything free" wins.

Switch by setting LLM_PROVIDER=groq in .env. 429s are handled via retry-after.
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from src.llm_providers.base import GenerateResult, Provider

log = logging.getLogger(__name__)

_MODEL_NAME = "openai/gpt-oss-20b"
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
        # Groq: JSON mode via response_format={"type":"json_object"}.
        # Schema is passed inline in the system prompt for compliance.
        schema_hint = json.dumps(response_schema, indent=2)
        aug_system = (
            f"{system}\n\nYour response MUST be a JSON object matching this schema:\n"
            f"```json\n{schema_hint}\n```"
        )
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": aug_system},
                        {"role": "user", "content": user},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.4,
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
                is_rate_limit = "rate_limit" in err_str or "429" in err_str or "tokens per minute" in err_str
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
