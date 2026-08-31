"""Rubric — CLAUDE.md §C4 / §D.2 / §E.7. Python sums booleans; LLM never freeform-scores."""
import pytest

from src.rubric import FACTORS, RubricResult, score


def _all_true() -> dict:
    return {f: True for f in FACTORS}


def _all_false() -> dict:
    return {f: False for f in FACTORS}


def test_all_true_is_five():
    r = score(_all_true())
    assert r.stars == 5
    assert all(v == 1 for v in r.breakdown.values())


def test_all_false_is_zero():
    r = score(_all_false())
    assert r.stars == 0


def test_partial_sums():
    b = _all_false()
    b["macro_alignment"] = True
    b["risk_reward"] = True
    r = score(b)
    assert r.stars == 2
    assert r.breakdown["macro_alignment"] == 1
    assert r.breakdown["catalyst_proximity"] == 0
    assert r.breakdown["risk_reward"] == 1


def test_missing_factor_raises():
    b = _all_true()
    del b["catalyst_proximity"]
    with pytest.raises(ValueError, match="catalyst_proximity"):
        score(b)


def test_earnings_forces_catalyst_proximity():
    """§D.8, §E.21: earnings_within_3d=True → catalyst_proximity=1 regardless of LLM output."""
    b = _all_false()
    r = score(b, earnings_within_3d=True)
    assert r.breakdown["catalyst_proximity"] == 1
    assert r.stars == 1


def test_earnings_does_not_double_count_if_already_true():
    b = _all_false()
    b["catalyst_proximity"] = True
    r = score(b, earnings_within_3d=True)
    assert r.stars == 1  # only catalyst_proximity is 1


def test_truthy_coercion():
    b = {f: 1 for f in FACTORS}
    r = score(b)
    assert r.stars == 5


# --- Rubric v1.1 audit tests (2026-08-18 calibration) --------------------

def test_macro_alignment_downgraded_when_fighting_trend():
    """LONG with spot below 20d MA cannot claim macro_alignment."""
    b = _all_true()
    r = score(b, direction="long", spot=95.0, ma20=100.0, reasoning_text="2024 CPI drift analog")
    assert r.breakdown["macro_alignment"] == 0
    assert r.stars == 4  # was 5, macro_alignment audit downgraded


def test_macro_alignment_kept_when_riding_trend():
    b = _all_true()
    r = score(b, direction="long", spot=105.0, ma20=100.0, reasoning_text="2024 CPI drift analog")
    assert r.breakdown["macro_alignment"] == 1


def test_macro_alignment_short_downgraded_when_price_above_ma():
    b = _all_true()
    r = score(b, direction="short", spot=105.0, ma20=100.0, reasoning_text="2024 breakdown analog")
    assert r.breakdown["macro_alignment"] == 0


def test_macro_alignment_unchanged_when_trend_unknown():
    """No trend data + macro keyword present → LLM boolean preserved."""
    b = _all_true()
    r = score(
        b, direction="long", spot=None, ma20=None,
        reasoning_text="Q3 2024 Fed rate-cut rebound analog",
    )
    assert r.breakdown["macro_alignment"] == 1


def test_base_rate_downgraded_without_dated_analog():
    b = _all_true()
    r = score(b, direction="long", spot=105.0, ma20=100.0, reasoning_text="historically this works")
    assert r.breakdown["base_rate_support"] == 0


def test_base_rate_kept_when_year_cited_with_outcome():
    """v1.2: analog year alone isn't enough — needs outcome verb nearby."""
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="Fed cuts — mirrors the 2019 rally pattern",
    )
    assert r.breakdown["base_rate_support"] == 1


def test_base_rate_kept_on_post_event_phrase():
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="Fed cuts — post-CPI drift setup",
    )
    assert r.breakdown["base_rate_support"] == 1


def test_base_rate_kept_on_quarter_reference_with_outcome():
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="Fed cuts — analog to Q4 2022 rally in duration",
    )
    assert r.breakdown["base_rate_support"] == 1


def test_both_audits_can_downgrade_stars_to_three():
    b = _all_true()
    r = score(b, direction="long", spot=95.0, ma20=100.0, reasoning_text="just usually works")
    assert r.breakdown["macro_alignment"] == 0
    assert r.breakdown["base_rate_support"] == 0
    assert r.stars == 3


# --- Rubric v1.2 audit tests (2026-08-31 calibration) --------------------

def test_technical_setup_kept_when_reasoning_cites_level_near_entry():
    """Reasoning naming a price level within 1×ATR of entry passes the audit."""
    b = _all_true()
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="breakout retest of 100.5 swing high — 2024 analog",
        entry=100.0, tp=104.0, sl=98.0, atr=2.0,
    )
    assert r.breakdown["technical_setup"] == 1


def test_technical_setup_downgraded_when_reasoning_names_no_level():
    """Reasoning with only MA-period tokens (20d, 200d) fails — those aren't levels."""
    b = _all_true()
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="long above 200-day MA — Q4 2024 analog",
        entry=100.0, tp=104.0, sl=98.0, atr=2.0,
    )
    assert r.breakdown["technical_setup"] == 0


def test_technical_setup_downgraded_when_cited_level_too_far():
    """A level >1×ATR from entry doesn't count — LLM cited a level not near price."""
    b = _all_true()
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="breakout at 130 support — 2024 analog",
        entry=100.0, tp=104.0, sl=98.0, atr=2.0,
    )
    assert r.breakdown["technical_setup"] == 0


def test_technical_setup_year_not_mistaken_for_level():
    """Year 2024 near entry $2020 must not be counted as a price level."""
    b = _all_true()
    r = score(
        b, direction="long", spot=2020.0, ma20=2000.0,
        reasoning_text="mirrors the 2024 setup",  # only year, no real level
        entry=2020.0, tp=2100.0, sl=1980.0, atr=20.0,
    )
    assert r.breakdown["technical_setup"] == 0


def test_technical_setup_unchanged_when_atr_unavailable():
    """Audit degrades gracefully when we can't measure — trust LLM boolean."""
    b = _all_true()
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="just vibes — 2024 analog",
        entry=100.0, tp=104.0, sl=98.0, atr=None,
    )
    assert r.breakdown["technical_setup"] == 1


def test_risk_reward_computed_from_prices_overrides_llm_true():
    """LLM says TRUE but actual R:R = 1.5 — Python forces FALSE."""
    b = _all_true()
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="2024 analog, breakout at 100.5",
        entry=100.0, tp=103.0, sl=98.0, atr=2.0,  # reward=3, risk=2 → R:R=1.5
    )
    assert r.breakdown["risk_reward"] == 0


def test_risk_reward_computed_from_prices_overrides_llm_false():
    """LLM says FALSE but actual R:R = 2.5 — Python forces TRUE."""
    b = _all_true()
    b["risk_reward"] = False
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="2024 analog, breakout at 100.5",
        entry=100.0, tp=105.0, sl=98.0, atr=2.0,  # reward=5, risk=2 → R:R=2.5
    )
    assert r.breakdown["risk_reward"] == 1


def test_risk_reward_short_direction_computed_correctly():
    """Short: risk = sl-entry, reward = entry-tp."""
    b = _all_true()
    r = score(
        b, direction="short", spot=100.0, ma20=100.0,
        reasoning_text="2024 breakdown analog, resistance at 100.2",
        entry=100.0, tp=95.0, sl=102.0, atr=2.0,  # reward=5, risk=2 → R:R=2.5
    )
    assert r.breakdown["risk_reward"] == 1


def test_risk_reward_unchanged_when_no_prices_supplied():
    """Pitches path: no entry/tp/sl — LLM boolean preserved."""
    b = _all_true()
    b["risk_reward"] = True
    r = score(b, direction="long", spot=100.0, ma20=100.0, reasoning_text="2024 analog")
    assert r.breakdown["risk_reward"] == 1


def test_risk_reward_invalid_prices_leaves_llm_boolean():
    """SL on wrong side of entry → computation invalid → LLM boolean preserved."""
    b = _all_true()
    r = score(
        b, direction="long", spot=100.0, ma20=100.0,
        reasoning_text="Fed 2024 rally analog, entry at 100.5",
        entry=100.0, tp=105.0, sl=101.0, atr=2.0,  # long but sl > entry
    )
    # LLM said TRUE, invalid prices → preserved
    assert r.breakdown["risk_reward"] == 1


# --- Rubric v1.2 P2 audits (macro keyword + base-rate outcome-verb) ------

def test_macro_alignment_downgraded_when_no_macro_keyword():
    """Trend agrees but reasoning names no macro theme → downgrade."""
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="chart looks fine and 2024 rally pattern held",
    )
    assert r.breakdown["macro_alignment"] == 0


def test_macro_alignment_kept_with_keyword():
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="riding Fed rate-cut path and 2024 rally analog",
    )
    assert r.breakdown["macro_alignment"] == 1


def test_macro_alignment_various_keywords_accepted():
    for kw in ("DXY soft", "yields falling", "hawkish tone", "risk-on regime", "dovish PCE"):
        b = _all_true()
        r = score(
            b, direction="long", spot=105.0, ma20=100.0,
            reasoning_text=f"{kw}, 2024 rally analog",
        )
        assert r.breakdown["macro_alignment"] == 1, f"expected keyword accepted: {kw!r}"


def test_base_rate_downgraded_when_analog_alone_without_verb():
    """v1.2 tightening: 'recall 2022' or 'mirrors 2019 pattern' without an outcome
    verb near the anchor no longer earns the point."""
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="Fed cuts — recall 2022 setup",  # no outcome verb near "2022"
    )
    assert r.breakdown["base_rate_support"] == 0


def test_base_rate_kept_with_outcome_verb_before_anchor():
    """Verb before anchor also counts (60-char window either side)."""
    b = _all_true()
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text="Fed cuts — gold rallied hard in 2019 on the same setup",
    )
    assert r.breakdown["base_rate_support"] == 1


def test_base_rate_downgraded_when_verb_too_far_from_anchor():
    """>60 chars between anchor and outcome verb → not proof of citation."""
    b = _all_true()
    long_text = (
        "Fed cuts — 2019 seen as reference. " + ("filler text " * 15) + "gold rallied"
    )
    r = score(
        b, direction="long", spot=105.0, ma20=100.0,
        reasoning_text=long_text,
    )
    assert r.breakdown["base_rate_support"] == 0
