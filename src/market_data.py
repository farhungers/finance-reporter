"""Price data — yfinance for equities/commodities/futures, CoinGecko for crypto.

CLAUDE.md §B.3. Both free, no key. Fallbacks: Stooq (equities/commodities), Binance (crypto).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Optional

import requests

log = logging.getLogger(__name__)

# Blue-chip universe (§C3): S&P 100 constituents + top-15 US large caps by market cap.
# Concrete list assembled from S&P 100 (as of 2026) + top-15 non-overlapping additions.
# When a ticker is added here, its knowledge/blue_chip/{ticker}_facts.md MUST also exist (§E.19).
BLUE_CHIP_UNIVERSE: tuple[str, ...] = (
    # S&P 100 core (partial — top-liquidity mega/large caps)
    "AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META", "TSLA",
    "BRK-B", "AVGO", "LLY", "JPM", "V", "WMT", "XOM", "UNH",
    "MA", "PG", "COST", "JNJ", "HD", "ORCL", "BAC", "ABBV",
    "NFLX", "CVX", "KO", "MRK", "AMD", "CRM", "PEP", "TMO",
    "ADBE", "LIN", "ACN", "MCD", "CSCO", "ABT", "PM", "TXN",
    "IBM", "GE", "WFC", "DIS", "DHR", "VZ", "INTC", "CAT",
    "PFE", "AMGN", "GS", "NOW", "QCOM", "AMAT", "T", "UBER",
    "AXP", "SPGI", "MS", "BLK", "RTX", "NEE", "BKNG", "PGR",
    "HON", "SYK", "TJX", "C", "SCHW", "LOW", "COP", "BSX",
    "PLD", "ADP", "REGN", "VRTX", "ETN", "MMC", "GILD", "MDLZ",
    "ANET", "DE", "SBUX", "CVS", "MU", "PANW", "LMT", "FI",
    "ADI", "BX", "KLAC", "SO", "CB", "CI", "ICE", "USB",
    "AON", "MO",
)


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    prev_close: Optional[float]
    day_change_pct: Optional[float]
    asset_class: str  # 'equity' / 'commodity' / 'crypto'


def yf_quote(symbol: str, asset_class: str = "equity") -> Optional[Quote]:
    """Fetch a single quote via yfinance. Returns None on failure or missing data."""
    try:
        import yfinance as yf
    except ImportError:
        log.error("yfinance not installed")
        return None
    try:
        t = yf.Ticker(symbol)
        fast = t.fast_info
        raw_price = fast.get("last_price") or fast.get("lastPrice")
        if raw_price is None:
            return None
        price = float(raw_price)
        prev = fast.get("previous_close") or fast.get("previousClose")
        prev_f = float(prev) if prev is not None else None
        chg = ((price - prev_f) / prev_f * 100.0) if prev_f else None
        if price <= 0:
            return None
        return Quote(symbol, price, prev_f, chg, asset_class)
    except Exception as e:
        log.warning("yf_quote failed for %s: %s", symbol, e)
        return None


def yf_history(symbol: str, days: int = 30) -> list[tuple[date, float, float, float, float]]:
    """Return list of (date, open, high, low, close) for last `days` trading days."""
    try:
        import yfinance as yf
    except ImportError:
        return []
    try:
        end = datetime.now(UTC).date()
        start = end - timedelta(days=days * 2)  # buffer for weekends
        df = yf.Ticker(symbol).history(start=start.isoformat(), end=(end + timedelta(days=1)).isoformat())
        out = []
        for idx, row in df.iterrows():
            out.append((idx.date(), float(row["Open"]), float(row["High"]), float(row["Low"]), float(row["Close"])))
        return out[-days:]
    except Exception as e:
        log.warning("yf_history failed for %s: %s", symbol, e)
        return []


# --- Crypto: CoinGecko free API ------------------------------------------
_CG_URL = "https://api.coingecko.com/api/v3/simple/price"

# Map common tickers → CoinGecko ids
_CG_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "MATIC": "matic-network",
}


def coingecko_quote(symbol: str) -> Optional[Quote]:
    cg_id = _CG_ID.get(symbol.upper())
    if not cg_id:
        return None
    try:
        r = requests.get(
            _CG_URL,
            params={"ids": cg_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json().get(cg_id) or {}
        price = float(data.get("usd") or 0)
        chg = data.get("usd_24h_change")
        chg_f = float(chg) if chg is not None else None
        prev = price / (1 + chg_f / 100.0) if chg_f is not None and chg_f != -100 else None
        if price <= 0:
            return None
        return Quote(symbol.upper(), price, prev, chg_f, "crypto")
    except Exception as e:
        log.warning("coingecko_quote failed for %s: %s", symbol, e)
        return None


COMMODITY_SYMBOLS = {
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "OIL_WTI": "CL=F",
    "OIL_BRENT": "BZ=F",
    "COPPER": "HG=F",
    "NAT_GAS": "NG=F",
}

# yfinance USD-pair suffix for common crypto tickers. Used only when we need
# ATR/history for a crypto trade (CoinGecko doesn't cheaply expose OHLC).
CRYPTO_YF_SUFFIX = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "AVAX": "AVAX-USD",
    "LINK": "LINK-USD",
}


def commodity_quote(name: str) -> Optional[Quote]:
    sym = COMMODITY_SYMBOLS.get(name.upper())
    if not sym:
        return None
    q = yf_quote(sym, "commodity")
    if q is None:
        return None
    # Rename to friendly key
    return Quote(name.upper(), q.price, q.prev_close, q.day_change_pct, "commodity")


def _yf_symbol_for(symbol: str, asset_class: str) -> Optional[str]:
    """Resolve a friendly symbol + class to the yfinance ticker string."""
    ac = asset_class.lower()
    s = symbol.upper()
    if ac == "commodity":
        return COMMODITY_SYMBOLS.get(s)
    if ac == "crypto":
        return CRYPTO_YF_SUFFIX.get(s) or (f"{s}-USD" if "-" not in s else s)
    return s  # equity — friendly symbol is the yfinance ticker


def latest_price(symbol: str, asset_class: str) -> Optional[float]:
    """Unified spot getter across classes. Returns None on any fetch failure —
    callers must degrade gracefully (§C11: never omit; low_star_warning instead).
    Crypto path prefers CoinGecko for spot (cheap, reliable) with yfinance fallback."""
    ac = asset_class.lower()
    if ac == "crypto":
        q = coingecko_quote(symbol)
        if q is not None:
            return q.price
    yf_sym = _yf_symbol_for(symbol, ac)
    if not yf_sym:
        return None
    q = yf_quote(yf_sym, ac)
    return q.price if q is not None else None


def ma20(symbol: str, asset_class: str) -> Optional[float]:
    """20-day simple moving average of closes. Used by rubric.score() to audit
    the LLM's `macro_alignment` claim: LONG with price under the 20d MA (or
    SHORT with price above) is fighting the tape and should not earn the
    factor point. Returns None when history unavailable."""
    yf_sym = _yf_symbol_for(symbol, asset_class)
    if not yf_sym:
        return None
    bars = yf_history(yf_sym, days=30)
    closes = [b[4] for b in bars[-20:]]
    if len(closes) < 20:
        return None
    return sum(closes) / 20.0


def atr14(symbol: str, asset_class: str) -> Optional[float]:
    """14-day Average True Range. Used to size SL/TP off market noise instead of
    LLM-guessed numbers. Returns None if history unavailable — caller must fall
    back to a percentage-based band.

    TR = max(high-low, |high-prev_close|, |low-prev_close|); ATR = SMA(TR, 14).
    Standard Wilder-style definition; SMA (not EMA) for simplicity."""
    yf_sym = _yf_symbol_for(symbol, asset_class)
    if not yf_sym:
        return None
    bars = yf_history(yf_sym, days=30)
    if len(bars) < 15:
        return None
    trs: list[float] = []
    for i in range(1, len(bars)):
        _, _, hi, lo, _ = bars[i]
        _, _, _, _, prev_close = bars[i - 1]
        tr = max(hi - lo, abs(hi - prev_close), abs(lo - prev_close))
        trs.append(tr)
    if len(trs) < 14:
        return None
    return sum(trs[-14:]) / 14.0
