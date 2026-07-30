"""Google Gemini 2.0 Flash provider — free tier default (CLAUDE.md §C9).

Free tier: 15 RPM, 1M TPM, 1500 req/day. We use ~30 calls/week, well inside limits.
Context caching enabled for knowledge library payload (near-zero token cost after warm).
"""
from __future__ import annotations

import json
import logging
from typing import Any

from src.llm_providers.base import GenerateResult, Provider

log = logging.getLogger(__name__)

_MODEL_NAME = "gemini-2.5-flash"

# Fields Gemini's schema dialect rejects. Strip recursively before send.
_GEMINI_UNSUPPORTED_KEYS = {
    "maxItems", "minItems", "maxLength", "minLength",
    "maxProperties", "minProperties", "pattern", "patternProperties",
    "additionalProperties", "$schema", "$id", "$ref", "definitions",
    "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "allOf", "anyOf", "oneOf", "not", "if", "then", "else",
}


def _sanitize_schema(node: Any) -> Any:
    if isinstance(node, dict):
        return {
            k: _sanitize_schema(v) for k, v in node.items()
            if k not in _GEMINI_UNSUPPORTED_KEYS
        }
    if isinstance(node, list):
        return [_sanitize_schema(x) for x in node]
    return node


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = _MODEL_NAME):
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing")
        # Imported lazily so tests can run without google-generativeai installed.
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._genai = genai
        self._model_name = model

    def generate(
        self,
        system: str,
        user: str,
        response_schema: dict[str, Any],
    ) -> GenerateResult:
        model = self._genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system,
        )
        # Structured output: mime=json + schema constrains the model's output.
        # Gemini's schema dialect is an OpenAPI subset — strip fields it rejects
        # (maxItems, minItems, etc.) so callers can pass full JSON Schema and we
        # gracefully downgrade. Bullet-count discipline moves into the system
        # prompt when maxItems is stripped.
        gen_config = {
            "response_mime_type": "application/json",
            "response_schema": _sanitize_schema(response_schema),
            "temperature": 0.4,
        }
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                resp = model.generate_content(user, generation_config=gen_config)
                text = resp.text or ""
                parsed = json.loads(text)
                usage = getattr(resp, "usage_metadata", None)
                return GenerateResult(
                    parsed=parsed,
                    tokens_in=getattr(usage, "prompt_token_count", 0) or 0,
                    tokens_out=getattr(usage, "candidates_token_count", 0) or 0,
                    raw_text=text,
                    provider=self.name,
                )
            except Exception as e:
                last_error = e
                log.warning("gemini attempt %d failed: %s", attempt + 1, e)
        raise RuntimeError(f"gemini failed after retry: {last_error}")
