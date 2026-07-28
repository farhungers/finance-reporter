"""Abstract Provider interface for LLM backends (CLAUDE.md §D.5).

Adding a new provider = one file implementing Provider + one factory line
in src/llm_client.py. Zero refactor."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerateResult:
    parsed: dict[str, Any]
    tokens_in: int = 0
    tokens_out: int = 0
    raw_text: str = ""
    provider: str = ""


class Provider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(
        self,
        system: str,
        user: str,
        response_schema: dict[str, Any],
    ) -> GenerateResult:
        """Return parsed JSON matching response_schema. Raise on failure after retry."""
        raise NotImplementedError
