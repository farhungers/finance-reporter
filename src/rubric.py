"""5-factor rubric, 0-5 star scoring. Python sums booleans — LLM never freeform-scores.

CLAUDE.md §C4, §D.2, §E.7. Do NOT invent factors. Do NOT let the LLM output a star int.

Rubric v1.1 (2026-08-18 calibration; §C5 authorized after n=22 resolved in 4★
bucket): factor NAMES remain locked per §C4, but Python now VERIFIES the LLM's
booleans against objective criteria and downgrades on mismatch.

v1.1 (Aug 2026): macro_alignment + base_rate_support gained trend/analog audits.

v1.2 (2026-08-31 calibration; §C5 authorized after n=55 resolved trades): the
two remaining LLM-authored factors (technical_setup, risk_reward) were ON for
100% of trades and lost all discrimination power. Data:
  • 5★ trades avg −0.50R, 4★ avg −0.37R, 2★ avg +0.02R — star rating INVERTED
  • technical_setup, risk_reward: never OFF in 55 resolved trades → dead
Audits added:
  • technical_setup=TRUE requires the reasoning to name a specific numeric
    level within 1×ATR of entry (else forced FALSE)
  • risk_reward is now OBJECTIVELY computed from entry/tp/sl/direction when
    those are supplied — LLM boolean overridden either way. TRUE iff actual
    R:R ≥ 2.0, else FALSE
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

# v1.2 audit for technical_setup: reasoning must name a numeric price level
# within 1×ATR of the (grounded) entry. Extracts ints and decimals; skips
# 4-digit integers 1900-2099 that are almost always analog years, not price
# levels. Also skips small integers ≤50 that are typically MA periods (20d,
# 50d, 200d) rather than actual levels.
_NUMERIC_TOKEN = re.compile(r"\b\d+(?:[.,]\d+)?\b")


def _reasoning_names_level(
    reasoning: str, entry: Optional[float], atr: Optional[float]
) -> bool:
    """True iff reasoning cites a number within 1×ATR of entry.

    Filters:
      • Years 1900-2099 as bare 4-digit ints — analog anchors, not levels.
      • Small ints ≤50 with no decimal — MA periods (20d, 200d) not levels.
    """
    if not reasoning or entry is None or entry <= 0 or atr is None or atr <= 0:
        return False
    for tok in _NUMERIC_TOKEN.findall(reasoning):
        try:
            n = float(tok.replace(",", ""))
        except ValueError:
            continue
        is_int = n == int(n)
        if is_int and 1900 <= n <= 2099:
            continue  # year, not a price level
        if is_int and n <= 50:
            continue  # MA period token (20d, 50d, 200d)
        if abs(n - entry) <= atr:
            return True
    return False


def _computed_rr(
    direction: Optional[str],
    entry: Optional[float],
    tp: Optional[float],
    sl: Optional[float],
) -> Optional[float]:
    """Objective R:R from grounded entry/tp/sl. None if any input missing or invalid."""
    if entry is None or tp is None or sl is None or not direction:
        return None
    d = direction.lower()
    if d == "long":
        risk = entry - sl
        reward = tp - entry
    elif d == "short":
        risk = sl - entry
        reward = entry - tp
    else:
        return None
    if risk <= 0 or reward <= 0:
        return None
    return reward / risk


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
    entry: Optional[float] = None,
    tp: Optional[float] = None,
    sl: Optional[float] = None,
    atr: Optional[float] = None,
) -> RubricResult:
    """Convert LLM-supplied booleans into a 0-5 star rating with Python audits.

    - Every FACTOR key must be present in `booleans`.
    - Truthy → 1, falsy → 0 after audits below.
    - If earnings_within_3d is True, catalyst_proximity is forced to 1
      regardless of LLM output (CLAUDE.md §D.8, §E.21).

    Audits:
      v1.1 (§C5, 2026-08-18):
      • macro_alignment=1: if direction+trend data supplied, verify direction
        agrees with 20d MA. Mismatch → forced 0.
      • base_rate_support=1: reasoning_text must contain a dated analog
        anchor. Missing → forced 0.
      v1.2 (§C5, 2026-08-31):
      • technical_setup=1: reasoning must cite a numeric level within 1×ATR
        of entry (when entry+atr supplied). Missing → forced 0.
      • risk_reward: when entry+tp+sl+direction supplied, compute actual R:R
        and OVERRIDE the LLM boolean. TRUE iff computed R:R ≥ 2.0.
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

    # v1.2 audit: technical_setup requires a cited level near entry.
    # Only fires when we have grounded entry + ATR to measure against.
    if (
        breakdown["technical_setup"] == 1
        and entry is not None
        and atr is not None
        and atr > 0
    ):
        if not _reasoning_names_level(reasoning_text, entry, atr):
            breakdown["technical_setup"] = 0

    # v1.2 audit: risk_reward is objectively computed when trade prices supplied.
    # Overrides LLM boolean in both directions — LLM claim is irrelevant when
    # we can measure R:R directly. Skipped for pitches (no entry/tp/sl).
    rr = _computed_rr(direction, entry, tp, sl)
    if rr is not None:
        breakdown["risk_reward"] = 1 if rr >= 2.0 else 0

    if earnings_within_3d:
        breakdown["catalyst_proximity"] = 1

    return RubricResult(stars=sum(breakdown.values()), breakdown=breakdown)
