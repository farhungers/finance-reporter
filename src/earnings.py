"""Earnings calendar check for pitched tickers (CLAUDE.md §D.8, §C16, §E.21).

Rule: if a pitched ticker's next earnings is within 3 trading days (either side),
`earnings_within_3d=1`, `catalyst_proximity` is force-set to 1 (LLM cannot override),
and the pitch thesis MUST mention the earnings date + expected direction.

Primary: yfinance. Fallback: Nasdaq calendar RSS. On both-fail: return None (no
auto-trigger; downstream treats NULL as unknown per §D.8 fallback rule).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

log = logging.getLogger(__name__)

# US market holidays are ignored here — a 3-trading-day window computed from
# calendar days minus weekends is a safe approximation (holidays only shift the
# window by ~1 day, well within the intended flag's tolerance).


@dataclass(frozen=True)
class EarningsInfo:
    ticker: str
    next_earnings_date: date
    days_until: int         # calendar days (may be negative if within 3d already passed)
    trading_days_until: int
    within_3_trading_days: bool
    direction_expectation: Optional[str] = None  # 'bullish' / 'bearish' / 'unknown'


def _trading_days_between(d0: date, d1: date) -> int:
    """Approximate trading-day count (weekdays only). d0<=d1 → positive."""
    if d0 > d1:
        return -_trading_days_between(d1, d0)
    days = 0
    cur = d0
    while cur < d1:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            days += 1
    return days


def check_earnings(ticker: str, today: Optional[date] = None) -> Optional[EarningsInfo]:
    """Return EarningsInfo if next earnings is knowable, None on both-fail.
    within_3_trading_days is True when the trading-day distance is 0..3 inclusive
    on either side of today.
    """
    if today is None:
        today = date.today()
    next_dt = _yf_next_earnings(ticker)
    if next_dt is None:
        next_dt = _nasdaq_next_earnings(ticker)
    if next_dt is None:
        return None
    days = (next_dt - today).days
    trading = _trading_days_between(today, next_dt)
    return EarningsInfo(
        ticker=ticker,
        next_earnings_date=next_dt,
        days_until=days,
        trading_days_until=trading,
        within_3_trading_days=abs(trading) <= 3,
    )


def _yf_next_earnings(ticker: str) -> Optional[date]:
    try:
        import yfinance as yf
    except ImportError:
        return None
    try:
        t = yf.Ticker(ticker)
        # Prefer earnings_dates (multi-row DataFrame indexed by datetime)
        try:
            ed = t.earnings_dates
            if ed is not None and len(ed) > 0:
                today = datetime.utcnow().date()
                future = [d for d in ed.index if d.date() >= today]
                if future:
                    return min(future).date()
        except Exception:
            pass
        # Fallback: t.calendar returns dict/DataFrame with 'Earnings Date'
        cal = t.calendar
        if cal is None:
            return None
        if hasattr(cal, "get"):
            ed = cal.get("Earnings Date")
            if isinstance(ed, list) and ed:
                first = ed[0]
                if isinstance(first, datetime):
                    return first.date()
                if isinstance(first, date):
                    return first
        return None
    except Exception as e:
        log.warning("yfinance earnings lookup failed for %s: %s", ticker, e)
        return None


def _nasdaq_next_earnings(ticker: str) -> Optional[date]:
    """Placeholder for Nasdaq RSS fallback. Not implemented in v1 pilot — we rely
    on yfinance; if it fails, return None (treated as unknown per §D.8)."""
    return None
