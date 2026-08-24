"""Blue-chip pitch generator (CLAUDE.md §D.1.a Part 2, §C3, §C11).

Always ships 2 pitches. Low-star (0-1) ships with a 1-line low_star_warning.
Never gaps. Never substitutes.

Rubric booleans come from the LLM; stars are summed in Python (§E.7).
Earnings-within-3d force-triggers catalyst_proximity=1 (§D.8, §E.21).
Knowledge sources cited by source_id → written to DB (§D.7, §E.20).
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

from src import config, db, knowledge, llm_client, market_data, rubric
from src.earnings import check_earnings
from src.market_data import BLUE_CHIP_UNIVERSE

log = logging.getLogger(__name__)

# §D.8 belt-and-suspenders: when a pitch is flagged EARNINGS_WITHIN_3D, the
# thesis MUST mention the earnings date. A missing mention is a spec violation
# — the LLM said "earnings soon" without wiring the actual date, which is the
# exact hallucination surface §D.8 exists to close.
_MONTH_TOKEN = re.compile(
    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b",
    re.IGNORECASE,
)
_NUMERIC_DATE = re.compile(r"\b\d{1,2}[/-]\d{1,2}\b")


def _thesis_mentions_date(thesis: str) -> bool:
    return bool(_MONTH_TOKEN.search(thesis) or _NUMERIC_DATE.search(thesis))


# 2026-08-24 roadmap Phase 2.2: when today's US calendar carries a 3-star event,
# the thesis must reference it (name substring, acronym, or its playbook topic).
# Keys are the substrings we look for in event names; values are the aliases the
# LLM might use. Warning-only per §C11 (never omit) but written to logs so
# operator sees drift, matching the earnings-date enforcement pattern.
_MACRO_EVENT_ALIASES: dict[str, tuple[str, ...]] = {
    "cpi": ("cpi", "inflation", "price index", "consumer price"),
    "core cpi": ("cpi", "core inflation", "sticky inflation"),
    "pce": ("pce", "personal consumption", "fed's preferred", "inflation target"),
    "core pce": ("pce", "core inflation", "fed's preferred"),
    "ppi": ("ppi", "producer price", "input cost"),
    "nfp": ("nfp", "payroll", "jobs report", "employment", "labor"),
    "non-farm employment": ("nfp", "payroll", "jobs report", "employment", "labor"),
    "unemployment": ("unemployment", "jobless", "labor market", "sahm"),
    "average hourly earnings": ("wages", "ahe", "hourly earnings"),
    "jolts": ("jolts", "job openings", "labor tightness", "quits"),
    "fomc": ("fomc", "fed", "powell", "rate decision", "dot plot", "sep"),
    "federal funds": ("fomc", "fed", "rate decision", "powell"),
    "chair powell": ("powell", "fed"),
    "fed chair": ("powell", "fed"),
    "beige book": ("beige book", "fed"),
    "retail sales": ("retail sales", "consumer spending", "control group"),
    "ism manufacturing": ("ism", "manufacturing pmi", "factory"),
    "ism services": ("ism services", "services pmi"),
    "10-y bond auction": ("10-year auction", "treasury auction", "bond auction", "duration"),
    "30-y bond auction": ("30-year auction", "treasury auction", "long bond"),
    "3-y note auction": ("3-year auction", "treasury auction"),
    "jackson hole": ("jackson hole", "powell keynote"),
}


def _thesis_mentions_macro(thesis: str, event_names: list[str]) -> bool:
    """True if thesis references any of today's US 3-star events by name or alias."""
    if not event_names:
        return True  # no macro event to reference → vacuously satisfied
    t = thesis.lower()
    for evt in event_names:
        el = evt.lower()
        for key, aliases in _MACRO_EVENT_ALIASES.items():
            if key in el:
                if any(a in t for a in aliases):
                    return True
    return False


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


# Named-slot schema (pitch_1 + pitch_2) instead of an array. Rationale
# (2026-08-18 audit): Groq's strict json_schema constrained decoder enforces
# types + required fields + enums reliably, but does NOT reliably enforce array
# `minItems` — model can still emit 1-item arrays and Groq's post-validator
# rejects the whole response. Named slots make BOTH pitches structurally
# required at the schema level, matching the pattern already used for trades
# (commodity/equity/crypto). Same downstream contract: 2 pitches always ship.
_PITCH_ITEM_SCHEMA: dict[str, Any] = {
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
        "horizon_days": {"type": "integer", "minimum": 1, "maximum": 15},
        "earnings_direction_expectation": {"type": "string"},
    },
    "required": [
        "asset_symbol", "direction", "thesis", "key_factors",
        "rough_entry_hint", "rubric", "knowledge_sources_used", "horizon_days",
    ],
}

_PITCH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "pitch_1": _PITCH_ITEM_SCHEMA,
        "pitch_2": _PITCH_ITEM_SCHEMA,
    },
    "required": ["pitch_1", "pitch_2"],
}


_SYSTEM_PROMPT = """You are a disciplined equity strategist producing 2 blue-chip pitches for a Wall Street financial advisor's morning briefing.

STRICT RULES:
- Output MUST contain EXACTLY two top-level keys: `pitch_1` and `pitch_2`. Both are non-negotiable.
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
- knowledge_sources_used: cite EVERY source_id from the KNOWLEDGE LIBRARY block that shaped this pitch. NEVER paste text verbatim — transform and apply. If a pitch used no knowledge chunks, return [].
- For each pitch with EARNINGS_WITHIN_3D marked, you MUST include earnings_direction_expectation ('bullish' / 'bearish' / 'unknown') AND mention the earnings date + expected impact in the thesis.
- horizon_days: hold window; DEFAULT 5-7 (tactical). Cap 15. Long horizons prevent the resolver from grading pitches in time for the weekly look-back — prior data through 2026-08-13 had 25/26 pitches still_open because horizons were too long.
- low_star_warning (only when your rubric booleans sum to 0 or 1): 1 line, plain English, non-joking — explain honestly why shipping despite low conviction. Something the FA can say: "no near-term catalyst; treat as watch-list only". Omit or leave empty when stars≥2.

RUBRIC — you output 5 booleans; Python sums them. Be STRICT. Default to FALSE when the criterion is not clearly met. A 5/5 should be rare (~10% of days). Star inflation destroys the calibration loop.

  macro_alignment: TRUE only if today's setup rides the DOMINANT macro theme
    (rates direction, DXY move, VIX regime, active sector rotation). You must
    be able to name that macro read in the thesis in one clause.
    FALSE if the setup fights the tape or ignores the day's driver.
    Default FALSE.

  technical_setup: TRUE only if a CLEAN nameable structural level is in play
    (support, resistance, trendline, prior breakout base, 50/200-DMA).
    FALSE if the chart is mid-range with no defined level.
    Default FALSE unless the entry hint sits at a nameable level.

  catalyst_proximity: TRUE only if a NAMED, DATED catalyst hits within the
    horizon: earnings this week, a scheduled macro release today/tomorrow, a
    scheduled sector event.
    FALSE for "eventually", "in coming weeks", or "expected". No date = FALSE.
    (Python force-sets this TRUE for EARNINGS_WITHIN_3D tickers — you can't
    override that, but for non-flagged tickers, be strict.)

  base_rate_support: TRUE only if this SETUP TYPE has been historically
    playable — cite the class of prior instances (post-CPI drift, post-FOMC
    vol, seasonal Nov-Apr, breakout-retest after tight consolidation, etc.).
    Reference the pattern in your thesis or key_factors.
    FALSE if the setup is novel or you can't name the historical analog.
    Default FALSE.

  risk_reward: TRUE only if the move has ≥2× typical daily ATR of headroom
    to the thesis target AND a defined invalidation level is nameable.
    FALSE if the target is close, or if no invalidation is nameable.
    "Room to run" without an invalidation = FALSE. Default FALSE.

STAR CALIBRATION (honest distribution over 30 days):
  5/5 — ~10%. Every factor individually defensible with cited evidence.
  4/5 — the solid daily default when the setup is real.
  3/5 — "we can talk about this but it's not a slam dunk."
  2/5 — "here's what we have if you insist on 2 today."
  0-1/5 — ship with low_star_warning; do not withhold (per §C11).

Examples that are 0 on the named factor:
  • Pitch that "feels right" but names no macro read → macro_alignment=0.
  • "Trend is up" with no nameable level → technical_setup=0.
  • "Earnings soon" with no scheduled date → catalyst_proximity=0.
  • "Historically it's worked" without citing the analog class → base_rate_support=0.
  • Target 3% away but no invalidation named → risk_reward=0.

The Python layer will:
- Sum your rubric booleans to compute the 0-5 star rating
- Force catalyst_proximity=1 for EARNINGS_WITHIN_3D tickers regardless of your value
- Write low_star_warning to the report only when the final star_rating ≤ 1
"""


_COOLDOWN_SESSIONS = 5   # skip any ticker picked in the last N daily_morning reports


def _recent_pitch_tickers(sessions: int = _COOLDOWN_SESSIONS) -> set[str]:
    """Return the set of tickers picked in the last N daily_morning report_dates.
    Enforces rotation discipline: prior data showed MSFT×7, AAPL×5, GOOGL×3 =
    15/26 pitches from 3 tickers — no rotation. This filter breaks that."""
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT DISTINCT asset_symbol FROM pitches
               WHERE report_date IN (
                 SELECT DISTINCT report_date FROM pitches
                 ORDER BY report_date DESC LIMIT ?
               )""",
            (sessions,),
        ).fetchall()
    return {r[0] for r in rows}


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
    excluded_tickers: Optional[set[str]] = None,
    todays_us_3star_events: Optional[list[str]] = None,
) -> str:
    excl = excluded_tickers or set()
    filtered = [t for t in BLUE_CHIP_UNIVERSE if t not in excl]
    # If cooldown wiped >80% of the universe (unlikely at 100 tickers, but be
    # safe), fall back to the full list — §C11 never omit beats hollow rotation.
    if len(filtered) < 20:
        filtered = list(BLUE_CHIP_UNIVERSE)
    universe = ", ".join(filtered)
    cooldown_note = ""
    if excl and filtered is not BLUE_CHIP_UNIVERSE:
        cooldown_note = (
            f"\n(Cooldown: {len(excl)} ticker(s) picked in the last "
            f"{_COOLDOWN_SESSIONS} sessions are excluded above.)\n"
        )
    earnings_lines = []
    for t, info in earnings_flags.items():
        earnings_lines.append(
            f"- {t}: EARNINGS_WITHIN_3D=True, date={info['date']}, trading_days_from_today={info['td']}"
        )
    earnings_block = "\n".join(earnings_lines) if earnings_lines else "(no pitched-universe earnings within 3 trading days flagged this morning)"

    # 2026-08-24 roadmap Phase 2.2: elevate US 3-star events to a dedicated
    # section so the LLM can't miss them. If any exist, thesis MUST reference
    # them (checked post-hoc, warning-only per §C11). Matches the earnings
    # enforcement pattern.
    us_events = todays_us_3star_events or []
    if us_events:
        macro_block = (
            "US 3-STAR MACRO EVENTS TODAY (MUST reference in at least one thesis):\n"
            + "\n".join(f"- {n}" for n in us_events)
            + "\nUse the matching playbook loaded in the KNOWLEDGE LIBRARY block "
              "above to frame the thesis mechanism (post-CPI drift, dot-plot "
              "reaction, etc.) — do NOT quote verbatim."
        )
    else:
        macro_block = "US 3-STAR MACRO EVENTS TODAY: (none scheduled)"

    # news_summary intentionally dropped from prompt 2026-08-18 — Groq's 8K TPM
    # org cap made every daily_morning fail; news pulse was ~500 tokens with the
    # least direct signal for pitch quality (calendar + earnings drive the
    # catalyst, market_snapshot drives the setup). If we get provider headroom
    # back later, restore it.
    return f"""DATE: {date_ist} IST

BLUE_CHIP_UNIVERSE (choose exactly 2, distinct):
{universe}{cooldown_note}

TODAY'S CALENDAR (IST):
{calendar_summary}

{macro_block}

MARKET SNAPSHOT:
{market_snapshot}

EARNINGS-WITHIN-3D FLAGS:
{earnings_block}

{knowledge_context}

Produce 2 blue-chip pitches — one as `pitch_1`, one as `pitch_2`. Cite knowledge sources by source_id.
"""


def generate(
    date_ist: str,
    calendar_summary: str,
    market_snapshot: str,
    news_summary: str,
    report_type: str = "daily_morning",
    todays_us_3star_events: list[str] | None = None,
) -> tuple[list[Pitch], dict[str, int]]:
    """Return (pitches, token_counts). Persists each pitch to DB BEFORE any send.

    todays_us_3star_events: names of US 3-star calendar events for the report
    date. When present, (a) the matching macro playbook is loaded into the LLM
    context via knowledge.load_for_report, and (b) each pitch thesis is checked
    post-hoc for a reference to the event (warning only, per §C11).
    """
    todays_us_3star_events = todays_us_3star_events or []
    # Rotating ticker-facts sample: pass a day-seeded slice of the universe so
    # different tickers receive deep-context exposure over the week. Groq TPM cap
    # (12K/min) forces this trim; without it, 25+ populated ticker files blow the
    # budget. LLM still receives the full universe list in the system prompt and
    # can pitch any ticker — sampled ones just get the extra facts as context.
    # Sample=1: at 3 we hit Groq's 8K TPM org cap; at 1 the pitch prompt fits
    # under 6.5K with headroom. Rotation still cycles the full populated set
    # over ~25 days at size=1. See knowledge.load_for_report() header for the
    # broader budget analysis.
    ticker_sample = _rotating_ticker_sample(date_ist, size=1)
    kb = knowledge.load_for_report(
        report_type, tickers=ticker_sample,
        todays_event_names=todays_us_3star_events,
    )
    kb_ctx = knowledge.build_context_block(kb)

    # Pre-compute EARNINGS_WITHIN_3D flags for the ticker sample so the LLM sees
    # them BEFORE selection and can prefer earnings-week candidates. Post-hoc
    # rubric enforcement still runs on whatever ticker the LLM picks (even
    # outside the sample), but sample coverage is where the extra signal is
    # most valuable. yfinance calls ~1s per ticker × 3 = ~3s added latency.
    earnings_flags: dict[str, dict[str, Any]] = {}
    for t in ticker_sample:
        try:
            ei = check_earnings(t)
        except Exception as e:
            log.warning("earnings check failed for %s: %s", t, e)
            continue
        if ei and ei.within_3_trading_days:
            earnings_flags[t] = {
                "date": ei.next_earnings_date.isoformat(),
                "td": ei.trading_days_until,
            }

    excluded = _recent_pitch_tickers()
    user_prompt = _build_user_prompt(
        date_ist, calendar_summary, market_snapshot, news_summary, kb_ctx, earnings_flags,
        excluded_tickers=excluded,
        todays_us_3star_events=todays_us_3star_events,
    )
    result = llm_client.generate(_SYSTEM_PROMPT, user_prompt, _PITCH_SCHEMA)
    total_tin = result.tokens_in
    total_tout = result.tokens_out
    # Named-slot schema (pitch_1 + pitch_2) — strict decoder guarantees both
    # keys are present. Extract to a list to preserve downstream contract.
    parsed = result.parsed
    if "pitch_1" not in parsed or "pitch_2" not in parsed:
        raise ValueError(f"LLM output missing pitch_1/pitch_2 slots: {list(parsed.keys())}")
    raw = [parsed["pitch_1"], parsed["pitch_2"]]

    pitches: list[Pitch] = []
    for p in raw:
        sym = p["asset_symbol"].upper()
        if sym not in BLUE_CHIP_UNIVERSE:
            raise ValueError(f"LLM picked non-universe ticker: {sym!r}")
        # Post-hoc earnings check for the chosen ticker
        ei = check_earnings(sym)
        within_3d = bool(ei and ei.within_3_trading_days)
        # Rubric v1.1 audit inputs: trend + reasoning text (thesis + key_factors)
        # scanned for macro_alignment / base_rate_support truthfulness.
        audit_text = p.get("thesis", "") + " " + " ".join(p.get("key_factors") or [])
        rs = rubric.score(
            p["rubric"],
            earnings_within_3d=within_3d,
            direction=p.get("direction"),
            spot=market_data.latest_price(sym, "equity"),
            ma20=market_data.ma20(sym, "equity"),
            reasoning_text=audit_text,
        )
        low_warn = p.get("low_star_warning") if rs.stars <= 1 else None
        thesis_text = p["thesis"].strip()
        if within_3d and not _thesis_mentions_date(thesis_text):
            # §D.8, §E.21: flagged tickers MUST reference the earnings date.
            # Downgrade to a warning rather than hard-fail so we still ship
            # (per §C11 never-omit); operator sees the drift in logs.
            log.warning(
                "pitch %s flagged EARNINGS_WITHIN_3D but thesis has no date token — spec drift",
                sym,
            )
        # 2026-08-24 roadmap Phase 2.2: when a US 3-star macro event lands
        # today, thesis must acknowledge it. Warning-only per §C11.
        if todays_us_3star_events and not _thesis_mentions_macro(thesis_text, todays_us_3star_events):
            log.warning(
                "pitch %s did not reference today's US 3-star event(s) %s — spec drift",
                sym, todays_us_3star_events,
            )
        # §D.7: LLM MUST NOT paste knowledge text verbatim — transform and apply.
        # Detect 8-token contiguous copies from any loaded chunk. Warn only per
        # §C11 (never omit); operator sees the drift in logs and can prune the
        # offending chunk over time.
        vh = knowledge.verbatim_hits(thesis_text, kb)
        if vh:
            for sid, phrase in vh[:3]:
                log.warning(
                    "pitch %s thesis contains verbatim chunk from %s: %r",
                    sym, sid, phrase,
                )
        pitches.append(
            Pitch(
                asset_symbol=sym,
                direction=p["direction"],
                thesis=thesis_text,
                key_factors=[k.strip() for k in p["key_factors"]],
                rough_entry_hint=(p.get("rough_entry_hint") or "").strip() or None,
                star_rating=rs.stars,
                rubric_breakdown=rs.breakdown,
                low_star_warning=low_warn,
                earnings_within_3d=within_3d,
                earnings_date_ist=(ei.next_earnings_date.isoformat() if within_3d and ei else None),
                earnings_direction_expectation=p.get("earnings_direction_expectation"),
                knowledge_sources_used=list(p.get("knowledge_sources_used") or []),
                horizon_days=min(int(p.get("horizon_days") or 7), 15),
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

    return pitches, {"tokens_in": total_tin, "tokens_out": total_tout}
