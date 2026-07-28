"""Daily Wrap — 19:00 IST Mon-Fri (CLAUDE.md §D.1.b).

~1 min read (~400 tokens display). 19:00 IST = 12:00 ET, mid-US session.
Uses the shared visual language from src.reports._style.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from src import calendar_source, config, event_explanations, llm_client, market_data, news, telegram_send
from src.reports._style import (
    COUNTRY_FLAG,
    FOOTER,
    HR,
    report_header,
)

log = logging.getLogger(__name__)

esc = telegram_send.esc

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "one_line_summary": {"type": "string"},
        "notable_items": {
            "type": "array",
            "minItems": 0,
            "maxItems": 5,
            "items": {"type": "string"},
        },
    },
    "required": ["one_line_summary", "notable_items"],
}

_SYSTEM = """You are producing a 1-minute mid-session wrap for a Wall Street FA at 19:00 IST (12:00 ET).

Rules:
- one_line_summary: a single sentence characterizing today's tape so far. Concrete, no jokes. Plain English (a client could hear it).
- notable_items: 0-5 short bullet strings — anomalies, unusual moves, index-vs-sector divergences, notable single-stock action. Each ≤15 words. Precise, no filler. If nothing notable, return [].

Style: Bloomberg terminal note. No hype. No exclamation points."""


def _tomorrow_calendar_cards(events: list, tomorrow: str) -> str:
    """3-star events tomorrow as blockquote cards with what/why lines."""
    tomorrow_events = [e for e in events if e.date_ist == tomorrow and e.importance >= 3]
    tomorrow_events.sort(key=lambda e: (e.time_ist or "99:99", e.event_name))
    if not tomorrow_events:
        return "_No 3\\-star events scheduled\\._"

    cards: list[str] = []
    for e in tomorrow_events:
        t = e.time_ist or "AllDay"
        flag = COUNTRY_FLAG.get(e.country.upper(), f"`{esc(e.country[:3])}`")
        friendly = event_explanations.friendly_name(e.event_name)
        head_bits = [
            f"`{esc(t)} IST`",
            flag,
            f"*{esc(friendly)}*",
            esc("★" * e.importance),
        ]
        if e.forecast:
            head_bits.append(f"·  _F {esc(e.forecast)}_")
        head = "  ".join(head_bits)
        why = event_explanations.explain(e.event_name)
        lines = [head]
        if why:
            lines.append(f"_{esc(why)}_")
        cards.append("\n".join(f">{l}" for l in lines))
    return "\n\n".join(cards)


def generate(now: Optional[datetime] = None) -> tuple[str, dict]:
    now = now or datetime.now(config.TZ_UTC)
    now_ist = now.astimezone(config.TZ_IST)
    date_ist = now_ist.strftime("%Y-%m-%d")
    header_date = now_ist.strftime("%A, %d %b %Y")

    events = calendar_source.fetch_week()
    tomorrow = (now_ist + timedelta(days=1)).strftime("%Y-%m-%d")

    market_snap = _market_snapshot_wide()
    headlines = news.fetch_headlines(max_per_feed=3)
    headline_block = "\n".join(f"- [{h.source}] {h.title}" for h in headlines[:12])

    user_prompt = f"""DATE: {date_ist} IST (19:00 IST = 12:00 ET, mid-US session)

INDEX / MACRO SNAPSHOT:
{market_snap}

TODAY'S HEADLINES:
{headline_block}
"""
    result = llm_client.generate(_SYSTEM, user_prompt, _SCHEMA)
    parsed = result.parsed
    summary = parsed.get("one_line_summary", "").strip()
    notes = [n.strip() for n in parsed.get("notable_items", []) if n.strip()]

    lines: list[str] = [
        report_header("📊", "DAY WRAP", header_date),
        HR,
        f"📈 *TAPE* — {esc(summary)}" if summary else "📈 *TAPE* — _no summary produced_",
    ]
    if notes:
        lines.append(HR)
        lines.append("🔍 *NOTABLE MOVES*")
        for n in notes:
            lines.append(f"  • {esc(n)}")
    lines.append(HR)
    lines.append("📆 *TOMORROW* _· 3\\-star events · IST_")
    lines.append(_tomorrow_calendar_cards(events, tomorrow))
    lines.append(HR)
    lines.append(FOOTER)
    lines.append("🌙 _Have a good night\\._")

    text = "\n".join(lines)
    telemetry = {"llm_tokens_in": result.tokens_in, "llm_tokens_out": result.tokens_out}
    return text, telemetry


def _market_snapshot_wide() -> str:
    parts = []
    for sym in ("SPY", "QQQ", "IWM", "^VIX", "^TNX"):
        yf_sym = {"^TNX": "^TNX", "^VIX": "^VIX"}.get(sym, sym)
        q = market_data.yf_quote(yf_sym, "equity")
        if q and q.day_change_pct is not None:
            parts.append(f"{sym}={q.price:.2f} ({q.day_change_pct:+.2f}%)")
    for name in ("GOLD", "OIL_WTI", "COPPER"):
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
