"""MARKET WIRE — 3 news-analysis blocks for the daily morning briefing (§D.1.a §C11).

Each item = one headline the FA can read to a client. Format:
  Lead      → 1 sentence, dated, quantitative when possible
  Significance → 2-3 sentences explaining WHY it matters (mechanism)
  Impact    → cross-asset directions (USD / gold / stocks / crypto / key sector)

Sources (free only, §G):
  (a) Today's 3-star calendar events + forecast/prior deltas
  (b) Filtered RSS headlines (macro/rates/geopol keywords) via news.fetch_headlines

Grounded by knowledge/macro/impact_matrix.md so impact directions are
mechanism-linked rather than vibes. LLM MUST NOT paste knowledge text
verbatim — must transform/apply (§D.7).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

from src import calendar_source, config, db, knowledge, llm_client, news
from src.event_explanations import friendly_name

log = logging.getLogger(__name__)


# Emoji / country vocabulary — tightly bounded so the schema enum matches
# telegram render and knowledge_hits stays greppable.
_COUNTRY_FLAGS: dict[str, str] = {
    "US": "🇺🇸", "EU": "🇪🇺", "UK": "🇬🇧", "JP": "🇯🇵",
    "CN": "🇨🇳", "GLOBAL": "🌐",
}
_LEAD_EMOJI: frozenset[str] = frozenset({"🔴", "🟡", "🟢", "🔵", "⚪"})
_IMPACT: frozenset[str] = frozenset({"+", "-", "~"})


@dataclass
class WireItem:
    country_code: str            # US / EU / UK / JP / CN / GLOBAL
    lead_emoji: str              # 🔴 alarm | 🟡 watch | 🟢 positive | 🔵 neutral | ⚪ meta
    headline: str                # 1 sentence
    significance: str            # 2-3 sentences
    impact_usd: str              # + / - / ~
    impact_gold: str
    impact_stocks: str
    impact_crypto: str
    key_sector: str              # optional; empty string when N/A
    knowledge_sources_used: list[str] = field(default_factory=list)


# ---------- headline filtering ----------------------------------------------

# Keywords that mark a headline as macro/rates/geopol-relevant (worth showing
# to the LLM). Everything else is single-name earnings chatter or opinion
# columns that shouldn't shape the wire.
_MACRO_KWS: tuple[str, ...] = (
    "fed", "powell", "fomc", "rate", "yield", "treasury", "bond", "cpi",
    "inflation", "pce", "ppi", "jobs", "payroll", "unemployment", "jolts",
    "gdp", "recession", "ism", "pmi", "dollar", "dxy", "yuan", "yen",
    "ecb", "boj", "boe", "lagarde", "opec", "oil", "crude", "gold",
    "bitcoin", "crypto", "tariff", "trade war", "china", "russia",
    "ukraine", "iran", "middle east", "sanction", "geopolit",
    "sovereign", "downgrade", "s&p 500", "nasdaq", "vix", "risk-off",
    "risk on", "safe haven", "auction", "bid-to-cover", "debt ceiling",
    "shutdown", "election", "trump", "biden",
)


def _is_macro_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in _MACRO_KWS)


def _filtered_headlines(cap: int = 12) -> list[news.Headline]:
    """Return the top `cap` macro-relevant headlines. Filter is coarse — the
    LLM makes the final pick; this just avoids paying tokens for single-name
    noise."""
    hl = news.fetch_headlines(max_per_feed=4)
    filtered = [h for h in hl if _is_macro_relevant(h.title)]
    # Dedupe by title (RSS feeds often cross-post the same wire story)
    seen: set[str] = set()
    out: list[news.Headline] = []
    for h in filtered:
        key = re.sub(r"\s+", " ", h.title.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
        if len(out) >= cap:
            break
    return out


def _calendar_lines_for_llm(
    events: list[calendar_source.CalendarEvent], date_ist: str
) -> str:
    todays = [e for e in events if e.date_ist == date_ist and e.importance >= 3]
    todays.sort(key=lambda e: (e.time_ist or "99:99", e.event_name))
    if not todays:
        return "(no 3-star events today)"
    return "\n".join(
        f"- {e.time_ist or 'AllDay'} [{e.country}] {friendly_name(e.event_name)} "
        f"(F={e.forecast}, P={e.previous})"
        for e in todays
    )


# ---------- schema ----------------------------------------------------------

# Named-slot schema (item_1..item_3) matches the pitches.py pattern — Groq's
# strict json_schema decoder does NOT reliably enforce array minItems, so we
# use required top-level keys instead. Enums keep the impact direction from
# drifting into free text.
_WIRE_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "country_code": {
            "type": "string",
            "enum": ["US", "EU", "UK", "JP", "CN", "GLOBAL"],
        },
        "lead_emoji": {
            "type": "string",
            "enum": ["🔴", "🟡", "🟢", "🔵", "⚪"],
        },
        "headline": {"type": "string"},
        "significance": {"type": "string"},
        "impact_usd": {"type": "string", "enum": ["+", "-", "~"]},
        "impact_gold": {"type": "string", "enum": ["+", "-", "~"]},
        "impact_stocks": {"type": "string", "enum": ["+", "-", "~"]},
        "impact_crypto": {"type": "string", "enum": ["+", "-", "~"]},
        "key_sector": {"type": "string"},
        "knowledge_sources_used": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "country_code", "lead_emoji", "headline", "significance",
        "impact_usd", "impact_gold", "impact_stocks", "impact_crypto",
        "key_sector", "knowledge_sources_used",
    ],
}

_WIRE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "item_1": _WIRE_ITEM_SCHEMA,
        "item_2": _WIRE_ITEM_SCHEMA,
        "item_3": _WIRE_ITEM_SCHEMA,
    },
    "required": ["item_1", "item_2", "item_3"],
}


_SYSTEM_PROMPT = """You are the market-wire desk producing 3 news-analysis blocks for a Wall Street financial advisor's morning briefing.

STRICT RULES:
- Output MUST contain EXACTLY three top-level keys: `item_1`, `item_2`, `item_3`. All three are non-negotiable.
- Rank by significance to a US-focused, rates-sensitive, blue-chip-equity-focused portfolio. Item 1 is the biggest driver.
- Do NOT duplicate topics across items (one item on rates, one on inflation, one on geopolitics — not three rates items).
- Prefer TODAY'S SCHEDULED CALENDAR EVENTS as sources when they exist; use RSS headlines to fill the remaining slots. Never gap — if you have fewer than 3 clean stories, ship the best available and mark the weakest with lead_emoji '⚪' (meta / low-conviction).

HEADLINE STYLE — write for a client to hear aloud:
  • ONE sentence
  • Dated when possible ("as of Monday's close", "at the 08:30 ET release")
  • Quantitative when possible ("5.35%", "230K jobs", "+0.4% MoM")
  • Plain English — no jargon a client wouldn't know
  • Good: "The 30-year US Treasury yield hit 5.35%, its highest since June 2007."
  • Bad: "USTs bear-steepened on TIC selling pressure into duration."

SIGNIFICANCE STYLE — 2-3 sentences:
  • Explain the MECHANISM (why this moves markets), not just the fact
  • Anchor to today's regime — cite the DXY / VIX / 10Y state from MARKET SNAPSHOT
  • Reference the impact_matrix mechanism (e.g. "higher real yields raise the discount rate on growth multiples")
  • Never paste text verbatim from the knowledge library — transform + apply
  • Good: "This matters because higher real yields raise the discount rate on future cash flows, compressing growth multiples first (Nasdaq > S&P). With DXY firm and VIX calm, the flow is orderly rotation from duration equities into banks and value, not a broad risk-off event."
  • Bad: "Yields going up is bad for stocks."

IMPACT LINE — cross-asset directions using ONLY the enum values:
  '+' = the asset typically appreciates on this driver
  '−' = the asset typically depreciates
  '~' = mixed or magnitude-dependent — use this when honest
Directions MUST match the impact_matrix.md tables loaded in KNOWLEDGE LIBRARY (or be explicitly justified in Significance when today's regime overrides the default). Do NOT invent directions to sound confident.

KEY SECTOR — optional string:
  • Name ONE sector where second-order impact is loudest ("Real Estate", "Banks", "Energy", "Homebuilders", "Utilities", "Tech Growth")
  • Add sign for magnitude ("Real Estate −−", "Energy ++")
  • Empty string when nothing stands out — do not stretch

COUNTRY CODE — enum: US / EU / UK / JP / CN / GLOBAL
  • Use GLOBAL for cross-border stories (oil, crypto-native, war escalation)

LEAD EMOJI — enum:
  🔴 = alarm / large negative surprise / risk-off catalyst
  🟡 = watch / meaningful development but not yet moving markets
  🟢 = positive surprise / risk-on catalyst
  🔵 = neutral / informational (scheduled release with no surprise yet)
  ⚪ = meta / low-conviction filler (used when the wire is a slow day)

KNOWLEDGE SOURCES — cite EVERY source_id from KNOWLEDGE LIBRARY that shaped this item. The impact_matrix.md source is expected on every item that gives cross-asset directions. Empty list = you didn't use any (rare — impact_matrix should almost always cite).

STYLE (§C12): precise, easy to understand, no jokes, no exclamation points, no hedging like "may perhaps possibly". Confidence is expressed by the impact directions and lead_emoji, not by adjective inflation.
"""


def _build_user_prompt(
    date_ist: str,
    calendar_summary: str,
    market_snapshot: str,
    headlines: list[news.Headline],
    knowledge_context: str,
) -> str:
    if headlines:
        headline_lines = "\n".join(
            f"- [{h.source}] {h.title}" for h in headlines
        )
    else:
        headline_lines = "(no macro-relevant RSS headlines fetched)"
    return f"""DATE: {date_ist} IST

MARKET SNAPSHOT (use REGIME line for context):
{market_snapshot}

TODAY'S 3-STAR CALENDAR EVENTS (IST):
{calendar_summary}

MACRO-FILTERED RSS HEADLINES (recent, deduped):
{headline_lines}

{knowledge_context}

Produce 3 wire items — one as `item_1`, one as `item_2`, one as `item_3`. Rank by significance. Cite knowledge sources by source_id.
"""


def generate(
    date_ist: str,
    events: list[calendar_source.CalendarEvent],
    market_snapshot: str,
) -> tuple[list[WireItem], dict[str, int]]:
    """Return (wire_items, token_counts). Sequential 3rd LLM call in
    daily_morning after pitches + trades. Trim knowledge to keep the prompt
    under Groq's 8K TPM cap."""
    cal_summary = _calendar_lines_for_llm(events, date_ist)
    headlines = _filtered_headlines(cap=12)

    # Load impact_matrix + active_themes only — no ticker facts (wire is macro).
    kb = knowledge.load_for_report("daily_morning", tickers=[])
    # Force-include impact_matrix if it wasn't picked up by applies_to_reports.
    matrix_path = config.KNOWLEDGE_DIR / "macro" / "impact_matrix.md"
    if matrix_path.exists():
        chunk = knowledge._read_chunk(matrix_path)
        if chunk and chunk.body and not knowledge._is_stub(chunk):
            kb[chunk.source_id] = chunk.body

    # Char budget mirrors pitches._trim_knowledge_to_budget rationale: system
    # ~1500 tokens + user frame ~500 + 2500 completion reservation → ~3000
    # tokens of knowledge headroom = ~9000 chars. impact_matrix is ~5KB, so
    # this fits with room for active_themes.
    if sum(len(b) for b in kb.values()) > 9000:
        by_size = sorted(kb.items(), key=lambda kv: -len(kv[1]))
        kept = dict(kb)
        total = sum(len(b) for b in kb.values())
        for sid, body in by_size:
            if total <= 9000:
                break
            # Never drop impact_matrix — it's the whole point of grounding
            if sid.endswith("impact_matrix.md"):
                continue
            log.warning("market_wire trim: dropping %s (%d chars)", sid, len(body))
            del kept[sid]
            total -= len(body)
        kb = kept
    kb_ctx = knowledge.build_context_block(kb)

    user_prompt = _build_user_prompt(
        date_ist, cal_summary, market_snapshot, headlines, kb_ctx,
    )
    result = llm_client.generate(_SYSTEM_PROMPT, user_prompt, _WIRE_SCHEMA)
    parsed = result.parsed
    for k in ("item_1", "item_2", "item_3"):
        if k not in parsed:
            raise ValueError(f"market_wire LLM output missing {k}: keys={list(parsed.keys())}")

    items: list[WireItem] = []
    for k in ("item_1", "item_2", "item_3"):
        raw = parsed[k]
        # Defensive coercion in case the model emits an unexpected enum value —
        # never blocks a ship (§C11), just falls back to a safe default.
        cc = raw["country_code"] if raw.get("country_code") in _COUNTRY_FLAGS else "GLOBAL"
        emoji = raw["lead_emoji"] if raw.get("lead_emoji") in _LEAD_EMOJI else "⚪"

        def _clean_impact(v: str) -> str:
            return v if v in _IMPACT else "~"

        items.append(
            WireItem(
                country_code=cc,
                lead_emoji=emoji,
                headline=(raw.get("headline") or "").strip(),
                significance=(raw.get("significance") or "").strip(),
                impact_usd=_clean_impact(raw.get("impact_usd", "~")),
                impact_gold=_clean_impact(raw.get("impact_gold", "~")),
                impact_stocks=_clean_impact(raw.get("impact_stocks", "~")),
                impact_crypto=_clean_impact(raw.get("impact_crypto", "~")),
                key_sector=(raw.get("key_sector") or "").strip(),
                knowledge_sources_used=list(raw.get("knowledge_sources_used") or []),
            )
        )

    # §E.20: every knowledge citation logs to knowledge_hits so the weekly
    # look-back can correlate sources with outcomes. Wire items have no
    # pitch_id/trade_id — both stay NULL, distinguishing wire citations from
    # pitch/trade citations in the same table.
    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with db.connect() as conn:
        cur = conn.cursor()
        for it in items:
            for sid in it.knowledge_sources_used:
                cur.execute(
                    """INSERT INTO knowledge_hits (used_at, report_type, source_id)
                    VALUES (?,?,?)""",
                    (now_utc, "daily_morning_wire", sid),
                )

    return items, {"tokens_in": result.tokens_in, "tokens_out": result.tokens_out}


def country_flag(cc: str) -> str:
    """Return the flag emoji for a country_code. Renderer helper — used by
    daily_morning._wire_block()."""
    return _COUNTRY_FLAGS.get(cc, "🌐")
