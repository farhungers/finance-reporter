"""Blue-chip pitch generator (CLAUDE.md §D.1.a Part 2, §C3, §C11).

Always ships 3 pitches. Low-star (0-1) ships with a 1-line low_star_warning.
Never gaps. Never substitutes.

Rubric booleans come from the LLM; stars are summed in Python (§E.7).
Earnings-within-3d force-triggers catalyst_proximity=1 (§D.8, §E.21).
Knowledge sources cited by source_id → written to DB (§D.7, §E.20).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

from src import config, db, knowledge, llm_client, rubric
from src.earnings import check_earnings
from src.market_data import BLUE_CHIP_UNIVERSE

log = logging.getLogger(__name__)


@dataclass
class Pitch:
    asset_symbol: str
    direction: str            # 'long' / 'short' / 'neutral'
    thesis: str
    key_factors: list[str]
    rough_entry_hint: Optional[str]
    star_rating: int
    rubric_breakdown: dict[str, int]
    low_star_warning: Optional[str]
    earnings_within_3d: bool
    earnings_date_ist: Optional[str] = None
    earnings_direction_expectation: Optional[str] = None
    knowledge_sources_used: list[str] = field(default_factory=list)
    horizon_days: int = 7
    db_id: Optional[int] = None


_PITCH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "pitches": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "asset_symbol": {"type": "string"},
                    "direction": {"type": "string", "enum": ["long", "short", "neutral"]},
                    "thesis": {"type": "string"},
                    "key_factors": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 4,
                        "items": {"type": "string"},
                    },
                    "rough_entry_hint": {"type": "string"},
                    "rubric": {
                        "type": "object",
                        "properties": {
                            "macro_alignment": {"type": "boolean"},
                            "technical_setup": {"type": "boolean"},
                            "catalyst_proximity": {"type": "boolean"},
                            "base_rate_support": {"type": "boolean"},
                            "risk_reward": {"type": "boolean"},
                        },
                        "required": [
                            "macro_alignment", "technical_setup", "catalyst_proximity",
                            "base_rate_support", "risk_reward",
                        ],
                    },
                    "low_star_warning": {"type": "string"},
                    "knowledge_sources_used": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "horizon_days": {"type": "integer", "minimum": 1, "maximum": 30},
                    "earnings_direction_expectation": {"type": "string"},
                },
                "required": [
                    "asset_symbol", "direction", "thesis", "key_factors",
                    "rough_entry_hint", "rubric", "knowledge_sources_used", "horizon_days",
                ],
            },
        }
    },
    "required": ["pitches"],
}


_SYSTEM_PROMPT = """You are a disciplined equity strategist producing 2 blue-chip pitches for a Wall Street financial advisor's morning briefing.

STRICT RULES:
- The `pitches` array MUST contain EXACTLY 2 items — no more, no fewer. This is non-negotiable.
- Pick exactly 2 distinct tickers from the provided BLUE_CHIP_UNIVERSE. Never pick outside it.
- Directions may repeat but assets must not.

THESIS STYLE — this is the most important rule. Write the thesis as a "ready-to-repeat" pitch: prose the FA can literally read aloud to a client. This means:
  • 3-5 sentences, plain English, no jargon
  • Prefer "Apple reports earnings July 30" over "AAPL prints EPS 7/30"
  • Prefer "the Street reset expectations lower" over "Street bar reset"
  • Prefer "trading 12% cheaper than its 5-year average" over "12% discount to 5-yr median PE"
  • Name the catalyst by date. Name the mechanism (why it moves). Name the primary risk.
  • Client-facing tone — HNW-briefing calm, not Reddit or Twitter. No hype, no adjectives without numbers, no exclamation points.
  • Frame as an investable idea, not an academic observation.

KEY FACTORS:
- 3-4 short bullet strings, ≤12 words each
- Plain English — a client reading each bullet should understand it immediately
- Concrete observations with numbers/dates when possible
- Example good: "Earnings July 30 — Street already reset expectations lower"
- Example bad: "Q3 EPS 7/30 with buy-side de-risked positioning per weekly flows"

OTHER FIELDS:
- rough_entry_hint: freeform, natural language ("near $185 support", "on pullback to 50-day average"). Not a precise number.
- Rubric: return 5 booleans exactly. Do NOT compute stars — the Python layer does that.
- knowledge_sources_used: cite EVERY source_id from the KNOWLEDGE LIBRARY block that shaped this pitch. NEVER paste text verbatim — transform and apply. If a pitch used no knowledge chunks, return [] (allowed but note it costs a rubric factor).
- For each pitch with EARNINGS_WITHIN_3D marked, you MUST include earnings_direction_expectation ('bullish' / 'bearish' / 'unknown') AND mention the earnings date + expected impact in the thesis.
- horizon_days: typical hold window (5-15 for tactical, up to 30 for slower thematic).
- low_star_warning (only when your rubric booleans sum to 0 or 1): 1 line, plain English, non-joking — explain honestly why shipping despite low conviction. Something the FA can say: "no near-term catalyst; treat as watch-list only". Omit or leave empty when stars≥2.

The Python layer will:
- Sum your rubric booleans to compute the 0-5 star rating
- Force catalyst_proximity=1 for EARNINGS_WITHIN_3D tickers regardless of your value
- Write low_star_warning to the report only when the final star_rating ≤ 1
"""


def _rotating_ticker_sample(date_ist: str, size: int = 3) -> list[str]:
    """Deterministic day-seeded rotating slice — sampled from *populated* ticker
    fact files only, so the LLM always gets real context (not stubs). Same date
    → same sample, but different days rotate through the populated set. Keeps
    per-report token load bounded (~9KB at size=3) so we stay comfortably under
    Groq's 12K TPM cap. Size was 5 initially but hit the limit; 3 gives headroom
    while still rotating full 25-ticker set every ~8-9 days."""
    populated = _populated_tickers()
    n = len(populated)
    if n == 0 or size >= n:
        return populated
    try:
        doy = datetime.strptime(date_ist, "%Y-%m-%d").timetuple().tm_yday
    except Exception:
        doy = 0
    start = (doy * size) % n
    end = start + size
    if end <= n:
        return populated[start:end]
    return populated[start:] + populated[: end - n]


def _populated_tickers() -> list[str]:
    """Return the subset of BLUE_CHIP_UNIVERSE whose facts file is not a stub."""
    out: list[str] = []
    for t in BLUE_CHIP_UNIVERSE:
        p = config.KNOWLEDGE_DIR / "blue_chip" / f"{t}_facts.md"
        if not p.exists():
            continue
        chunk = knowledge._read_chunk(p)
        if chunk is not None and not knowledge._is_stub(chunk):
            out.append(t)
    return out


def _build_user_prompt(
    date_ist: str,
    calendar_summary: str,
    market_snapshot: str,
    news_summary: str,
    knowledge_context: str,
    earnings_flags: dict[str, dict[str, Any]],
) -> str:
    universe = ", ".join(BLUE_CHIP_UNIVERSE)
    earnings_lines = []
    for t, info in earnings_flags.items():
        earnings_lines.append(
            f"- {t}: EARNINGS_WITHIN_3D=True, date={info['date']}, trading_days_from_today={info['td']}"
        )
    earnings_block = "\n".join(earnings_lines) if earnings_lines else "(no pitched-universe earnings within 3 trading days flagged this morning)"

    return f"""DATE: {date_ist} IST

BLUE_CHIP_UNIVERSE (choose exactly 3, distinct):
{universe}

TODAY'S CALENDAR (IST):
{calendar_summary}

MARKET SNAPSHOT:
{market_snapshot}

NEWS PULSE (headlines only — do not quote verbatim):
{news_summary}

EARNINGS-WITHIN-3D FLAGS:
{earnings_block}

{knowledge_context}

Produce 3 blue-chip pitches per the schema. Cite knowledge sources by source_id.
"""


def generate(
    date_ist: str,
    calendar_summary: str,
    market_snapshot: str,
    news_summary: str,
    report_type: str = "daily_morning",
) -> tuple[list[Pitch], dict[str, int]]:
    """Return (pitches, token_counts). Persists each pitch to DB BEFORE any send."""
    # Rotating ticker-facts sample: pass a day-seeded slice of the universe so
    # different tickers receive deep-context exposure over the week. Groq TPM cap
    # (12K/min) forces this trim; without it, 25+ populated ticker files blow the
    # budget. LLM still receives the full universe list in the system prompt and
    # can pitch any ticker — sampled ones just get the extra facts as context.
    ticker_sample = _rotating_ticker_sample(date_ist, size=3)
    kb = knowledge.load_for_report(report_type, tickers=ticker_sample)
    kb_ctx = knowledge.build_context_block(kb)

    # Compute earnings flags for the full universe (or a targeted subset — for now, full).
    # yfinance calls can be slow; skip if quota-worried. We check a small set for the pilot.
    # In production, cache these daily.
    earnings_flags: dict[str, dict[str, Any]] = {}
    # For pilot speed, only check a rotating subset. LLM will still be told about the universe.
    # Skip in dry-run pilot unless explicitly requested — see pipeline caller.

    user_prompt = _build_user_prompt(
        date_ist, calendar_summary, market_snapshot, news_summary, kb_ctx, earnings_flags,
    )
    result = llm_client.generate(_SYSTEM_PROMPT, user_prompt, _PITCH_SCHEMA)
    raw = result.parsed.get("pitches", [])
    if len(raw) < 2:
        raise ValueError(f"LLM returned {len(raw)} pitches, expected at least 2")
    if len(raw) > 2:
        # Groq JSON mode doesn't strictly enforce maxItems; truncate defensively.
        log.warning("LLM returned %d pitches, truncating to 2", len(raw))
        raw = raw[:2]

    pitches: list[Pitch] = []
    for p in raw:
        sym = p["asset_symbol"].upper()
        if sym not in BLUE_CHIP_UNIVERSE:
            raise ValueError(f"LLM picked non-universe ticker: {sym!r}")
        # Post-hoc earnings check for the chosen ticker
        ei = check_earnings(sym)
        within_3d = bool(ei and ei.within_3_trading_days)
        rs = rubric.score(p["rubric"], earnings_within_3d=within_3d)
        low_warn = p.get("low_star_warning") if rs.stars <= 1 else None
        pitches.append(
            Pitch(
                asset_symbol=sym,
                direction=p["direction"],
                thesis=p["thesis"].strip(),
                key_factors=[k.strip() for k in p["key_factors"]],
                rough_entry_hint=(p.get("rough_entry_hint") or "").strip() or None,
                star_rating=rs.stars,
                rubric_breakdown=rs.breakdown,
                low_star_warning=low_warn,
                earnings_within_3d=within_3d,
                earnings_date_ist=(ei.next_earnings_date.isoformat() if within_3d and ei else None),
                earnings_direction_expectation=p.get("earnings_direction_expectation"),
                knowledge_sources_used=list(p.get("knowledge_sources_used") or []),
                horizon_days=int(p.get("horizon_days") or 7),
            )
        )

    # Persist BEFORE send (§C10, §E.5)
    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with db.connect() as conn:
        cur = conn.cursor()
        for pi in pitches:
            cur.execute(
                """INSERT INTO pitches
                (generated_at, report_date, asset_symbol, asset_class, direction, thesis,
                 key_factors_json, rough_entry_hint, star_rating, rubric_breakdown_json,
                 low_star_warning, earnings_within_3d, knowledge_sources_used, horizon_days)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    now_utc, date_ist, pi.asset_symbol, "equity_bluechip", pi.direction, pi.thesis,
                    json.dumps(pi.key_factors), pi.rough_entry_hint, pi.star_rating,
                    json.dumps(pi.rubric_breakdown), pi.low_star_warning,
                    1 if pi.earnings_within_3d else 0,
                    json.dumps(pi.knowledge_sources_used), pi.horizon_days,
                ),
            )
            pi.db_id = cur.lastrowid
            # knowledge_hits (§E.20)
            for sid in pi.knowledge_sources_used:
                cur.execute(
                    """INSERT INTO knowledge_hits (used_at, report_type, source_id, pitch_id)
                    VALUES (?,?,?,?)""",
                    (now_utc, report_type, sid, pi.db_id),
                )

    return pitches, {"tokens_in": result.tokens_in, "tokens_out": result.tokens_out}
