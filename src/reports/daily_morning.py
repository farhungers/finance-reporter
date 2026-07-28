"""Daily Morning report — 07:00 IST Mon-Fri (CLAUDE.md §D.1.a).

Structure (fixed order):
  1. Today's calendar (IST)
  2. Today's pitches — 3 blue-chip
  3. Today's trades — 1 commodity + 1 stock + 1 crypto

Length budget: ~1500 tokens display.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from src import calendar_source, company_names, config, db, event_explanations, market_data, news, pitches, stars, telegram_send, trades
from src.reports._style import (
    CLASS_ICON as _CLASS_ICON,
    COUNTRY_FLAG as _COUNTRY_FLAG,
    HR as _HR,
    MINI as _MINI,
    direction_dot as _direction_dot,
    fmt_num as _fmt_num,
    pad as _pad,
)

log = logging.getLogger(__name__)

esc = telegram_send.esc


def _calendar_block(events: list[calendar_source.CalendarEvent], date_ist: str) -> str:
    """3-star events only. Each event = one blockquote card with what/why line.
    Blank line between cards to break the blockquote grouping (per Telegram MDv2)."""
    todays = [e for e in events if e.date_ist == date_ist and e.importance >= 3]
    todays.sort(key=lambda e: (e.time_ist or "99:99", e.event_name))
    if not todays:
        return "_No 3\\-star events today\\._"

    cards: list[str] = []
    for e in todays:
        t = e.time_ist or "AllDay"
        flag = _COUNTRY_FLAG.get(e.country.upper(), f"`{esc(e.country[:3])}`")
        stars_str = "★" * e.importance
        # Header line: time · flag · event · stars · F/P
        friendly = event_explanations.friendly_name(e.event_name)
        head_bits = [
            f"`{esc(t)} IST`",
            flag,
            f"*{esc(friendly)}*",
            esc(stars_str),
        ]
        if e.forecast:
            head_bits.append(f"·  _F {esc(e.forecast)}_")
        if e.previous:
            head_bits.append(f"_P {esc(e.previous)}_")
        head = "  ".join(head_bits)

        why = event_explanations.explain(e.event_name)
        why_line = f"_{esc(why)}_" if why else ""

        card_lines = [f">{head}"]
        if why_line:
            card_lines.append(f">{why_line}")
        cards.append("\n".join(card_lines))
    # Blank line between blockquote cards ends the previous quote block
    return "\n\n".join(cards)


from src.reports._style import levels_table as _levels_block  # noqa: E402


def _pitch_block(pl: list[pitches.Pitch]) -> str:
    """PITCHES section: company name + ticker header, client-ready thesis prose,
    plain-English key factors. Tightened whitespace."""
    blocks: list[str] = []
    for p in pl:
        dot = _direction_dot(p.direction, p.star_rating)
        cname = company_names.name(p.asset_symbol)
        # Header: "🟢 Apple (AAPL) · LONG · 🌟🌟🌟🌟🌟"
        head = (
            f"{dot} *{esc(cname)} \\({esc(p.asset_symbol)}\\)*  ·  "
            f"_{esc(p.direction.upper())}_  ·  {stars.render(p.star_rating)}"
        )
        card: list[str] = [head]
        if p.earnings_within_3d and p.earnings_date_ist:
            impact = p.earnings_direction_expectation or "impact expected"
            card.append(f"📅 _Earnings {esc(p.earnings_date_ist)} · {esc(impact)}_")
        if p.low_star_warning:
            card.append(f"⚠️ _{esc(p.low_star_warning)}_")
        card.append(f"📖 *Thesis* — {esc(p.thesis)}")
        card.append("📍 *Key factors*")
        for kf in p.key_factors:
            card.append(f"  • {esc(kf)}")
        if p.rough_entry_hint:
            card.append(f"🎯 *Entry* — _{esc(p.rough_entry_hint)}_")
        blocks.append("\n".join(card))
    return f"\n{_MINI}\n".join(blocks)


def _trade_block(tl: list[trades.Trade]) -> str:
    order = {"commodity": 0, "equity": 1, "crypto": 2}
    tl_sorted = sorted(tl, key=lambda t: order.get(t.asset_class, 99))
    blocks: list[str] = []
    for t in tl_sorted:
        icon = _CLASS_ICON.get(t.asset_class, "•")
        dot = _direction_dot(t.direction, t.star_rating)
        head = (
            f"{icon} {dot} *{esc(t.asset_symbol)}*  ·  _{esc(t.direction.upper())}_  ·  "
            f"{stars.render(t.star_rating)}"
        )
        card: list[str] = [head]
        if t.low_star_warning:
            card.append(f"⚠️ _{esc(t.low_star_warning)}_")
        card.append(_levels_block(t.entry, t.tp, t.sl, t.direction))
        card.append(f"💡 _{esc(t.one_line_reasoning)}_")
        blocks.append("\n".join(card))
    return f"\n{_MINI}\n".join(blocks)


def _market_snapshot() -> str:
    """Compact snapshot for LLM context + light for humans. Not shown in report body directly."""
    parts = []
    for sym in ("SPY", "QQQ", "DXY", "^TNX", "^VIX"):
        # yfinance quote via market_data.yf_quote — DXY here uses DX-Y.NYB as yf symbol
        yf_sym = {"DXY": "DX-Y.NYB", "^TNX": "^TNX", "^VIX": "^VIX"}.get(sym, sym)
        q = market_data.yf_quote(yf_sym, "equity")
        if q and q.day_change_pct is not None:
            parts.append(f"{sym}={q.price:.2f} ({q.day_change_pct:+.2f}%)")
        elif q:
            parts.append(f"{sym}={q.price:.2f}")
    for name in ("GOLD", "OIL_WTI"):
        q = market_data.commodity_quote(name)
        if q:
            chg = f" ({q.day_change_pct:+.2f}%)" if q.day_change_pct is not None else ""
            parts.append(f"{name}={q.price:.2f}{chg}")
    for coin in ("BTC", "ETH"):
        q = market_data.coingecko_quote(coin)
        if q:
            chg = f" ({q.day_change_pct:+.2f}%)" if q.day_change_pct is not None else ""
            parts.append(f"{coin}={q.price:.0f}{chg}")
    return " | ".join(parts) if parts else "(market data unavailable)"


def _news_summary() -> str:
    headlines = news.fetch_headlines(max_per_feed=3)
    if not headlines:
        return "(no headlines fetched)"
    lines = [f"- [{h.source}] {h.title}" for h in headlines[:15]]
    return "\n".join(lines)


def _calendar_summary_for_llm(events: list[calendar_source.CalendarEvent], date_ist: str) -> str:
    """Unescaped compact calendar for LLM consumption (not for report body)."""
    todays = [e for e in events if e.date_ist == date_ist]
    if not todays:
        return "(no major events today)"
    return "\n".join(
        f"- {e.time_ist or 'All Day'} IST [{e.country}] {e.event_name} (impact={e.importance}, F={e.forecast}, P={e.previous})"
        for e in todays
    )


def generate(now: Optional[datetime] = None) -> tuple[str, dict]:
    """Return (message_text, telemetry). Reports never send directly — the scheduler
    calls telegram_send.send()."""
    now = now or datetime.now(config.TZ_UTC)
    now_ist = now.astimezone(config.TZ_IST)
    date_ist = now_ist.strftime("%Y-%m-%d")
    header_date = now_ist.strftime("%A, %d %b %Y")

    events = calendar_source.fetch_week()
    market_snap = _market_snapshot()
    news_sum = _news_summary()
    cal_llm = _calendar_summary_for_llm(events, date_ist)

    pitches_list, ptok = pitches.generate(date_ist, cal_llm, market_snap, news_sum)
    trades_list, ttok = trades.generate(date_ist, market_snap, cal_llm)

    calendar_block = _calendar_block(events, date_ist)

    # Tomorrow / week-ahead teasers — 3-star only
    tomorrow = (now_ist + __import__("datetime").timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_events = calendar_source.events_for_day(events, tomorrow, min_importance=3)
    tomorrow_line = (
        " · ".join(
            f"{e.time_ist or 'All Day'} {event_explanations.friendly_name(e.event_name)}"
            for e in tomorrow_events[:4]
        )
        if tomorrow_events else "no 3-star events"
    )

    header = (
        f"☀️ *MORNING BRIEFING*  ·  📅 _{esc(header_date)}_"
    )
    body = "\n".join([
        header,
        "☕ _Good morning\\._",
        _HR,
        f"🗓  *SECTION 1 · CALENDAR*  _· 3\\-star · IST_",
        _HR,
        calendar_block,
        f"📆 _Tomorrow:_ {esc(tomorrow_line)}",
        _HR,
        f"💼  *SECTION 2 · PITCHES*  _· Blue chip · 2 ideas_",
        _HR,
        _pitch_block(pitches_list),
        _HR,
        f"⚡  *SECTION 3 · TRADES*  _· 1 commodity · 1 stock · 1 crypto_",
        _HR,
        _trade_block(trades_list),
        _HR,
        "🔒 _Personal research — not investment advice\\._",
        "_Have a productive day\\._",
    ])

    telemetry = {
        "llm_tokens_in": ptok["tokens_in"] + ttok["tokens_in"],
        "llm_tokens_out": ptok["tokens_out"] + ttok["tokens_out"],
    }
    return body, telemetry
