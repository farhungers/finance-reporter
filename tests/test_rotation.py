"""Rotation-discipline regressions (2026-08-18).

Prior data (through 2026-08-13):
  • Pitch universe concentration: MSFT×7, AAPL×5, GOOGL×3 = 15/26 pitches from
    3 tickers over 3 weeks. No rotation.
  • Commodity trades: 11/11 GOLD long mean-reversion. 0 TP, all SL, avg R -1.0.

Fixes:
  • Ticker cooldown — recent pitches excluded from the LLM's ticker menu.
  • Commodity day-of-week anchor — Mon GOLD, Tue OIL_WTI, Wed COPPER, Thu SILVER,
    Fri NAT_GAS.
"""
from __future__ import annotations

from src import pitches, trades


def test_commodity_dow_rotation_covers_workweek():
    picks = {trades._suggested_commodity(f"2026-08-{17 + i:02d}") for i in range(5)}
    # Aug 17 = Mon, Aug 21 = Fri
    assert picks == {"GOLD", "OIL_WTI", "COPPER", "SILVER", "NAT_GAS"}


def test_commodity_anchor_appears_in_prompt():
    body = trades._build_user_prompt(
        date_ist="2026-08-19",   # Wednesday
        market_snapshot="SPY=500",
        calendar_summary="(none)",
        knowledge_context="",
        suggested_commodity=trades._suggested_commodity("2026-08-19"),
        suggested_crypto=trades._suggested_crypto("2026-08-19"),
    )
    assert "COMMODITY ROTATION ANCHOR: COPPER" in body
    # 2026-08-31: crypto rotation added — verify it's rendered too.
    assert "CRYPTO ROTATION ANCHOR: SOL" in body  # Wed anchor


def test_pitch_prompt_excludes_recent_tickers():
    body = pitches._build_user_prompt(
        date_ist="2026-08-18",
        calendar_summary="(none)",
        market_snapshot="SPY=500",
        news_summary="(none)",
        knowledge_context="",
        earnings_flags={},
        excluded_tickers={"MSFT", "AAPL"},
    )
    universe_line = [l for l in body.splitlines() if l.startswith("AAPL,") or "MSFT," in l]
    # Excluded tickers should not appear in the universe list line.
    for ln in body.splitlines():
        if ln.startswith("BLUE_CHIP_UNIVERSE"):
            continue
        # The universe is inline on the next line; simplest check:
    assert "MSFT" not in body.split("TODAY'S CALENDAR")[0]
    assert "AAPL" not in body.split("TODAY'S CALENDAR")[0]


def test_pitch_prompt_keeps_universe_when_cooldown_empty():
    body = pitches._build_user_prompt(
        date_ist="2026-08-18",
        calendar_summary="(none)",
        market_snapshot="SPY=500",
        news_summary="(none)",
        knowledge_context="",
        earnings_flags={},
        excluded_tickers=set(),
    )
    assert "MSFT" in body
    assert "AAPL" in body


def test_pitch_horizon_capped_at_15():
    # Named-slot schema (2026-08-18) — check via pitch_1's horizon_days field.
    schema = pitches._PITCH_SCHEMA["properties"]["pitch_1"]["properties"]["horizon_days"]
    assert schema["maximum"] == 15
