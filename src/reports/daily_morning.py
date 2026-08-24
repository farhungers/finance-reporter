"""Daily Morning report — 07:00 IST Mon-Fri (CLAUDE.md §D.1.a).

Structure (fixed order):
  1. Today's calendar (IST)
  2. Today's pitches — 2 blue-chip
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


_US_DETAILED_EVENT_CAP = 3  # length-budget guardrail (Phase 4.4)
# ForexFactory uses "USD" for US events; tests + some other sources may use "US".
# Accept both so the US-detailed-format path fires consistently.
_US_COUNTRY_TAGS = frozenset({"USD", "US", "USA"})


def _calendar_block(events: list[calendar_source.CalendarEvent], date_ist: str) -> str:
    """3-star events only. US 3-star events get the full 3-line card
    (time+flag+name+stars+F/P, then What-it-is, then market effect). Non-US
    events keep the 1-line-with-market-effect card.

    Length-budget guardrail (Phase 4.4): only the first _US_DETAILED_EVENT_CAP
    US 3-star events by time render the full 3-line format; any additional
    US 3-star events fall back to the compact 1-line format so the calendar
    block cannot blow the ~1500-token morning budget on FOMC + CPI + PPI + JOLTS
    stacked days.
    """
    todays = [e for e in events if e.date_ist == date_ist and e.importance >= 3]
    todays.sort(key=lambda e: (e.time_ist or "99:99", e.event_name))
    if not todays:
        return "_No 3\\-star events today\\._"

    us_detailed_count = 0
    cards: list[str] = []
    for e in todays:
        t = e.time_ist or "AllDay"
        is_us = e.country.upper() in _US_COUNTRY_TAGS
        flag = _COUNTRY_FLAG.get(e.country.upper(), f"`{esc(e.country[:3])}`")
        stars_str = "★" * e.importance
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

        card_lines = [f">{head}"]

        # US 3-star events (up to the cap): 3-line format with what_is + effect
        if is_us and us_detailed_count < _US_DETAILED_EVENT_CAP:
            defn = event_explanations.what_is(e.event_name)
            effect = event_explanations.explain(e.event_name)
            if defn:
                card_lines.append(f">📘 _What:_ {esc(defn)}")
            if effect:
                card_lines.append(f">📈 _Effect:_ {esc(effect)}")
            us_detailed_count += 1
        else:
            # Non-US or overflow-past-cap: compact 1-line effect
            effect = event_explanations.explain(e.event_name)
            if effect:
                card_lines.append(f">_{esc(effect)}_")

        cards.append("\n".join(card_lines))
    # Blank line between blockquote cards ends the previous quote block
    return "\n\n".join(cards)


def _us_3star_event_names(events: list[calendar_source.CalendarEvent], date_ist: str) -> list[str]:
    """Return today's US 3-star event names sorted by time. Used to pass to the
    pitches generator so its LLM prompt can enforce macro-tie references and
    the knowledge loader can pull the matching playbook."""
    us_evts = [e for e in events if e.date_ist == date_ist and e.importance >= 3
               and e.country.upper() in _US_COUNTRY_TAGS]
    us_evts.sort(key=lambda e: (e.time_ist or "99:99", e.event_name))
    return [e.event_name for e in us_evts]


def _macro_focus_line(us_event_names: list[str]) -> str | None:
    """One-liner surfaced above the calendar when US 3-star events land today.
    Names the top 2 events so the FA reads them within 5 seconds of opening
    the message. Escaped for MDv2."""
    if not us_event_names:
        return None
    friendly = [event_explanations.friendly_name(n) for n in us_event_names[:2]]
    label = " · ".join(friendly)
    return f"🎯 *US FOCUS TODAY* — _{esc(label)}_"


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
    """Compact snapshot for LLM context + light for humans. Not shown in report body directly.

    2026-08-24 (roadmap Phase 2.3): prepends a computed regime label —
    DXY-vs-20d-MA trend, VIX bucket, 2s10s curve state — so the LLM has
    a pre-classified macro read to anchor the macro_alignment rubric factor
    against instead of hallucinating one from the raw snapshot."""
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
    snap = " | ".join(parts) if parts else "(market data unavailable)"
    regime = _macro_regime_label()
    return f"[REGIME] {regime}\n{snap}" if regime else snap


def _macro_regime_label() -> str:
    """Compute a compact macro regime line:
    - DXY vs 20d MA: 'DXY firm' / 'DXY soft' / 'DXY flat'
    - VIX: 'VIX calm (<15)' / 'VIX normal (15-20)' / 'VIX elevated (20-30)' / 'VIX stressed (>30)'
    - 2Y-10Y curve: 'curve inverted' / 'curve flat' / 'curve steep'

    Best-effort — any component that fails yfinance gets skipped. Returns
    a joined string like 'DXY firm · VIX normal · curve inverted' or ''
    if nothing was computed."""
    bits: list[str] = []
    # DXY trend
    dxy_spot = market_data.latest_price("DX-Y.NYB", "equity")
    dxy_ma = market_data.ma20("DX-Y.NYB", "equity")
    if dxy_spot is not None and dxy_ma is not None and dxy_ma > 0:
        delta = (dxy_spot - dxy_ma) / dxy_ma
        if delta > 0.005:
            bits.append("DXY firm")
        elif delta < -0.005:
            bits.append("DXY soft")
        else:
            bits.append("DXY flat")
    # VIX bucket
    vix = market_data.latest_price("^VIX", "equity")
    if vix is not None:
        if vix < 15:
            bits.append(f"VIX calm ({vix:.1f})")
        elif vix < 20:
            bits.append(f"VIX normal ({vix:.1f})")
        elif vix < 30:
            bits.append(f"VIX elevated ({vix:.1f})")
        else:
            bits.append(f"VIX stressed ({vix:.1f})")
    # 10Y yield direction (via ^TNX vs its 20d MA) is a reliable proxy for
    # rates regime; skipping explicit 2s10s curve since yfinance 2Y series is
    # spotty on free data and downstream is fine with the 10Y trend alone.
    tnx_spot = market_data.latest_price("^TNX", "equity")
    tnx_ma = market_data.ma20("^TNX", "equity")
    if tnx_spot is not None and tnx_ma is not None and tnx_ma > 0:
        delta = (tnx_spot - tnx_ma) / tnx_ma
        if delta > 0.01:
            bits.append(f"10Y rising ({tnx_spot / 10:.2f}%)")
        elif delta < -0.01:
            bits.append(f"10Y falling ({tnx_spot / 10:.2f}%)")
        else:
            bits.append(f"10Y range ({tnx_spot / 10:.2f}%)")
    return " · ".join(bits)


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
    us_3star_names = _us_3star_event_names(events, date_ist)

    pitches_list, ptok = pitches.generate(
        date_ist, cal_llm, market_snap, news_sum,
        todays_us_3star_events=us_3star_names,
    )
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
    macro_focus = _macro_focus_line(us_3star_names)
    body_lines = [
        header,
        "☕ _Good morning\\._",
    ]
    if macro_focus:
        body_lines.append(macro_focus)
    body_lines += [
        "",
        _HR,
        f"🗓  *SECTION 1 · CALENDAR*  _· 3\\-star · IST_",
        _HR,
        calendar_block,
        f"📆 _Tomorrow:_ {esc(tomorrow_line)}",
        "",
        _HR,
        f"💼  *SECTION 2 · PITCHES*  _· Blue chip · 2 ideas_",
        _HR,
        _pitch_block(pitches_list),
        "",
        _HR,
        f"⚡  *SECTION 3 · TRADES*  _· 1 commodity · 1 stock · 1 crypto_",
        _HR,
        _trade_block(trades_list),
        "",
        _HR,
        "🔒 _Personal research — not investment advice\\._",
        "_Have a productive day\\._",
    ]
    body = "\n".join(body_lines)

    telemetry = {
        "llm_tokens_in": ptok["tokens_in"] + ttok["tokens_in"],
        "llm_tokens_out": ptok["tokens_out"] + ttok["tokens_out"],
    }
    return body, telemetry
