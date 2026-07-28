"""5-factor rubric, 0-5 star scoring. Python sums booleans — LLM never freeform-scores.

CLAUDE.md §C4, §D.2, §E.7. Do NOT invent factors. Do NOT let the LLM output a star int.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FACTORS = (
    "macro_alignment",
    "technical_setup",
    "catalyst_proximity",
    "base_rate_support",
    "risk_reward",
)


@dataclass(frozen=True)
class RubricResult:
    stars: int
    breakdown: dict[str, int]  # {factor: 0 or 1}


def score(booleans: dict[str, Any], earnings_within_3d: bool = False) -> RubricResult:
    """Convert LLM-supplied booleans into a 0-5 star rating.

    - Every FACTOR key must be present in `booleans`.
    - Truthy → 1, falsy → 0.
    - If earnings_within_3d is True, catalyst_proximity is forced to 1
      regardless of LLM output (CLAUDE.md §D.8, §E.21).
    """
    breakdown: dict[str, int] = {}
    for f in FACTORS:
        if f not in booleans:
            raise ValueError(f"rubric missing factor: {f!r} (got keys {list(booleans)})")
        breakdown[f] = 1 if bool(booleans[f]) else 0

    if earnings_within_3d:
        breakdown["catalyst_proximity"] = 1

    return RubricResult(stars=sum(breakdown.values()), breakdown=breakdown)
