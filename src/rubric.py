"""5-factor rubric, 0-5 star scoring. Python sums booleans — LLM never freeform-scores.

CLAUDE.md §C4, §D.2, §E.7. Do NOT invent factors. Do NOT let the LLM output a star int.

Rubric v1.1 (2026-08-18 calibration; §C5 authorized after n=22 resolved in 4★
bucket): factor NAMES remain locked per §C4, but Python now VERIFIES the LLM's
booleans against objective criteria and downgrades on mismatch.

Prior data (n=35 resolved trades) showed macro_alignment TRUE→12% TP vs FALSE
→40%, and base_rate_support TRUE→9% vs FALSE→38% — the LLM was setting both
TRUE indiscriminately. Verification closes those cheats:
  • macro_alignment=TRUE requires direction agreeing with 20d trend
    (else Python forces FALSE regardless of LLM claim)
  • base_rate_support=TRUE requires a nameable analog — a year/date-anchored
    reference in the one_line_reasoning or thesis (else forced FALSE)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

FACTORS = (
    "macro_alignment",
    "technical_setup",
    "catalyst_proximity",
    "base_rate_support",
    "risk_reward",
)

# "post-CPI Oct 2024 drift", "2020 gold spike", "2022-Q4", "March '23", etc.
# Loose but not wide-open — must anchor to a specific time reference, not
# just "historically" or "in prior cycles" (the exact hedge the LLM used to
# earn base_rate_support=TRUE without support).
_ANALOG_ANCHOR = re.compile(
    r"\b(?:19|20)\d{2}\b"
    r"|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+(?:19|20)?\d{2}\b"
    r"|\bQ[1-4]\s*(?:19|20)?\d{2}\b"
    r"|\bpost[- ](?:cpi|fomc|nfp|opec|ecb|boe)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RubricResult:
    stars: int
    breakdown: dict[str, int]  # {factor: 0 or 1}


def _trend_agrees(direction: str, spot: Optional[float], ma20: Optional[float]) -> Optional[bool]:
    """Return True/False if direction aligns with the 20-day MA cross-over; None
    when trend data unavailable (caller then falls back to LLM's boolean)."""
    if spot is None or ma20 is None or ma20 <= 0:
        return None
    trend_up = spot >= ma20
    d = direction.lower()
    if d == "long":
        return trend_up
    if d == "short":
        return not trend_up
    return None  # neutral — no directional trend claim to verify


def score(
    booleans: dict[str, Any],
    earnings_within_3d: bool = False,
    *,
    direction: Optional[str] = None,
    spot: Optional[float] = None,
    ma20: Optional[float] = None,
    reasoning_text: str = "",
) -> RubricResult:
    """Convert LLM-supplied booleans into a 0-5 star rating with Python audits.

    - Every FACTOR key must be present in `booleans`.
    - Truthy → 1, falsy → 0 after audits below.
    - If earnings_within_3d is True, catalyst_proximity is forced to 1
      regardless of LLM output (CLAUDE.md §D.8, §E.21).

    Audits (§C5 calibration, rubric v1.1):
      • macro_alignment=1: if direction+trend data supplied, verify direction
        agrees with 20d MA. Mismatch → forced 0.
      • base_rate_support=1: reasoning_text must contain a dated analog
        anchor (year, month+year, quarter, or a "post-EVENT" phrase).
        Missing → forced 0.
    """
    breakdown: dict[str, int] = {}
    for f in FACTORS:
        if f not in booleans:
            raise ValueError(f"rubric missing factor: {f!r} (got keys {list(booleans)})")
        breakdown[f] = 1 if bool(booleans[f]) else 0

    # Audit: macro_alignment must agree with 20d trend when we can measure it.
    if breakdown["macro_alignment"] == 1 and direction is not None:
        agrees = _trend_agrees(direction, spot, ma20)
        if agrees is False:
            breakdown["macro_alignment"] = 0

    # Audit: base_rate_support requires a nameable dated analog in the text.
    if breakdown["base_rate_support"] == 1 and reasoning_text:
        if not _ANALOG_ANCHOR.search(reasoning_text):
            breakdown["base_rate_support"] = 0

    if earnings_within_3d:
        breakdown["catalyst_proximity"] = 1

    return RubricResult(stars=sum(breakdown.values()), breakdown=breakdown)
