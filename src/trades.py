"""Trade generator: exactly 3 trades (1 commodity + 1 stock + 1 crypto).

CLAUDE.md §D.1.a Part 3, §C2, §C11, §E.14. Never substitute across classes. Never gap.
Low-star ships with 1-line warning. Rubric booleans → Python sum (§E.7).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

from src import db, knowledge, llm_client, rubric

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
- TP/SL ratio ≥ 2:1 → rubric.risk_reward=true, else false.
- SL must sit at a real technical level (prior swing, ATR band, structural break), not arbitrary.
- one_line_reasoning: single line, precise, non-joking. Cite the mechanism (breakout retest, mean reversion at level, macro-catalyst positioning).
- Rubric: return 5 booleans exactly. Do NOT sum — Python does.
- knowledge_sources_used: cite source_ids that shaped the trade.
- low_star_warning (only when rubric sums to 0 or 1): 1 line, precise, explain why shipping despite low conviction. Never omit a class slot — always ship 3.

Class integrity: even if a class has no A-grade setup today, produce the best available with honest low stars and a low_star_warning. Do NOT substitute across classes."""


def _build_user_prompt(
    date_ist: str,
    market_snapshot: str,
    calendar_summary: str,
    knowledge_context: str,
) -> str:
    return f"""DATE: {date_ist} IST

MARKET SNAPSHOT (spot prices + day change):
{market_snapshot}

TODAY'S CALENDAR (IST):
{calendar_summary}

{knowledge_context}

Produce exactly 3 trades: 1 commodity, 1 equity, 1 crypto. Per schema.
"""


def generate(
    date_ist: str,
    market_snapshot: str,
    calendar_summary: str,
    report_type: str = "daily_morning",
) -> tuple[list[Trade], dict[str, int]]:
    """Return ([commodity, equity, crypto], token_counts). Persists BEFORE any send."""
    kb = knowledge.load_for_report(report_type, tickers=[])
    kb_ctx = knowledge.build_context_block(kb)

    user_prompt = _build_user_prompt(date_ist, market_snapshot, calendar_summary, kb_ctx)
    result = llm_client.generate(_SYSTEM_PROMPT, user_prompt, _TRADE_SCHEMA)
    raw = result.parsed

    trades: list[Trade] = []
    for klass in ("commodity", "equity", "crypto"):
        if klass not in raw:
            raise ValueError(f"LLM missing trade class: {klass}")
        t = raw[klass]
        rs = rubric.score(t["rubric"], earnings_within_3d=False)
        low_warn = t.get("low_star_warning") if rs.stars <= 1 else None
        trades.append(
            Trade(
                asset_symbol=t["asset_symbol"].upper(),
                asset_class=klass,
                direction=t["direction"],
                entry=float(t["entry"]),
                tp=float(t["tp"]),
                sl=float(t["sl"]),
                one_line_reasoning=t["one_line_reasoning"].strip(),
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
