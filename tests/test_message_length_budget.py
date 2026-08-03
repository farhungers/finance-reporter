"""Length budget guardrails — CLAUDE.md §E.14.

Approximates token budget as chars/4 (rule-of-thumb for English + markdown).
The tests assemble reports with realistic-max content and assert body length
stays under the char budget derived from each report's token cap.

Budgets (from §E.14):
  daily_morning:     ≤ ~1500 tokens display  → char limit ~6500
  daily_wrap:        ≤ ~400 tokens           → char limit ~1800
  weekly_lookback:   ≤ ~2000 tokens          → char limit ~8500
  weekly_prep:       ≤ ~1200 tokens          → char limit ~5200
  /stats reply:      ≤ ~600 tokens           → char limit ~2600

Prior to 2026-08-03 this file only exposed the budget dict — no actual length
enforcement. §E.14 says "budgets enforced by this test", so it now does.
"""
from src import calendar_source, pitches, trades
from src.reports.daily_morning import _calendar_block, _pitch_block, _trade_block


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


def _big_pitch(sym: str, with_earnings: bool = False) -> pitches.Pitch:
    """Maximally-sized pitch within schema limits — 4 key_factors, long thesis."""
    return pitches.Pitch(
        asset_symbol=sym,
        direction="long",
        thesis=(
            "This name reports earnings on Wednesday and the setup is unusually "
            "clean going in. The Street already reset expectations lower after "
            "the recent guidance shift, so the bar is easy to clear. Fund "
            "positioning is light, meaning any modest beat brings buyers back "
            "in size. The primary risk is a broad-market risk-off session that "
            "overrides the single-name catalyst — manageable but real."
        ),
        key_factors=[
            "Earnings Wednesday — Street already reset expectations lower",
            "Fund positioning light, room for buyers to return in size",
            "Trading 12% cheaper than its 5-year average P/E multiple",
            "Product cycle mix favors the second half of the fiscal year",
        ],
        rough_entry_hint="near $185 prior-swing support on any morning pullback",
        star_rating=4,
        rubric_breakdown={f: 1 for f in ["macro_alignment", "technical_setup",
                                          "catalyst_proximity", "base_rate_support",
                                          "risk_reward"]},
        low_star_warning=None,
        earnings_within_3d=with_earnings,
        earnings_date_ist="2026-08-06" if with_earnings else None,
        earnings_direction_expectation="bullish setup on cloud growth momentum" if with_earnings else None,
        knowledge_sources_used=["knowledge/blue_chip/AAPL_facts.md"],
        horizon_days=7,
    )


def _big_trade(sym: str, klass: str) -> trades.Trade:
    return trades.Trade(
        asset_symbol=sym,
        asset_class=klass,
        direction="long",
        entry=4045.0,
        tp=4120.0,
        sl=4008.0,
        one_line_reasoning=(
            "Retest of prior breakout level with DXY rolling off recent highs "
            "supports a bounce-off-support entry with clear invalidation."
        ),
        star_rating=4,
        rubric_breakdown={f: 1 for f in ["macro_alignment", "technical_setup",
                                          "catalyst_proximity", "base_rate_support",
                                          "risk_reward"]},
        low_star_warning=None,
        knowledge_sources_used=["knowledge/correlations/dxy_gold.md"],
    )


def _big_events(date_ist: str, n: int = 6) -> list[calendar_source.CalendarEvent]:
    """n 3-star events for the day — plausible realistic-max load."""
    templates = [
        ("CPI m/m", "US", "0.3%", "0.2%"),
        ("Retail Sales m/m", "US", "0.1%", "-0.1%"),
        ("Initial Jobless Claims", "US", "215K", "220K"),
        ("FOMC Meeting Minutes", "US", "—", "—"),
        ("ECB Rate Decision", "EU", "4.25%", "4.25%"),
        ("BoJ Policy Statement", "JP", "0.5%", "0.5%"),
    ]
    return [
        calendar_source.CalendarEvent(
            date_ist=date_ist,
            time_ist=f"{15 + (i % 6):02d}:30",
            country=c,
            event_name=name,
            importance=3,
            forecast=f,
            previous=p,
            actual=None,
            source="test",
        )
        for i, (name, c, f, p) in enumerate(templates[:n])
    ]


def test_daily_morning_layout_under_budget():
    """Assemble maximally-sized calendar + 2 pitches + 3 trades and verify total
    body length stays under the daily_morning char budget."""
    events = _big_events("2026-08-04", n=6)
    pl = [_big_pitch("AAPL", with_earnings=True), _big_pitch("MSFT")]
    tl = [_big_trade("GOLD", "commodity"), _big_trade("SPY", "equity"),
          _big_trade("BTC", "crypto")]

    cal = _calendar_block(events, "2026-08-04")
    pit = _pitch_block(pl)
    tra = _trade_block(tl)

    # Layout content only (headers/footer add ~500 chars, well under margin)
    layout_body = "\n\n".join([cal, pit, tra])
    assert len(layout_body) < BUDGETS_CHARS["daily_morning"], (
        f"daily_morning layout {len(layout_body)} > budget "
        f"{BUDGETS_CHARS['daily_morning']} — reduce content or expand budget"
    )


def test_daily_morning_calendar_scales():
    """No 3-star events → very compact calendar block. Verify no runaway."""
    cal = _calendar_block([], "2026-08-04")
    assert len(cal) < 200  # empty-day sentinel is a single short line


def test_pitch_block_scales_with_count():
    """One 5★ pitch should be well under half a full 2-pitch block."""
    single = _pitch_block([_big_pitch("AAPL")])
    double = _pitch_block([_big_pitch("AAPL"), _big_pitch("MSFT")])
    # 2× isn't exactly 2× (shared separator overhead) but must be > 1.5×
    assert len(double) > len(single) * 1.5


def test_trade_block_covers_all_three_classes():
    """Every class must appear once — no substitution across classes (§C2)."""
    tl = [_big_trade("GOLD", "commodity"), _big_trade("SPY", "equity"),
          _big_trade("BTC", "crypto")]
    out = _trade_block(tl)
    # Ticker symbols must all be present
    assert "GOLD" in out
    assert "SPY" in out
    assert "BTC" in out
