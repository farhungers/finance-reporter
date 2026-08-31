"""Concentration guard — CLAUDE.md §C11, §D.1.a Part 3.

Data through 2026-08-31: 23/24 crypto trades were BTC, 12/23 commodity trades
were GOLD. The soft anchor didn't bind. This guard forces the weekday anchor
when the same asset would fill the slot for the 3rd time in 5 sessions.
"""
from unittest.mock import patch

from src.trades import (
    _CRYPTO_DOW,
    _COMMODITY_DOW,
    _concentration_forced_symbol,
    _suggested_commodity,
    _suggested_crypto,
)


def test_commodity_weekday_anchors_cover_all_days():
    assert set(_COMMODITY_DOW.keys()) == {0, 1, 2, 3, 4}


def test_crypto_weekday_anchors_cover_all_days():
    assert set(_CRYPTO_DOW.keys()) == {0, 1, 2, 3, 4}


def test_suggested_commodity_monday_is_gold():
    # 2026-08-31 is a Monday
    assert _suggested_commodity("2026-08-31") == "GOLD"


def test_suggested_crypto_tuesday_is_eth():
    # 2026-09-01 is a Tuesday
    assert _suggested_crypto("2026-09-01") == "ETH"


def test_concentration_no_history_no_force():
    """First trade in a slot — no history, no substitution."""
    with patch("src.trades._recent_slot_asset", return_value=[]):
        assert _concentration_forced_symbol("crypto", "BTC", "BTC") is None
        assert _concentration_forced_symbol("crypto", "SOL", "BTC") is None


def test_concentration_forces_anchor_on_3rd_same_asset_in_5():
    """2 recent BTC in the window + today's BTC = 3 → force anchor."""
    with patch("src.trades._recent_slot_asset", return_value=["BTC", "BTC", "ETH", "SOL", "ETH"]):
        # LLM picked BTC again; anchor for the day is ETH
        forced = _concentration_forced_symbol("crypto", "BTC", "ETH")
        assert forced == "ETH"


def test_concentration_2_of_5_not_forced():
    """Only 1 BTC in history + today's BTC = 2 → still under threshold."""
    with patch("src.trades._recent_slot_asset", return_value=["BTC", "ETH", "SOL", "ETH", "SOL"]):
        forced = _concentration_forced_symbol("crypto", "BTC", "ETH")
        assert forced is None


def test_concentration_anchor_already_picked_no_op():
    """LLM's pick already matches the anchor — nothing to force even if concentrated."""
    with patch("src.trades._recent_slot_asset", return_value=["ETH", "ETH", "ETH", "SOL", "BTC"]):
        forced = _concentration_forced_symbol("crypto", "ETH", "ETH")
        assert forced is None


def test_concentration_case_insensitive():
    with patch("src.trades._recent_slot_asset", return_value=["BTC", "BTC"]):
        assert _concentration_forced_symbol("crypto", "btc", "eth") == "eth"


def test_concentration_gold_pattern_forces_anchor():
    """Real pathology: GOLD in commodity slot 3 of last 5 → force weekday anchor."""
    with patch("src.trades._recent_slot_asset", return_value=["GOLD", "GOLD", "COPPER", "GOLD", "OIL_WTI"]):
        forced = _concentration_forced_symbol("commodity", "GOLD", "SILVER")
        assert forced == "SILVER"


def test_concentration_5_different_no_force():
    """Perfect rotation — no forcing regardless of today's pick."""
    with patch("src.trades._recent_slot_asset", return_value=["GOLD", "OIL_WTI", "COPPER", "SILVER", "NAT_GAS"]):
        assert _concentration_forced_symbol("commodity", "GOLD", "SILVER") is None
