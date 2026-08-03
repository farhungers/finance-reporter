"""Earnings line render — §D.8 requires flagged pitches to display
'📅 Earnings <date IST> · <impact>' between header and thesis."""
from src import pitches
from src.reports.daily_morning import _pitch_block


def _make_pitch(**overrides) -> pitches.Pitch:
    defaults = dict(
        asset_symbol="AAPL",
        direction="long",
        thesis="Apple looks set up on the print.",
        key_factors=["one", "two"],
        rough_entry_hint="near 185",
        star_rating=4,
        rubric_breakdown={"macro_alignment": 1, "technical_setup": 1,
                          "catalyst_proximity": 1, "base_rate_support": 1,
                          "risk_reward": 0},
        low_star_warning=None,
        earnings_within_3d=False,
        earnings_date_ist=None,
        earnings_direction_expectation=None,
        knowledge_sources_used=[],
        horizon_days=7,
    )
    defaults.update(overrides)
    return pitches.Pitch(**defaults)


def test_earnings_line_rendered_when_flagged():
    p = _make_pitch(
        earnings_within_3d=True,
        earnings_date_ist="2026-08-05",
        earnings_direction_expectation="bullish setup on cloud growth",
    )
    out = _pitch_block([p])
    # Emoji + escaped date + impact text should be present
    assert "📅" in out
    assert "2026\\-08\\-05" in out  # MarkdownV2 escapes hyphens
    assert "bullish setup on cloud growth" in out


def test_earnings_line_absent_when_not_flagged():
    p = _make_pitch(earnings_within_3d=False)
    out = _pitch_block([p])
    assert "📅" not in out


def test_earnings_line_falls_back_when_impact_missing():
    """§C11 never-omit — if LLM forgot direction, we still show the date line."""
    p = _make_pitch(
        earnings_within_3d=True,
        earnings_date_ist="2026-08-05",
        earnings_direction_expectation=None,
    )
    out = _pitch_block([p])
    assert "📅" in out
    assert "impact expected" in out  # the fallback string in daily_morning.py


def test_earnings_line_needs_both_flag_and_date():
    """If flag is on but we lack the date, don't emit a bare '📅 Earnings' line."""
    p = _make_pitch(
        earnings_within_3d=True,
        earnings_date_ist=None,
        earnings_direction_expectation="bullish",
    )
    out = _pitch_block([p])
    assert "📅" not in out
