"""Novelty check for pitch/trade reasoning (CLAUDE.md §C11, §D.7).

2026-08-31 pathology: LLM reasoning templates repeat verbatim across days —
"breakout retest of 200-day MA, riding AI capex ROI proof-cycle" appeared for
6 different tickers over a 2-week window. Same words → same failure mode.

This module provides:
  • recent_reasoning() — pull last N days of pitch theses / trade reasoning
    from SQLite, for injection into the next prompt as anti-repetition context
  • similarity() — Jaccard on ≥3-char token bags between two strings; caller
    thresholds (default 0.6)

Post-generation: if new text similarity to any recent baseline ≥ threshold,
log LOUD. Not hard-blocked per §C11 (never-omit) — operator sees the drift
and can force regeneration on subsequent runs.
"""
from __future__ import annotations

import logging
import re
from typing import Iterable

from src import db

log = logging.getLogger(__name__)

_TOKEN = re.compile(r"[a-zA-Z]{3,}")
# Very common finance words that would inflate Jaccard on their own — dropped
# so the metric measures whether the SETUP is repeated, not just the vocabulary.
_STOPWORDS: frozenset[str] = frozenset({
    "the", "and", "for", "with", "into", "from", "long", "short",
    "over", "under", "above", "below", "near", "against", "next",
    "today", "tomorrow", "week", "month", "day", "days",
    "price", "level", "levels", "trade", "trades", "pitch", "pitches",
    "target", "entry", "exit", "session", "market", "markets",
    "risk", "reward", "ratio", "position", "trend",
})


def _tokens(s: str) -> frozenset[str]:
    """Lowercase token bag of ≥3-char alpha words, minus common stopwords."""
    if not s:
        return frozenset()
    return frozenset(t.lower() for t in _TOKEN.findall(s)) - _STOPWORDS


def similarity(a: str, b: str) -> float:
    """Jaccard similarity of two strings' token bags. Range [0.0, 1.0]."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 0.0
    union = ta | tb
    if not union:
        return 0.0
    return len(ta & tb) / len(union)


def most_similar(new_text: str, baselines: Iterable[str]) -> tuple[float, str]:
    """Return (best_jaccard, matching_baseline_text). (0.0, "") if no baselines."""
    best = 0.0
    match = ""
    for b in baselines:
        j = similarity(new_text, b)
        if j > best:
            best = j
            match = b
    return best, match


def recent_pitch_theses(days: int = 3) -> list[str]:
    """Return theses from pitches generated in the last `days` days.
    Ordered newest-first, capped at 20 rows to bound memory."""
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT thesis FROM pitches
               WHERE generated_at >= datetime('now', ?)
               ORDER BY generated_at DESC LIMIT 20""",
            (f"-{days} days",),
        ).fetchall()
    return [r["thesis"] for r in rows if r["thesis"]]


def recent_trade_reasoning(days: int = 3) -> list[str]:
    """Return one_line_reasoning strings from trades in the last `days` days."""
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT one_line_reasoning FROM trades
               WHERE generated_at >= datetime('now', ?)
               ORDER BY generated_at DESC LIMIT 20""",
            (f"-{days} days",),
        ).fetchall()
    return [r["one_line_reasoning"] for r in rows if r["one_line_reasoning"]]


def snippets(rows: list[str], max_words: int = 15, cap: int = 3) -> list[str]:
    """Trim rows to `max_words` each and return the first `cap`. Used to build
    a small anti-repetition context block for the prompt without blowing the
    Groq 8K TPM budget."""
    out = []
    for r in rows[:cap]:
        words = (r or "").split()
        if len(words) > max_words:
            out.append(" ".join(words[:max_words]) + "…")
        else:
            out.append(r or "")
    return out
