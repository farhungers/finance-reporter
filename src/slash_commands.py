"""Slash command handlers — /stats in v1 (CLAUDE.md §D.9, §C17).

Session 3 hooks (emoji feedback etc.) are stubbed in feedback_reactions table
but not consumed here — do not build in v1 (§C18).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from src import accuracy, config, db, knowledge, stars, telegram_send
from src.reports._style import FOOTER, HR, code_block, pad, report_header

_STATS_RATE_LIMIT_SEC = 60
_last_stats_reply: dict[str, float] = {}   # chat_id -> unix ts


def render_stats(now_ist_str: str) -> str:
    s = accuracy.stats_snapshot()
    esc = telegram_send.esc

    lines: list[str] = []
    lines.append(report_header("📊", "RUNNING STATS", f"as of {now_ist_str} IST"))

    # PITCHES
    lines.append(HR)
    lines.append(f"💼 *PITCHES* — {s.pitches_open} open · {s.pitches_resolved} resolved")
    if s.pitches_by_star:
        rows: list[str] = []
        for star in sorted(s.pitches_by_star.keys(), reverse=True):
            row = s.pitches_by_star[star]
            total = sum(row.values())
            resolved = total - row.get("still_open", 0)
            played = row.get("thesis_played_out", 0)
            pct = f"{played / resolved * 100:.0f}%" if resolved else "—"
            rows.append(f"{pad(f'{star}/5', 4)} n={total:<3} played={pct}")
        lines.append(code_block(rows))

    # TRADES
    lines.append(HR)
    lines.append(f"⚡ *TRADES* — {s.trades_open} open · {s.trades_resolved} resolved")
    if s.trades_resolved:
        tp_pct = f"{s.trades_hit_tp / s.trades_resolved * 100:.0f}%"
        sl_pct = f"{s.trades_hit_sl / s.trades_resolved * 100:.0f}%"
        exp_pct = f"{s.trades_expired / s.trades_resolved * 100:.0f}%"
        avg_r = f"{s.trades_avg_r:.2f}" if s.trades_avg_r is not None else "—"
        trade_rows = [
            f"TP  {tp_pct}",
            f"SL  {sl_pct}",
            f"Exp {exp_pct}",
            f"Avg R  {avg_r}",
        ]
        lines.append(code_block(trade_rows))
    class_rows: list[str] = []
    for klass in ("commodity", "equity", "crypto"):
        row = s.trades_by_class.get(klass, {})
        if row:
            parts = " ".join(f"{k}={v}" for k, v in row.items())
            class_rows.append(f"{pad(klass, 10)} {parts}")
    if class_rows:
        lines.append(code_block(class_rows))

    # OPEN POSITIONS
    lines.append(HR)
    lines.append("📍 *OPEN POSITIONS*")
    if s.open_positions:
        for op in s.open_positions[:10]:
            if op["kind"] == "trade":
                lines.append(
                    f"  • {esc(op['symbol'])} \\({esc(op['class'])}\\) "
                    f"{esc(op['direction'])} — age {op['age_days']}d"
                )
            else:
                lines.append(
                    f"  • {esc(op['symbol'])} pitch {esc(op['direction'])} "
                    f"{stars.render(op['stars'])} — age {op['age_days']}d"
                )
    else:
        lines.append("_No open positions\\._")

    # ACTIVE THEMES
    lines.append(HR)
    lines.append("🎯 *ACTIVE THEMES*")
    themes_path = config.KNOWLEDGE_DIR / "house_view" / "active_themes.md"
    themes_body = ""
    if themes_path.exists():
        themes_body = themes_path.read_text(encoding="utf-8")
    theme_bullets = _extract_theme_bullets(themes_body)
    if theme_bullets:
        for b in theme_bullets[:5]:
            lines.append(f"  • {esc(b)}")
    else:
        lines.append("_No active themes populated — see `knowledge/house_view/active_themes.md`\\._")

    lines.append(HR)
    lines.append(FOOTER)
    return "\n".join(lines)


def _extract_theme_bullets(body: str) -> list[str]:
    """Pull markdown bullets from the 'Current themes' section. Skip placeholder lines."""
    if not body:
        return []
    out: list[str] = []
    in_section = False
    for line in body.splitlines():
        s = line.strip()
        if s.lower().startswith("## current themes"):
            in_section = True
            continue
        if s.startswith("## ") and in_section:
            break
        if in_section and (s.startswith("- ") or s.startswith("* ") or (len(s) > 2 and s[0].isdigit() and s[1] == ".")):
            content = s.lstrip("-* ").split(".", 1)[-1].strip() if s[0].isdigit() else s.lstrip("-* ").strip()
            if "placeholder" in content.lower():
                continue
            if content:
                out.append(content)
    return out


def handle_stats(chat_id: str, now_ist_str: str) -> Optional[str]:
    """Return the message text if allowed, or None if rate-limited."""
    now = time.monotonic()
    last = _last_stats_reply.get(chat_id, 0.0)
    if now - last < _STATS_RATE_LIMIT_SEC:
        return None
    _last_stats_reply[chat_id] = now
    return render_stats(now_ist_str)


_last_health_reply: dict[str, float] = {}


def render_health(now_ist_str: str) -> str:
    """Compact reliability card: last-send timestamp + staleness flag for each of
    the 4 scheduled reports. Exists because on 2026-08-14 → 2026-08-18 the LLM
    provider silently 401'd and 4 straight days of missed reports slipped past
    the operator. Now: `/health` shows the freshness at a glance."""
    esc = telegram_send.esc
    freshness = accuracy.last_send_by_type()
    lines: list[str] = []
    lines.append(report_header("💓", "HEALTH", f"as of {now_ist_str} IST"))
    lines.append(HR)
    rows: list[str] = []
    for rt in ("daily_morning", "daily_wrap", "weekly_lookback", "weekly_prep"):
        info = freshness.get(rt) or {}
        age = info.get("age_hours")
        if age is None:
            label = "NEVER"
        elif age < 24:
            label = f"{age:.1f}h ago"
        else:
            label = f"{age / 24:.1f}d ago"
        flag = "🔴 STALE" if info.get("stale") else "🟢 OK"
        rows.append(f"{pad(rt, 17)} {pad(label, 12)} {flag}")
    lines.append(code_block(rows))
    lines.append(HR)
    lines.append(FOOTER)
    return "\n".join(lines)


def handle_health(chat_id: str, now_ist_str: str) -> Optional[str]:
    """Same 60s per-chat rate limit as /stats."""
    now = time.monotonic()
    last = _last_health_reply.get(chat_id, 0.0)
    if now - last < _STATS_RATE_LIMIT_SEC:
        return None
    _last_health_reply[chat_id] = now
    return render_health(now_ist_str)
