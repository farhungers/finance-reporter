"""Earnings-within-3d flag — CLAUDE.md §D.8 / §E.21.

Testing the trading-day math (not the yfinance fetch) since network calls are
not deterministic. yfinance is exercised in the pilot dry-run separately."""
from datetime import date, timedelta

from src.earnings import _trading_days_between


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
