"""Earnings-within-3d flag — CLAUDE.md §D.8 / §E.21.

Testing the trading-day math (not the yfinance fetch) since network calls are
not deterministic. yfinance is exercised in the pilot dry-run separately."""
from datetime import date, timedelta
from unittest.mock import patch

from src.earnings import _trading_days_between, check_earnings


def test_same_day():
    d = date(2026, 7, 27)  # Monday
    assert _trading_days_between(d, d) == 0


def test_next_weekday():
    d0 = date(2026, 7, 27)  # Mon
    d1 = date(2026, 7, 28)  # Tue
    assert _trading_days_between(d0, d1) == 1


def test_across_weekend():
    fri = date(2026, 7, 31)  # Fri
    mon = date(2026, 8, 3)   # Mon
    assert _trading_days_between(fri, mon) == 1


def test_backward_negative():
    d0 = date(2026, 7, 27)
    d1 = date(2026, 7, 30)
    assert _trading_days_between(d1, d0) == -3


def test_within_3d_boundary():
    """A ticker with earnings 3 trading days out is within the flag; 4 is outside."""
    today = date(2026, 7, 27)  # Mon
    earnings_thu = date(2026, 7, 30)  # +3 trading days
    earnings_fri = date(2026, 7, 31)  # +4 trading days
    assert _trading_days_between(today, earnings_thu) == 3
    assert _trading_days_between(today, earnings_fri) == 4


# --- 2026-08-31 tense-discipline calibration ---------------------------------

def test_future_earnings_within_3d_triggers_flag():
    today = date(2026, 8, 4)  # Tue
    with patch("src.earnings._yf_next_earnings", return_value=date(2026, 8, 6)):
        info = check_earnings("AAPL", today=today)
    assert info is not None
    assert info.within_3_trading_days is True
    assert info.trading_days_until == 2


def test_past_earnings_within_3d_does_NOT_trigger_flag():
    """Past-side earnings (already reported) must NOT trigger — they aren't
    forward catalysts (2026-08-31 calibration; see earnings.py docstring)."""
    today = date(2026, 8, 4)  # Tue
    past = date(2026, 7, 30)  # 3 trading days ago
    with patch("src.earnings._yf_next_earnings", return_value=past):
        info = check_earnings("AAPL", today=today)
    assert info is not None
    assert info.within_3_trading_days is False
    assert info.trading_days_until == -3


def test_same_day_earnings_triggers_flag():
    """0 trading days out (earnings today) still triggers."""
    today = date(2026, 8, 4)
    with patch("src.earnings._yf_next_earnings", return_value=today):
        info = check_earnings("MSFT", today=today)
    assert info is not None
    assert info.within_3_trading_days is True
    assert info.trading_days_until == 0


def test_4_days_ahead_does_not_trigger():
    today = date(2026, 8, 3)  # Mon
    ahead = date(2026, 8, 7)  # +4 trading days (Fri)
    with patch("src.earnings._yf_next_earnings", return_value=ahead):
        info = check_earnings("NVDA", today=today)
    assert info is not None
    assert info.within_3_trading_days is False
