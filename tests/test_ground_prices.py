"""Trade-price grounding regression — Session-N §D.1.a Part 3 quality fix.

Prior generator shipped LLM-invented entries: NVDA@520 across weeks even after
NVDA had traded elsewhere. Root cause: market_snapshot only fed indices +
gold/oil/BTC to the LLM; the picked equity's live price was never in context,
so the model anchored to training data. Result: 60% SL hit rate.

_ground_prices() snaps entry to live spot when the LLM drifts >2% and sizes
SL/TP from 14d ATR to guarantee R:R ≥ 2:1.
"""
from __future__ import annotations

from unittest.mock import patch

from src import trades


def test_entry_snapped_when_llm_drift_over_two_percent():
    with patch("src.market_data.latest_price", return_value=500.0), \
         patch("src.market_data.atr14", return_value=None):
        entry, tp, sl, notes = trades._ground_prices(
            "NVDA", "equity", "long",
            llm_entry=520.0, llm_tp=560.0, llm_sl=500.0,
        )
    assert entry == 500.0
    assert any(n.startswith("entry_snapped") for n in notes)
    # TP/SL distances preserved from LLM when ATR unavailable
    assert tp == 500.0 + 40.0     # llm_tp - llm_entry = 40
    assert sl == 500.0 - 20.0     # llm_entry - llm_sl = 20


def test_entry_kept_when_llm_within_tolerance():
    with patch("src.market_data.latest_price", return_value=500.0), \
         patch("src.market_data.atr14", return_value=None):
        entry, _, _, notes = trades._ground_prices(
            "NVDA", "equity", "long",
            llm_entry=505.0, llm_tp=550.0, llm_sl=490.0,  # 1% dev
        )
    assert entry == 505.0
    assert not any(n.startswith("entry_snapped") for n in notes)


def test_atr_sizes_sl_and_enforces_2to1_rr_long():
    with patch("src.market_data.latest_price", return_value=100.0), \
         patch("src.market_data.atr14", return_value=2.0):
        entry, tp, sl, notes = trades._ground_prices(
            "AAPL", "equity", "long",
            llm_entry=100.0, llm_tp=101.0, llm_sl=99.5,  # bad R:R
        )
    # SL = spot - 1.5*ATR = 100 - 3 = 97
    # TP = spot + 2*(1.5*ATR) = 100 + 6 = 106  → R:R = 6/3 = 2.0
    assert sl == 97.0
    assert tp == 106.0
    assert (tp - entry) / (entry - sl) >= 2.0
    assert any(n.startswith("atr_sized") for n in notes)


def test_atr_sizes_sl_and_enforces_2to1_rr_short():
    with patch("src.market_data.latest_price", return_value=100.0), \
         patch("src.market_data.atr14", return_value=2.0):
        entry, tp, sl, notes = trades._ground_prices(
            "XOM", "equity", "short",
            llm_entry=100.0, llm_tp=99.0, llm_sl=100.5,
        )
    assert sl == 103.0
    assert tp == 94.0
    assert (entry - tp) / (sl - entry) >= 2.0


def test_spot_unavailable_returns_llm_numbers():
    with patch("src.market_data.latest_price", return_value=None), \
         patch("src.market_data.atr14", return_value=None):
        entry, tp, sl, notes = trades._ground_prices(
            "GOLD", "commodity", "long",
            llm_entry=4000.0, llm_tp=4100.0, llm_sl=3950.0,
        )
    assert entry == 4000.0
    assert tp == 4100.0
    assert sl == 3950.0
    assert "spot_unavailable" in notes
