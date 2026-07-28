"""Star rendering per CLAUDE.md §C14. Single source of truth — never inline stars elsewhere."""
from __future__ import annotations

_EMPTY = "\u2606"   # ☆
_FILLED = "\u2b50"  # ⭐
_GOLD = "\U0001f31f"  # 🌟

_TABLE = {
    0: _EMPTY * 5,
    1: _FILLED + _EMPTY * 4,
    2: _FILLED * 2 + _EMPTY * 3,
    3: _FILLED * 3 + _EMPTY * 2,
    4: _FILLED * 4 + _EMPTY,
    5: _GOLD * 5,
}


def render(n: int) -> str:
    if n not in _TABLE:
        raise ValueError(f"star count must be 0..5, got {n!r}")
    return _TABLE[n]
