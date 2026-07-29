"""Accuracy resolver + stats aggregator (CLAUDE.md §D.3, §E.8).

Two entry points:
  - resolve_open_positions(): batch resolver, called before weekly look-back
  - stats_snapshot(): read-only aggregator, feeds /stats AND weekly look-back rendering

Rule: no writeback to generator. resolution/realized_* fields are append-once.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Optional

from src import db
from src.market_data import yf_history, coingecko_quote

log = logging.getLogger(__name__)

_TRADE_EXPIRY_DAYS = 5   # trading days
_PITCH_MOVE_THRESHOLD_PCT = 2.0


@dataclass
class Stats:
    pitches_open: int = 0
    pitches_resolved: int = 0
    pitches_by_star: dict[int, dict[str, int]] = field(default_factory=dict)  # {stars: {resolution: n}}
    trades_open: int = 0
    trades_resolved: int = 0
    trades_by_class: dict[str, dict[str, int]] = field(default_factory=dict)  # {class: {resolution: n}}
    trades_hit_tp: int = 0
    trades_hit_sl: int = 0
    trades_expired: int = 0
    trades_avg_r: Optional[float] = None
    open_positions: list[dict] = field(default_factory=list)  # summarized open trades/pitches


def _trading_days_between(d0: date, d1: date) -> int:
    if d1 <= d0:
        return 0
    days = 0
    cur = d0
    while cur < d1:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            days += 1
    return days


def resolve_open_positions(as_of: Optional[datetime] = None) -> tuple[int, int]:
    """Resolve still-open trades and pitches. Returns (n_trades_resolved, n_pitches_resolved).
    Append-only: never rewrites an already-resolved row."""
    as_of = as_of or datetime.now(UTC)
    n_trades = _resolve_trades(as_of)
    n_pitches = _resolve_pitches(as_of)
    return n_trades, n_pitches


def _resolve_trades(as_of: datetime) -> int:
    n = 0
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT * FROM trades WHERE resolution IS NULL OR resolution = 'still_open'"""
        ).fetchall()
        for r in rows:
            gen_at = datetime.fromisoformat(r["generated_at"].replace("Z", ""))
            gen_date = gen_at.date()
            elapsed_td = _trading_days_between(gen_date, as_of.date())

            hist = _history_for_asset(r["asset_symbol"], r["asset_class"], gen_date)
            if not hist:
                continue

            hit = _check_tp_sl(r["direction"], float(r["entry"]), float(r["tp"]), float(r["sl"]), hist)
            if hit is None and elapsed_td >= _TRADE_EXPIRY_DAYS:
                hit = ("expired", None)
            if hit is None:
                continue

            resolution, realized_r = hit
            conn.execute(
                """UPDATE trades SET resolved_at=?, resolution=?, realized_r=? WHERE id=?""",
                (as_of.strftime("%Y-%m-%dT%H:%M:%SZ"), resolution, realized_r, r["id"]),
            )
            n += 1
    return n


def _resolve_pitches(as_of: datetime) -> int:
    n = 0
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT * FROM pitches WHERE resolution IS NULL OR resolution = 'still_open'"""
        ).fetchall()
        for r in rows:
            gen_at = datetime.fromisoformat(r["generated_at"].replace("Z", ""))
            horizon = int(r["horizon_days"] or 7)
            elapsed_td = _trading_days_between(gen_at.date(), as_of.date())
            if elapsed_td < horizon:
                continue

            hist = _history_for_asset(r["asset_symbol"], "equity", gen_at.date())
            if not hist:
                continue
            entry_price = hist[0][4]  # first close post-generation
            end_price = hist[-1][4]
            pct = (end_price - entry_price) / entry_price * 100.0
            direction = r["direction"]
            aligned = pct if direction == "long" else -pct
            if aligned >= _PITCH_MOVE_THRESHOLD_PCT:
                resolution = "thesis_played_out"
            elif aligned <= -_PITCH_MOVE_THRESHOLD_PCT:
                resolution = "thesis_failed"
            else:
                resolution = "noise"

            conn.execute(
                """UPDATE pitches SET resolved_at=?, resolution=?, realized_pct=? WHERE id=?""",
                (as_of.strftime("%Y-%m-%dT%H:%M:%SZ"), resolution, pct, r["id"]),
            )
            n += 1
    return n


def _history_for_asset(symbol: str, asset_class: str, since: date) -> list[tuple[date, float, float, float, float]]:
    days = (date.today() - since).days + 3
    days = max(days, 7)
    if asset_class == "crypto":
        # CoinGecko free API doesn't give clean daily OHLC via /simple/price.
        # Full historical OHLC would need /coins/{id}/market_chart — for pilot,
        # fall back to yfinance for crypto tickers formatted as e.g. 'BTC-USD'.
        yf_sym = f"{symbol}-USD"
        return yf_history(yf_sym, days=days)
    return yf_history(symbol, days=days)


def _check_tp_sl(
    direction: str, entry: float, tp: float, sl: float,
    hist: list[tuple[date, float, float, float, float]],
) -> Optional[tuple[str, float]]:
    """Return ('hit_tp'|'hit_sl', realized_r) if hit, else None. If both hit in same
    bar, assume worst (SL) — conservative accounting."""
    r_denom = abs(entry - sl)
    if r_denom == 0:
        return None
    for _, o, h, l, c in hist:
        if direction == "long":
            if l <= sl:
                realized_r = (sl - entry) / r_denom
                return ("hit_sl", realized_r)
            if h >= tp:
                realized_r = (tp - entry) / r_denom
                return ("hit_tp", realized_r)
        else:
            if h >= sl:
                realized_r = (entry - sl) / r_denom
                return ("hit_sl", realized_r)
            if l <= tp:
                realized_r = (entry - tp) / r_denom
                return ("hit_tp", realized_r)
    return None


def stats_snapshot() -> Stats:
    s = Stats()
    with db.connect() as conn:
        # Pitches
        for row in conn.execute("SELECT star_rating, resolution FROM pitches"):
            star = int(row["star_rating"])
            res = row["resolution"] or "still_open"
            if res == "still_open":
                s.pitches_open += 1
            else:
                s.pitches_resolved += 1
            s.pitches_by_star.setdefault(star, {}).setdefault(res, 0)
            s.pitches_by_star[star][res] = s.pitches_by_star[star][res] + 1

        # Trades
        r_sum = 0.0
        r_n = 0
        for row in conn.execute("SELECT asset_class, resolution, realized_r FROM trades"):
            klass = row["asset_class"]
            res = row["resolution"] or "still_open"
            if res == "still_open":
                s.trades_open += 1
            else:
                s.trades_resolved += 1
            if res == "hit_tp":
                s.trades_hit_tp += 1
            elif res == "hit_sl":
                s.trades_hit_sl += 1
            elif res == "expired":
                s.trades_expired += 1
            s.trades_by_class.setdefault(klass, {}).setdefault(res, 0)
            s.trades_by_class[klass][res] = s.trades_by_class[klass][res] + 1
            if row["realized_r"] is not None:
                r_sum += float(row["realized_r"])
                r_n += 1
        s.trades_avg_r = (r_sum / r_n) if r_n else None

        # Open positions summary
        for row in conn.execute(
            """SELECT id, asset_symbol, asset_class, direction, entry, tp, sl, generated_at
            FROM trades WHERE resolution IS NULL OR resolution='still_open' ORDER BY generated_at DESC LIMIT 10"""
        ):
            gen = datetime.fromisoformat(row["generated_at"].replace("Z", "+00:00"))
            age = (datetime.now(UTC) - gen).days
            s.open_positions.append({
                "kind": "trade",
                "symbol": row["asset_symbol"],
                "class": row["asset_class"],
                "direction": row["direction"],
                "entry": float(row["entry"]),
                "age_days": age,
            })
        for row in conn.execute(
            """SELECT id, asset_symbol, direction, generated_at, star_rating
            FROM pitches WHERE resolution IS NULL OR resolution='still_open' ORDER BY generated_at DESC LIMIT 10"""
        ):
            gen = datetime.fromisoformat(row["generated_at"].replace("Z", "+00:00"))
            age = (datetime.now(UTC) - gen).days
            s.open_positions.append({
                "kind": "pitch",
                "symbol": row["asset_symbol"],
                "direction": row["direction"],
                "stars": int(row["star_rating"]),
                "age_days": age,
            })

    return s
