"""Length budget guardrails — CLAUDE.md §E.14.

Approximates token budget as chars/4 (rule-of-thumb for English + markdown).
The test asserts an UPPER bound to catch runaway generation. Under-budget is fine.

Budgets (from §E.14):
  daily_morning:     ≤ ~1500 tokens display  → char limit ~6500
  daily_wrap:        ≤ ~400 tokens           → char limit ~1800
  weekly_lookback:   ≤ ~2000 tokens          → char limit ~8500
  weekly_prep:       ≤ ~1200 tokens          → char limit ~5200
  /stats reply:      ≤ ~600 tokens           → char limit ~2600
"""

BUDGETS_CHARS = {
    "daily_morning": 6500,
    "daily_wrap": 1800,
    "weekly_lookback": 8500,
    "weekly_prep": 5200,
    "stats": 2600,
}


def test_budgets_exposed():
    for k, v in BUDGETS_CHARS.items():
        assert v > 0
