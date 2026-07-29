"""Shared visual language for all reports (locked with operator 2026-07-28).

Every report uses these primitives so the FA sees a consistent Bloomberg-terminal
vibe across morning, wrap, look-back, prep, and /stats.

Textures (used to differentiate sections within a report):
  - `blockquote_card()` — indented left-border card (calendar, cited data)
  - `code_block()` — gray monospace card (tabular numeric data)
  - flat prose with bold headers + emoji anchors (thesis, macro bullets)
"""
from __future__ import annotations

from src.telegram_send import esc

HR = "═" * 13    # double-line section divider (mobile-safe width; ~40% narrower than v1)
MINI = "╌" * 13  # light card separator (mobile-safe width)

COUNTRY_FLAG = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵", "CHF": "🇨🇭",
    "CAD": "🇨🇦", "AUD": "🇦🇺", "NZD": "🇳🇿", "CNY": "🇨🇳",
}

CLASS_ICON = {"commodity": "🥇", "equity": "📈", "crypto": "₿"}
CIRCLED = ("①", "②", "③", "④", "⑤")

FOOTER = "🔒 _Personal research — not investment advice\\._"


def direction_dot(direction: str, stars_n: int) -> str:
    """Colored dot per direction, or yellow for low-conviction (≤1 star)."""
    if stars_n <= 1:
        return "🟡"
    d = direction.lower()
    if d == "long":
        return "🟢"
    if d == "short":
        return "🔴"
    return "🟡"


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - len(s))


def fmt_num(v: float) -> str:
    if abs(v) >= 1000:
        return f"{v:,.2f}"
    if abs(v) >= 10:
        return f"{v:.2f}"
    return f"{v:.4f}"


def section_banner(number: int | None, emoji: str, title: str, subtitle: str | None = None) -> str:
    """Section banner: heavy line above, bold title with emoji, thin subtitle, heavy line below.
    Pass number=None to omit 'SECTION N'."""
    if number is None:
        label = f"{emoji}  *{esc(title)}*"
    else:
        label = f"{emoji}  *SECTION {number} · {esc(title)}*"
    if subtitle:
        label = f"{label}  _· {esc(subtitle)}_"
    return f"{HR}\n{label}\n{HR}"


def report_header(emoji: str, title: str, subtitle: str) -> str:
    """Report-level top header: emoji + BOLD title + italic subtitle on one line."""
    return f"{emoji} *{esc(title)}*  ·  📅 _{esc(subtitle)}_"


def code_block(lines: list[str]) -> str:
    """Wrap lines in triple-backtick fenced code block. Interior is literal — no escaping needed."""
    return "```\n" + "\n".join(lines) + "\n```"


def blockquote_card(lines: list[str]) -> str:
    """Render a single blockquote card (multi-line, MDv2). Callers are responsible
    for escaping the interior lines EXCEPT for MDv2 syntax they want interpreted."""
    return "\n".join(f">{line}" for line in lines)


def cards_stack(cards: list[str], separator: str = MINI) -> str:
    """Join card strings with a mini-separator between them."""
    return f"\n{separator}\n".join(cards)


def levels_table(entry: float, tp: float, sl: float, direction: str) -> str:
    """Entry/TP/SL as a monospace code-block table with %/RR columns."""
    tp_pct = (tp - entry) / entry * 100 if direction == "long" else (entry - tp) / entry * 100
    sl_pct = (entry - sl) / entry * 100 if direction == "long" else (sl - entry) / entry * 100
    rr_denom = abs(entry - sl)
    rr = abs(tp - entry) / rr_denom if rr_denom else 0.0

    entry_s = fmt_num(entry)
    tp_s = fmt_num(tp)
    sl_s = fmt_num(sl)
    w = max(len(entry_s), len(tp_s), len(sl_s))
    tp_pct_s = f"{tp_pct:+.2f}%".replace("-", "−")
    sl_pct_s = f"-{abs(sl_pct):.2f}%".replace("-", "−")
    return code_block([
        f"Entry   {pad(entry_s, w)}",
        f"TP      {pad(tp_s, w)}   {tp_pct_s}   RR {rr:.1f}",
        f"SL      {pad(sl_s, w)}   {sl_pct_s}",
    ])
