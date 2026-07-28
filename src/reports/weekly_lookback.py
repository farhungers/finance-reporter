"""Weekly Look-Back — Saturday 16:00 IST (CLAUDE.md §D.1.c, §E.25 bootstrap discipline).

Uses shared visual language from src.reports._style.
Sections (numbered):
  1. Calendar surprises this week
  2. Pitch report card
  3. Trade report card
  4. Rubric calibration (only when n≥20 in a bucket)
  5. Knowledge library report (only when n≥20 with populated knowledge_sources_used)
  6. Interesting facts / anomalies

BOOTSTRAP (§E.25): first 4 weeks OR while all buckets have n<5 → skip %-tables,
show raw counts + qualitative observations only. No fake precision.
"""
from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from src import accuracy, config, db, stars, telegram_send
from src.reports._style import (
    FOOTER,
    HR,
    code_block,
    pad,
    report_header,
    section_banner,
)

log = logging.getLogger(__name__)

esc = telegram_send.esc

_BOOTSTRAP_MIN_N_PER_BUCKET = 5
_CALIBRATION_MIN_N = 20


def _week_range_ist(now_ist: datetime) -> tuple[str, str]:
    weekday = now_ist.weekday()
    end = now_ist - timedelta(days=weekday - 4)
    start = end - timedelta(days=4)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def generate(now: Optional[datetime] = None) -> tuple[str, dict]:
    now = now or datetime.now(config.TZ_UTC)
    now_ist = now.astimezone(config.TZ_IST)
    week_start, week_end = _week_range_ist(now_ist)

    n_tr, n_pi = accuracy.resolve_open_positions(as_of=now)
    log.info("weekly resolver: %d trades, %d pitches resolved", n_tr, n_pi)

    s = accuracy.stats_snapshot()
    bucket_max_n = max((sum(v.values()) for v in s.pitches_by_star.values()), default=0)
    bootstrap = bucket_max_n < _BOOTSTRAP_MIN_N_PER_BUCKET
    calibration_available = any(sum(v.values()) >= _CALIBRATION_MIN_N for v in s.pitches_by_star.values())

    lines: list[str] = []
    lines.append(report_header("🔍", "WEEKLY LOOK-BACK", f"Week of {week_start} — {week_end}"))
    if bootstrap:
        weeks = _weeks_since_first_pitch(now)
        lines.append(
            f"_Bootstrap week {weeks} of 4 — accuracy percentages activate once n≥5 in any bucket\\._"
        )

    # SECTION 1 — Calendar surprises
    lines.append(section_banner(1, "📅", "CALENDAR SURPRISES", None))
    highlights = _calendar_highlights(week_start, week_end)
    if highlights:
        for h in highlights:
            lines.append(f"  • {esc(h)}")
    else:
        lines.append("_No notable calendar surprises tracked this week\\._")

    # SECTION 2 — Pitch report card
    lines.append(section_banner(2, "💼", "PITCH REPORT CARD", None))
    lines.append(
        f"Total: *{s.pitches_open + s.pitches_resolved}*  ·  "
        f"Resolved: *{s.pitches_resolved}*  ·  Open: *{s.pitches_open}*"
    )
    if s.pitches_by_star:
        pitch_rows = _pitch_star_rows(s, bootstrap)
        if pitch_rows:
            lines.append(code_block(pitch_rows))
    best, worst = _best_worst_pitches()
    if best:
        lines.append(f"🏆 *Best call:* {esc(best)}")
    if worst:
        lines.append(f"💥 *Worst call:* {esc(worst)}")

    # SECTION 3 — Trade report card
    lines.append(section_banner(3, "⚡", "TRADE REPORT CARD", None))
    lines.append(
        f"Total: *{s.trades_open + s.trades_resolved}*  ·  "
        f"TP: *{s.trades_hit_tp}*  ·  SL: *{s.trades_hit_sl}*  ·  "
        f"Expired: *{s.trades_expired}*"
    )
    if s.trades_resolved:
        win = s.trades_hit_tp / s.trades_resolved * 100
        avg_r_s = f"{s.trades_avg_r:.2f}" if s.trades_avg_r is not None else "—"
        lines.append(f"Win rate: *{esc(f'{win:.0f}%')}*  ·  Avg R: *{esc(avg_r_s)}*")
    class_rows = _trade_class_rows(s)
    if class_rows:
        lines.append(code_block(class_rows))

    # SECTION 4 — Rubric calibration (gated)
    if calibration_available:
        lines.append(section_banner(4, "🎛", "RUBRIC CALIBRATION", "n≥20 threshold met"))
        lines.append("_Proposals below require operator review before applied\\._")
        for note in _rubric_calibration_notes():
            lines.append(f"  • {esc(note)}")

    # SECTION 5 — Knowledge library report (gated)
    if _knowledge_report_available():
        lines.append(section_banner(5, "📚", "KNOWLEDGE LIBRARY", None))
        for note in _knowledge_report_notes():
            lines.append(f"  • {esc(note)}")

    # SECTION 6 — Observations & anomalies (substantive across bootstrap + post-bootstrap)
    lines.append(section_banner(6, "🔎", "OBSERVATIONS & ANOMALIES", None))
    obs_lines = _observations(week_start, week_end, s, bootstrap)
    if obs_lines:
        for label, detail in obs_lines:
            lines.append(f"  *•* *{esc(label)}* — {esc(detail)}")
    else:
        lines.append("_No notable observations this week\\._")

    lines.append(HR)
    lines.append(FOOTER)
    lines.append("📅 _Have a good week ahead\\._")
    return "\n".join(lines), {"llm_tokens_in": 0, "llm_tokens_out": 0}


def _pitch_star_rows(s: accuracy.Stats, bootstrap: bool) -> list[str]:
    rows: list[str] = []
    for star in sorted(s.pitches_by_star.keys(), reverse=True):
        row = s.pitches_by_star[star]
        total = sum(row.values())
        star_glyph = f"{star}/5"
        if bootstrap:
            parts = " ".join(f"{k}={v}" for k, v in row.items())
            rows.append(f"{pad(star_glyph, 4)}  n={total:<3}  {parts}")
        else:
            resolved = total - row.get("still_open", 0)
            played = row.get("thesis_played_out", 0)
            pct = f"{played / resolved * 100:.0f}%" if resolved else "—"
            rows.append(f"{pad(star_glyph, 4)}  n={total:<3}  played={pct}")
    return rows


def _trade_class_rows(s: accuracy.Stats) -> list[str]:
    rows: list[str] = []
    for klass in ("commodity", "equity", "crypto"):
        row = s.trades_by_class.get(klass, {})
        if not row:
            continue
        parts = " ".join(f"{k}={v}" for k, v in row.items())
        rows.append(f"{pad(klass, 10)} {parts}")
    return rows


def _weeks_since_first_pitch(now: datetime) -> int:
    with db.connect() as conn:
        row = conn.execute("SELECT MIN(generated_at) AS first FROM pitches").fetchone()
        first = row["first"] if row else None
    if not first:
        return 1
    first_dt = datetime.fromisoformat(first.replace("Z", ""))
    weeks = max(1, (now.replace(tzinfo=None) - first_dt).days // 7 + 1)
    return min(weeks, 4)


def _calendar_highlights(week_start: str, week_end: str) -> list[str]:
    with db.connect() as conn:
        rows = conn.execute(
            """SELECT event_date, event_name, importance, forecast, actual, previous
            FROM calendar_events WHERE event_date BETWEEN ? AND ? AND importance >= 3
            ORDER BY event_date""",
            (week_start, week_end),
        ).fetchall()
    out: list[str] = []
    for r in rows:
        if r["actual"] and r["forecast"] and r["actual"] != r["forecast"]:
            out.append(f"{r['event_date']} {r['event_name']}: actual {r['actual']} vs F {r['forecast']}")
    return out[:6]


def _best_worst_pitches() -> tuple[Optional[str], Optional[str]]:
    with db.connect() as conn:
        best = conn.execute(
            """SELECT asset_symbol, direction, realized_pct FROM pitches
            WHERE resolution = 'thesis_played_out'
            ORDER BY ABS(COALESCE(realized_pct, 0)) DESC LIMIT 1"""
        ).fetchone()
        worst = conn.execute(
            """SELECT asset_symbol, direction, realized_pct FROM pitches
            WHERE resolution = 'thesis_failed'
            ORDER BY ABS(COALESCE(realized_pct, 0)) DESC LIMIT 1"""
        ).fetchone()
    best_s = f"{best['asset_symbol']} {best['direction']} {best['realized_pct']:+.1f}%" if best else None
    worst_s = f"{worst['asset_symbol']} {worst['direction']} {worst['realized_pct']:+.1f}%" if worst else None
    return best_s, worst_s


def _observations(week_start: str, week_end: str, s: accuracy.Stats, bootstrap: bool) -> list[tuple[str, str]]:
    """Return (label, explanation) tuples. Each observation names WHAT and briefly
    WHY it's notable, so an FA reader can scan quickly and drill in only where
    interesting."""
    out: list[tuple[str, str]] = []

    with db.connect() as conn:
        # This-week pitch rows
        pitches_rows = conn.execute(
            """SELECT asset_symbol, direction, star_rating, resolution, realized_pct,
                      earnings_within_3d, rubric_breakdown_json
               FROM pitches WHERE report_date BETWEEN ? AND ?""",
            (week_start, week_end),
        ).fetchall()
        trades_rows = conn.execute(
            """SELECT asset_symbol, asset_class, direction, star_rating,
                      resolution, realized_r
               FROM trades WHERE report_date BETWEEN ? AND ?""",
            (week_start, week_end),
        ).fetchall()

    # 1. Direction bias
    dirs = Counter(r["direction"] for r in pitches_rows)
    if dirs and (dirs.get("long", 0) == 0 or dirs.get("short", 0) == 0) and sum(dirs.values()) >= 3:
        dom = "long" if dirs.get("long", 0) > 0 else "short"
        out.append(("Direction bias", f"all {sum(dirs.values())} pitches this week were {dom}-only — worth watching if this reflects tape conviction or a blind spot"))

    # 2. Ticker concentration
    tickers = Counter(r["asset_symbol"] for r in pitches_rows)
    for sym, n in tickers.most_common(2):
        if n >= 3:
            out.append(("Ticker concentration", f"{sym} pitched {n} times this week — worth reviewing whether one thesis is being restated or if setups are actually distinct"))

    # 3. Earnings-flagged outcomes
    ew = [r for r in pitches_rows if r["earnings_within_3d"] == 1]
    if len(ew) >= 3:
        resolved = [r for r in ew if r["resolution"] and r["resolution"] != "still_open"]
        played = sum(1 for r in resolved if r["resolution"] == "thesis_played_out")
        if resolved:
            out.append(("Earnings pitches", f"{played}/{len(resolved)} earnings-flagged pitches played out — sample small but tracks calibration"))

    # 4. Trade streaks
    if s.trades_resolved:
        if s.trades_hit_sl > 0 and s.trades_hit_tp == 0:
            out.append(("SL streak", f"{s.trades_hit_sl} stop-losses hit with 0 take-profits this week — entry timing or SL placement is candidate to review"))
        elif s.trades_hit_tp >= 2 and s.trades_hit_sl == 0:
            out.append(("TP streak", f"{s.trades_hit_tp} take-profits with 0 stops — check whether TPs were conservative"))
        elif s.trades_avg_r is not None and s.trades_avg_r < -0.5:
            out.append(("Poor R week", f"average realized R {s.trades_avg_r:+.2f} — cluster of full-SL hits without offsetting TPs"))

    # 5. Class-level trade breakdown
    for klass in ("commodity", "equity", "crypto"):
        klass_rows = [r for r in trades_rows if r["asset_class"] == klass]
        if not klass_rows:
            continue
        wins = sum(1 for r in klass_rows if r["resolution"] == "hit_tp")
        losses = sum(1 for r in klass_rows if r["resolution"] == "hit_sl")
        if wins + losses >= 2 and wins == 0:
            out.append((f"{klass.title()} losses", f"0 wins on {wins + losses} resolved {klass} trades — class-specific review warranted"))

    # 6. Empty-dataset (bootstrap fallback)
    if bootstrap and not out:
        if s.pitches_open + s.pitches_resolved == 0:
            out.append(("Cold-start", "no pitches accumulated yet — first-week dataset"))
        elif s.trades_open + s.trades_resolved == 0:
            out.append(("Cold-start", "no trades accumulated yet — first-week dataset"))
        else:
            out.append(("Bootstrap week", f"{s.pitches_open + s.pitches_resolved} pitches / {s.trades_open + s.trades_resolved} trades logged — building the calibration base"))

    return out[:5]


def _rubric_calibration_notes() -> list[str]:
    return ["(stub — implemented after real data accumulates)"]


def _knowledge_report_available() -> bool:
    with db.connect() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS n FROM pitches WHERE knowledge_sources_used IS NOT NULL
            AND knowledge_sources_used != '[]'"""
        ).fetchone()
    return (row["n"] or 0) >= 20


def _knowledge_report_notes() -> list[str]:
    return ["(stub — top-cited sources by hit-rate; prune candidates)"]
