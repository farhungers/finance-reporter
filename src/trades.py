"""Trade generator: exactly 3 trades (1 commodity + 1 stock + 1 crypto).

CLAUDE.md §D.1.a Part 3, §C2, §C11, §E.14. Never substitute across classes. Never gap.
Low-star ships with 1-line warning. Rubric booleans → Python sum (§E.7).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, date
from typing import Any, Optional

from src import db, knowledge, llm_client, market_data, rubric

log = logging.getLogger(__name__)


@dataclass
class Trade:
    asset_symbol: str
    asset_class: str          # 'commodity' / 'equity' / 'crypto'
    direction: str
    entry: float
    tp: float
    sl: float
    one_line_reasoning: str
    star_rating: int
    rubric_breakdown: dict[str, int]
    low_star_warning: Optional[str]
    knowledge_sources_used: list[str] = field(default_factory=list)
    db_id: Optional[int] = None


_TRADE_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "asset_symbol": {"type": "string"},
        "direction": {"type": "string", "enum": ["long", "short"]},
        "entry": {"type": "number"},
        "tp": {"type": "number"},
        "sl": {"type": "number"},
        "one_line_reasoning": {"type": "string"},
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
        "knowledge_sources_used": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "asset_symbol", "direction", "entry", "tp", "sl",
        "one_line_reasoning", "rubric", "knowledge_sources_used",
    ],
}

_TRADE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "commodity": _TRADE_ITEM_SCHEMA,
        "equity": _TRADE_ITEM_SCHEMA,
        "crypto": _TRADE_ITEM_SCHEMA,
    },
    "required": ["commodity", "equity", "crypto"],
}


_SYSTEM_PROMPT = """You are a disciplined trader producing 3 daily trade ideas for a professional's personal book.

MANDATORY: exactly 3 trades — 1 commodity, 1 US-listed equity (NOT restricted to blue chips), 1 major crypto (BTC/ETH/SOL/etc.).

STRICT RULES:
- Provide precise numeric entry, TP, SL for each trade.
- SL must sit at a real technical level (prior swing, ATR band, structural break), not arbitrary.
- one_line_reasoning: single line, precise, non-joking. Cite the mechanism (breakout retest, mean reversion at level, macro-catalyst positioning).
- knowledge_sources_used: cite source_ids that shaped the trade.
- low_star_warning (only when rubric sums to 0 or 1): 1 line, precise, explain why shipping despite low conviction. Never omit a class slot — always ship 3.

Class integrity: even if a class has no A-grade setup today, produce the best available with honest low stars and a low_star_warning. Do NOT substitute across classes.

RUBRIC — you output 5 booleans; Python sums them. Be STRICT. Default to FALSE when the criterion is not clearly met. A 5/5 should be rare (~10% of days). Star inflation destroys the calibration loop.

  macro_alignment: TRUE only if today's direction rides the DOMINANT macro
    theme (rates direction, DXY move, VIX regime, active sector rotation).
    Name the read in one_line_reasoning.
    FALSE if fighting the tape or ignoring the day's driver. Default FALSE.

  technical_setup: TRUE only if entry sits at a CLEAN, nameable structural
    level (prior swing, breakout retest, trendline, moving-average band).
    FALSE if the entry floats mid-range or the level is invented. Default FALSE.

  catalyst_proximity: TRUE only if a NAMED, DATED catalyst hits within the
    trade's horizon (macro release today/tomorrow, earnings this week for
    equity, scheduled sector event, funding-rate flip for crypto).
    FALSE for "eventually" or "in coming weeks". No date = FALSE.

  base_rate_support: TRUE only if this SETUP TYPE has been historically
    playable — name the analog class in one_line_reasoning (post-CPI drift,
    post-FOMC vol, breakout-retest after tight consolidation, gold bid on
    real-yield fall, etc.).
    FALSE if novel or you cannot name the historical analog. Default FALSE.

  risk_reward: TRUE only if TP/SL distance ratio is ≥ 2:1 AND SL sits at a
    real technical level (not a round number). Both conditions required.
    FALSE if the ratio is below 2:1 OR the SL is arbitrary. Default FALSE.

STAR CALIBRATION (honest distribution over 30 days):
  5/5 — ~10%. Every factor individually defensible with cited evidence.
  4/5 — the solid daily default when the setup is real.
  3/5 — "playable but not a slam dunk."
  2/5 — "the best we have in this class today."
  0-1/5 — ship with low_star_warning; do not omit the class slot.

Examples that are 0 on the named factor:
  • Trade with no macro read cited → macro_alignment=0.
  • Entry mid-range with no nameable level → technical_setup=0.
  • "News soon" without a scheduled date → catalyst_proximity=0.
  • "It usually works" without an analog class → base_rate_support=0.
  • TP/SL ratio 1.5:1, or SL at a round number → risk_reward=0."""


# Weekday → suggested commodity anchor. Breaks the observed "always GOLD"
# pattern (11/11 commodity trades were GOLD long mean-reversion, 0 TP, all SL).
# The LLM may deviate — §C11 never-omit + a genuinely stronger setup elsewhere
# — but the anchor moves the base case so we sample the full commodity space
# across the week instead of one instrument, one playbook.
_COMMODITY_DOW = {
    0: "GOLD",       # Monday
    1: "OIL_WTI",    # Tuesday
    2: "COPPER",     # Wednesday
    3: "SILVER",     # Thursday
    4: "NAT_GAS",    # Friday
}


def _suggested_commodity(date_ist: str) -> str:
    try:
        d = date.fromisoformat(date_ist)
    except Exception:
        return "GOLD"
    return _COMMODITY_DOW.get(d.weekday(), "GOLD")


def _build_user_prompt(
    date_ist: str,
    market_snapshot: str,
    calendar_summary: str,
    knowledge_context: str,
    suggested_commodity: str,
) -> str:
    return f"""DATE: {date_ist} IST

MARKET SNAPSHOT (spot prices + day change):
{market_snapshot}

TODAY'S CALENDAR (IST):
{calendar_summary}

{knowledge_context}

COMMODITY ROTATION ANCHOR: {suggested_commodity}
(Default to this commodity today unless a materially stronger setup exists in
another commodity. Rotation exists to prevent single-instrument, single-playbook
concentration — data through 2026-08-13 showed 100% SL hit rate on 11 straight
GOLD-long mean-reversion trades. Deviate only when justified.)

Produce exactly 3 trades: 1 commodity, 1 equity, 1 crypto. Per schema.
"""


_ENTRY_SNAP_TOLERANCE = 0.02   # snap entry to spot if LLM number deviates >2%
_ATR_SL_MULT = 1.5             # SL = spot ± 1.5 × ATR14
_MIN_RR = 2.0                  # enforce TP/SL ratio ≥ 2:1


def _ground_prices(
    symbol: str,
    asset_class: str,
    direction: str,
    llm_entry: float,
    llm_tp: float,
    llm_sl: float,
) -> tuple[float, float, float, list[str]]:
    """Re-anchor LLM-guessed entry/tp/sl to live spot + 14d ATR.

    Prior LLM (Groq Llama 3.3 70B) was inventing entries from training-data
    memory: NVDA@520, MSFT@280, BTC@63k — all months-stale. Result: 60% SL rate
    across the trade book. This snaps the numbers to reality:

      • Entry: if |llm - spot|/spot > 2%, snap to spot
      • SL: 1.5 × 14d ATR away from entry (Wilder-standard breathing room)
      • TP: 2.0 × the SL distance in the trade direction (locks R:R ≥ 2:1)

    If market data is unavailable, we ship the LLM's numbers unchanged with a
    warning (§C11: never omit — the friend sees stars + reasoning and decides).
    Returns (entry, tp, sl, snap_notes)."""
    notes: list[str] = []
    spot = market_data.latest_price(symbol, asset_class)
    if spot is None or spot <= 0:
        notes.append("spot_unavailable")
        return llm_entry, llm_tp, llm_sl, notes

    entry = llm_entry
    dev = abs(llm_entry - spot) / spot
    if dev > _ENTRY_SNAP_TOLERANCE:
        notes.append(f"entry_snapped:{llm_entry:.4g}->{spot:.4g} (dev={dev:.1%})")
        entry = spot

    atr = market_data.atr14(symbol, asset_class)
    if atr is None or atr <= 0:
        # No history → keep LLM's SL/TP relative to (possibly snapped) entry.
        # Preserve original absolute distances if entry was snapped.
        if entry != llm_entry:
            sl_dist = abs(llm_entry - llm_sl)
            tp_dist = abs(llm_entry - llm_tp)
            if direction.lower() == "long":
                return entry, entry + tp_dist, entry - sl_dist, notes + ["atr_unavailable"]
            return entry, entry - tp_dist, entry + sl_dist, notes + ["atr_unavailable"]
        notes.append("atr_unavailable")
        return entry, llm_tp, llm_sl, notes

    sl_dist = _ATR_SL_MULT * atr
    tp_dist = _MIN_RR * sl_dist
    if direction.lower() == "long":
        sl = entry - sl_dist
        tp = entry + tp_dist
    else:
        sl = entry + sl_dist
        tp = entry - tp_dist
    notes.append(f"atr_sized:atr={atr:.4g} sl_dist={sl_dist:.4g} tp_dist={tp_dist:.4g}")
    return entry, tp, sl, notes


def generate(
    date_ist: str,
    market_snapshot: str,
    calendar_summary: str,
    report_type: str = "daily_morning",
) -> tuple[list[Trade], dict[str, int]]:
    """Return ([commodity, equity, crypto], token_counts). Persists BEFORE any send."""
    kb = knowledge.load_for_report(report_type, tickers=[])
    kb_ctx = knowledge.build_context_block(kb)

    user_prompt = _build_user_prompt(
        date_ist, market_snapshot, calendar_summary, kb_ctx,
        suggested_commodity=_suggested_commodity(date_ist),
    )
    try:
        result = llm_client.generate(_SYSTEM_PROMPT, user_prompt, _TRADE_SCHEMA)
        raw = result.parsed
    except Exception as e:
        # gpt-oss-20b (Groq free tier, forced by 8K TPM org cap) produces
        # invalid JSON on the nested trade schema periodically (observed
        # 2026-08-17: json_validate_failed x3). Groq's provider-level retries
        # use the SAME prompt so they don't help. Python-level retry with an
        # emphatic JSON-shape reminder gets a fresh attempt with useful hint.
        log.warning("trade LLM call failed once (%s); retrying with schema reminder", e)
        retry_prompt = user_prompt + (
            "\n\n⚠ CRITICAL: your previous response failed JSON validation. Return ONLY "
            "a single JSON object with EXACTLY three top-level keys: `commodity`, `equity`, "
            "`crypto`. Each MUST have `asset_symbol`, `direction` ('long'|'short'), `entry`, "
            "`tp`, `sl` (all numbers), `one_line_reasoning`, `rubric` (object with 5 booleans), "
            "and `knowledge_sources_used` (array). No markdown, no code fence, no prose — "
            "just the JSON object."
        )
        result = llm_client.generate(_SYSTEM_PROMPT, retry_prompt, _TRADE_SCHEMA)
        raw = result.parsed

    trades: list[Trade] = []
    for klass in ("commodity", "equity", "crypto"):
        if klass not in raw:
            raise ValueError(f"LLM missing trade class: {klass}")
        t = raw[klass]
        sym = t["asset_symbol"].upper()
        direction = t["direction"]
        entry, tp, sl, snap_notes = _ground_prices(
            sym, klass, direction,
            float(t["entry"]), float(t["tp"]), float(t["sl"]),
        )
        for note in snap_notes:
            log.info("trade %s %s ground_prices: %s", klass, sym, note)
        # Since Python now enforces ATR-sized SL + R:R ≥ 2:1, force risk_reward=1
        # when we successfully re-anchored (any "atr_sized" note). This prevents
        # the LLM from tanking the star rating with a conservative FALSE after
        # we already ensured the constraint.
        rubric_in = dict(t["rubric"])
        if any(n.startswith("atr_sized") for n in snap_notes):
            rubric_in["risk_reward"] = True
        # Rubric v1.1 audit inputs: trend (ma20) verifies macro_alignment;
        # reasoning text is scanned for a dated analog anchor for base_rate_support.
        rs = rubric.score(
            rubric_in,
            earnings_within_3d=False,
            direction=direction,
            spot=market_data.latest_price(sym, klass),
            ma20=market_data.ma20(sym, klass),
            reasoning_text=t.get("one_line_reasoning", ""),
        )
        low_warn = t.get("low_star_warning") if rs.stars <= 1 else None
        reasoning = t["one_line_reasoning"].strip()
        # §D.7: verbatim-paste detection also applies to trade reasoning.
        vh = knowledge.verbatim_hits(reasoning, kb)
        if vh:
            for sid, phrase in vh[:2]:
                log.warning(
                    "trade %s reasoning contains verbatim chunk from %s: %r",
                    sym, sid, phrase,
                )
        trades.append(
            Trade(
                asset_symbol=sym,
                asset_class=klass,
                direction=direction,
                entry=entry,
                tp=tp,
                sl=sl,
                one_line_reasoning=reasoning,
                star_rating=rs.stars,
                rubric_breakdown=rs.breakdown,
                low_star_warning=low_warn,
                knowledge_sources_used=list(t.get("knowledge_sources_used") or []),
            )
        )

    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with db.connect() as conn:
        cur = conn.cursor()
        for tr in trades:
            cur.execute(
                """INSERT INTO trades
                (generated_at, report_date, asset_symbol, asset_class, direction, entry, tp, sl,
                 one_line_reasoning, star_rating, rubric_breakdown_json, low_star_warning,
                 knowledge_sources_used)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    now_utc, date_ist, tr.asset_symbol, tr.asset_class, tr.direction,
                    tr.entry, tr.tp, tr.sl, tr.one_line_reasoning, tr.star_rating,
                    json.dumps(tr.rubric_breakdown), tr.low_star_warning,
                    json.dumps(tr.knowledge_sources_used),
                ),
            )
            tr.db_id = cur.lastrowid
            for sid in tr.knowledge_sources_used:
                cur.execute(
                    """INSERT INTO knowledge_hits (used_at, report_type, source_id, trade_id)
                    VALUES (?,?,?,?)""",
                    (now_utc, report_type, sid, tr.db_id),
                )

    return trades, {"tokens_in": result.tokens_in, "tokens_out": result.tokens_out}
