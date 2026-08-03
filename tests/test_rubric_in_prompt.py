"""Regression: rubric factor names AND criterion phrases must appear in the pitch
and trade system prompts. Prevents the "LLM guesses the factor meaning" drift
we found on 2026-08-03 (§D.2, §E.7)."""
from src.pitches import _SYSTEM_PROMPT as PITCH_PROMPT
from src.rubric import FACTORS
from src.trades import _SYSTEM_PROMPT as TRADE_PROMPT


# Phrases that must be discoverable near each factor definition. Not full spec
# text — just enough to prove the criterion was authored, not just the name.
# Pitches and trades share the first four factors; risk_reward differs (§D.2:
# pitches use ATR headroom; trades use TP/SL ratio ≥ 2:1).
_SHARED_MARKERS = {
    "macro_alignment": ("DOMINANT macro", "rides"),
    "technical_setup": ("nameable", "level"),
    "catalyst_proximity": ("NAMED", "DATED"),
    "base_rate_support": ("historically", "analog"),
}
_PITCH_MARKERS = {**_SHARED_MARKERS, "risk_reward": ("invalidation", "ATR")}
_TRADE_MARKERS = {**_SHARED_MARKERS, "risk_reward": ("TP/SL", "2:1")}


def _prompt_contains_all(prompt: str, markers: tuple[str, ...]) -> bool:
    return all(m in prompt for m in markers)


def test_pitch_prompt_names_each_factor():
    for f in FACTORS:
        assert f in PITCH_PROMPT, f"pitch prompt missing factor name {f!r}"


def test_trade_prompt_names_each_factor():
    for f in FACTORS:
        assert f in TRADE_PROMPT, f"trade prompt missing factor name {f!r}"


def test_pitch_prompt_has_criterion_markers():
    for f, markers in _PITCH_MARKERS.items():
        assert _prompt_contains_all(PITCH_PROMPT, markers), (
            f"pitch prompt is missing criterion markers for {f}: {markers}"
        )


def test_trade_prompt_has_criterion_markers():
    for f, markers in _TRADE_MARKERS.items():
        assert _prompt_contains_all(TRADE_PROMPT, markers), (
            f"trade prompt is missing criterion markers for {f}: {markers}"
        )


def test_pitch_prompt_forbids_5star_inflation():
    assert "rare" in PITCH_PROMPT.lower()
    assert "default FALSE" in PITCH_PROMPT or "Default FALSE" in PITCH_PROMPT


def test_trade_prompt_forbids_5star_inflation():
    assert "rare" in TRADE_PROMPT.lower()
    assert "default FALSE" in TRADE_PROMPT or "Default FALSE" in TRADE_PROMPT
