"""Cerebras Cloud provider — llama-3.3-70b on the free tier.

Positioned as a config-swap fallback for Groq. Same OpenAI-compatible chat API
shape, but Cerebras' free tier does not share Groq's 8K TPM per-org cap that
forced 10+ commits of prompt-trimming firefighting on 2026-08-18. Model is the
same size class (70b vs Groq's downgraded 20b), which lifts thesis-prose quality
back where the rubric was calibrated.

Switch with `LLM_PROVIDER=cerebras` + `CEREBRAS_API_KEY` set. Zero recurring
cost — free tier is generous enough for the 12 sends/week the bot produces.

Structured output uses JSON-object mode with the schema pasted into the system
prompt. Cerebras also advertises strict json_schema mode; we can adopt that
later if json_object mode drifts, but the schema-in-prompt path is what Groq
used pre-strict-mode and worked fine at this scale.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from src.llm_providers.base import GenerateResult, Provider

log = logging.getLogger(__name__)

_MODEL_NAME = "llama-3.3-70b"


def _schema_hint(schema: dict[str, Any]) -> str:
    return (
        "Return ONLY a single JSON object matching this schema exactly. "
        "No prose, no code fences, no commentary.\n"
        f"SCHEMA:\n{json.dumps(schema, separators=(',', ':'))}"
    )


class CerebrasProvider(Provider):
    name = "cerebras"

    def __init__(self, api_key: str, model: str = _MODEL_NAME):
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY missing")
        from cerebras.cloud.sdk import Cerebras

        self._client = Cerebras(api_key=api_key)
        self._model = model

    def generate(
        self,
        system: str,
        user: str,
        response_schema: dict[str, Any],
    ) -> GenerateResult:
        system_with_schema = f"{system}\n\n{_schema_hint(response_schema)}"
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_with_schema},
                        {"role": "user", "content": user},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.15,
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
                log.warning("cerebras attempt %d failed: %s", attempt + 1, e)
        raise RuntimeError(f"cerebras failed after retries: {last_error}")
