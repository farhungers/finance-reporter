"""Weekly Prep — Sunday 16:00 IST (CLAUDE.md §D.1.d).

Sections (numbered):
  1. Major events this week (Mon-Fri, ≥2-star)
  2. 3-star heat map
  3. Macro setup going in (LLM-generated)
  4. Earnings this week (blue chip)
  5. Sector / theme to watch (LLM-generated)

~1200 tokens.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional

from src import calendar_source, config, earnings, event_explanations, knowledge, llm_client, telegram_send
from src.market_data import BLUE_CHIP_UNIVERSE
from src.reports._style import (
    COUNTRY_FLAG,
    FOOTER,
    HR,
    code_block,
    pad,
    report_header,
    section_banner,
)

log = logging.getLogger(__name__)

esc = telegram_send.esc

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "macro_setup_bullets": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "sector_theme_bullets": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "knowledge_sources_used": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["macro_setup_bullets", "sector_theme_bullets", "knowledge_sources_used"],
}

_SYSTEM = """You are producing a Sunday-evening horizon note for a Wall Street FA.

Rules:
- macro_setup_bullets: 3-5 short bullets naming the dominant macro themes going into the week (rates direction, DXY regime, sector rotation, cross-asset tells). Concrete, plain English, ≤20 words each. No jokes.
- sector_theme_bullets: 1-3 sector/theme angles with brief rationale drawn from the KNOWLEDGE LIBRARY. Do NOT quote knowledge chunks verbatim — transform.
- knowledge_sources_used: cite EVERY source_id from the knowledge block that shaped this note.

Style: Bloomberg terminal note. Precise. Client-readable. No hype."""

_DOW_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


def generate(now: Optional[datetime] = None) -> tuple[str, dict]:
    now = now or datetime.now(config.TZ_UTC)
    now_ist = now.astimezone(config.TZ_IST)
    week_start_dt = now_ist + timedelta(days=1)
    week_end_dt = week_start_dt + timedelta(days=4)
    week_start = week_start_dt.strftime("%Y-%m-%d")
    week_end = week_end_dt.strftime("%Y-%m-%d")

    events = calendar_source.fetch_week()
    kb = knowledge.load_for_report("weekly_prep", tickers=list(BLUE_CHIP_UNIVERSE))
    kb_ctx = knowledge.build_context_block(kb)

    by_day: dict[str, list[calendar_source.CalendarEvent]] = defaultdict(list)
    heatmap: dict[str, int] = defaultdict(int)
    for i, name in enumerate(_DOW_NAMES):
        d = (week_start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        for e in events:
            if e.date_ist == d and e.importance >= 2:
                by_day[name].append(e)
            if e.date_ist == d and e.importance >= 3:
                heatmap[name] += 1

    earnings_lines: list[tuple[str, str]] = []
    for t in BLUE_CHIP_UNIVERSE:
        ei = earnings.check_earnings(t, today=week_start_dt.date())
        if ei and week_start_dt.date() <= ei.next_earnings_date <= week_end_dt.date():
            earnings_lines.append((t, ei.next_earnings_date.isoformat()))

    user_prompt = f"""WEEK OF: {week_start} — {week_end} IST

CALENDAR (this week, ≥3-star):
{_flat_calendar_for_llm(events, week_start, week_end)}

EARNINGS (blue chip):
{chr(10).join(f'- {t}: {d}' for t, d in earnings_lines) if earnings_lines else '(none in universe)'}

{kb_ctx}

Produce the horizon note per schema."""

    result = llm_client.generate(_SYSTEM, user_prompt, _SCHEMA)
    macro = result.parsed.get("macro_setup_bullets", [])
    sectors = result.parsed.get("sector_theme_bullets", [])

    lines: list[str] = []
    lines.append(report_header("🎯", "THE HORIZON", f"Week of {week_start} — {week_end}"))

    # SECTION 1 — This week's calendar
    lines.append(section_banner(1, "📅", "THIS WEEK'S CALENDAR", "≥2-star, IST"))
    for name in _DOW_NAMES:
        day_events = by_day.get(name, [])
        if day_events:
            for e in day_events[:5]:
                flag = COUNTRY_FLAG.get(e.country.upper(), f"`{esc(e.country[:3])}`")
                stars_str = esc("★" * e.importance)
                t = e.time_ist or "AllDay"
                friendly = event_explanations.friendly_name(e.event_name)
                head = f">`{esc(t)}` {flag} *{esc(friendly)}* {stars_str}"
                why = event_explanations.explain(e.event_name)
                if e.importance >= 3 and why:
                    lines.append(f">*{esc(name)}*")
                    lines.append(head)
                    lines.append(f">_{esc(why)}_")
                else:
                    lines.append(f">*{esc(name)}*  ·  {head[1:]}")  # strip leading >
                lines.append("")  # break blockquote
        else:
            lines.append(f"_{esc(name)}: no ≥2\\-star events_")

    # SECTION 2 — 3-star heat map
    lines.append(section_banner(2, "🔥", "3-STAR HEAT MAP", None))
    if heatmap:
        heat_rows: list[str] = []
        for name in _DOW_NAMES:
            n = heatmap.get(name, 0)
            bar = "★" * n if n else "·"
            heat_rows.append(f"{pad(name, 10)} {bar}  ({n})")
        lines.append(code_block(heat_rows))
    else:
        lines.append("_No 3\\-star events this week\\._")

    # SECTION 3 — Macro setup
    lines.append(section_banner(3, "🌐", "MACRO SETUP", None))
    if macro:
        for b in macro:
            lines.append(f"  • {esc(b)}")
    else:
        lines.append("_No macro bullets produced\\._")

    # SECTION 4 — Earnings this week
    lines.append(section_banner(4, "📊", "EARNINGS THIS WEEK", "blue chip"))
    if earnings_lines:
        rows: list[str] = []
        for t, d in earnings_lines[:20]:
            rows.append(f"{pad(t, 6)} {d}")
        lines.append(code_block(rows))
    else:
        lines.append("_No earnings in universe this week\\._")

    # SECTION 5 — Sectors / themes
    lines.append(section_banner(5, "🎯", "SECTORS / THEMES", None))
    if sectors:
        for s in sectors:
            lines.append(f"  • {esc(s)}")
    else:
        lines.append("_No sector bullets produced\\._")

    lines.append(HR)
    lines.append(FOOTER)
    lines.append("📅 _Have a good week ahead\\._")
    return "\n".join(lines), {"llm_tokens_in": result.tokens_in, "llm_tokens_out": result.tokens_out}


def _flat_calendar_for_llm(events, week_start: str, week_end: str) -> str:
    filtered = [e for e in events if week_start <= e.date_ist <= week_end and e.importance >= 3]
    return "\n".join(
        f"- {e.date_ist} {e.time_ist or 'All Day'} IST [{e.country}] {e.event_name}"
        for e in filtered
    ) or "(no 3-star events)"
