"""Accuracy resolver — CLAUDE.md §D.3 / §E.8. Append-only; no writeback to generator."""
import json
from datetime import date

from src.accuracy import _check_tp_sl, _trading_days_between


def test_trading_days_helper():
    d0 = date(2026, 7, 27)  # Mon
    d1 = date(2026, 8, 3)   # Mon
    assert _trading_days_between(d0, d1) == 5


def test_tp_hit_long():
    entry, tp, sl = 100.0, 110.0, 95.0
    hist = [(date(2026, 7, 27), 100, 111, 99, 110)]
    result = _check_tp_sl("long", entry, tp, sl, hist)
    assert result is not None
    label, r = result
    assert label == "hit_tp"
    assert r > 0


def test_sl_hit_long():
    entry, tp, sl = 100.0, 110.0, 95.0
    hist = [(date(2026, 7, 27), 100, 102, 94, 96)]
    result = _check_tp_sl("long", entry, tp, sl, hist)
    assert result is not None
    label, r = result
    assert label == "hit_sl"
    assert r < 0


def test_neither_hit_returns_none():
    entry, tp, sl = 100.0, 110.0, 95.0
    hist = [(date(2026, 7, 27), 100, 102, 98, 101)]
    assert _check_tp_sl("long", entry, tp, sl, hist) is None


def test_short_sl_hit():
    """Short: SL is above entry, TP is below."""
    entry, tp, sl = 100.0, 90.0, 105.0
    hist = [(date(2026, 7, 27), 100, 106, 100, 105)]
    result = _check_tp_sl("short", entry, tp, sl, hist)
    assert result is not None
    label, r = result
    assert label == "hit_sl"


def test_short_tp_hit():
    entry, tp, sl = 100.0, 90.0, 105.0
    hist = [(date(2026, 7, 27), 100, 101, 89, 91)]
    result = _check_tp_sl("short", entry, tp, sl, hist)
    assert result is not None
    label, r = result
    assert label == "hit_tp"


def test_same_bar_both_hit_conservative_sl():
    """If both TP and SL are hit in the same bar, we assume SL (conservative)."""
    entry, tp, sl = 100.0, 110.0, 95.0
    hist = [(date(2026, 7, 27), 100, 111, 94, 100)]
    result = _check_tp_sl("long", entry, tp, sl, hist)
    label, _ = result
    assert label == "hit_sl"
