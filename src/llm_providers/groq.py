"""Groq Llama 3.3 70B fallback provider — config swap only.

Free tier: 30 RPM. Switch by setting LLM_PROVIDER=groq in .env.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from src.llm_providers.base import GenerateResult, Provider

log = logging.getLogger(__name__)

_MODEL_NAME = "llama-3.3-70b-versatile"


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
        for attempt in range(2):
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
                log.warning("groq attempt %d failed: %s", attempt + 1, e)
        raise RuntimeError(f"groq failed after retry: {last_error}")
