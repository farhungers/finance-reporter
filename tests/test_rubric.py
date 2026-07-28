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
