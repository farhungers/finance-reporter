"""Class-integrity validator for trade slots — CLAUDE.md §C2, §D.1.a Part 3.

2026-08-31 calibration: LLM placed COP (ConocoPhillips equity) into the
commodity slot with reasoning about copper. Validator catches wrong-class
tickers before grounding runs on invalid asset/class pairings.
"""
from src.trades import _CRYPTO_ALLOWLIST, _class_mismatches, _validate_slot_class
from src.market_data import COMMODITY_SYMBOLS


def test_commodity_slot_accepts_gold():
    assert _validate_slot_class("commodity", "GOLD") is None


def test_commodity_slot_accepts_all_known_commodities():
    for sym in COMMODITY_SYMBOLS:
        assert _validate_slot_class("commodity", sym) is None


def test_commodity_slot_rejects_equity_ticker():
    """COP (ConocoPhillips) is an equity, not a commodity — 2026-08-26 pathology."""
    err = _validate_slot_class("commodity", "COP")
    assert err is not None
    assert "COP" in err


def test_commodity_slot_rejects_crypto():
    err = _validate_slot_class("commodity", "BTC")
    assert err is not None


def test_crypto_slot_accepts_btc_eth_sol():
    for sym in ("BTC", "ETH", "SOL"):
        assert _validate_slot_class("crypto", sym) is None


def test_crypto_slot_rejects_equity():
    err = _validate_slot_class("crypto", "AAPL")
    assert err is not None


def test_crypto_slot_rejects_commodity():
    err = _validate_slot_class("crypto", "GOLD")
    assert err is not None


def test_equity_slot_accepts_generic_ticker():
    assert _validate_slot_class("equity", "AAPL") is None
    assert _validate_slot_class("equity", "NVDA") is None


def test_equity_slot_rejects_commodity_symbol():
    err = _validate_slot_class("equity", "GOLD")
    assert err is not None


def test_equity_slot_rejects_crypto_symbol():
    err = _validate_slot_class("equity", "BTC")
    assert err is not None


def test_case_insensitive():
    """Symbols normalized to uppercase before check."""
    assert _validate_slot_class("commodity", "gold") is None
    assert _validate_slot_class("crypto", "btc") is None


def test_class_mismatches_all_correct():
    raw = {
        "commodity": {"asset_symbol": "GOLD"},
        "equity":    {"asset_symbol": "AAPL"},
        "crypto":    {"asset_symbol": "BTC"},
    }
    assert _class_mismatches(raw) == []


def test_class_mismatches_flags_wrong_slot():
    raw = {
        "commodity": {"asset_symbol": "COP"},   # equity in commodity slot
        "equity":    {"asset_symbol": "AAPL"},
        "crypto":    {"asset_symbol": "BTC"},
    }
    mismatches = _class_mismatches(raw)
    assert len(mismatches) == 1
    assert mismatches[0][0] == "commodity"


def test_class_mismatches_flags_all_wrong():
    raw = {
        "commodity": {"asset_symbol": "AAPL"},
        "equity":    {"asset_symbol": "GOLD"},
        "crypto":    {"asset_symbol": "MSFT"},
    }
    mismatches = _class_mismatches(raw)
    assert len(mismatches) == 3
    assert {m[0] for m in mismatches} == {"commodity", "equity", "crypto"}


def test_crypto_allowlist_covers_top_10():
    """Sanity: BTC/ETH/SOL definitely in allowlist so tests are meaningful."""
    for sym in ("BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE"):
        assert sym in _CRYPTO_ALLOWLIST
