---
title: FinanceReporter — standing build brief for Reporter-Claude
project_type: Telegram bot delivering scheduled financial-market briefings to a Wall-Street financial advisor (personal-use tool)
generated_by: Pythia Janus (CEO mode, 2026-07-28; v3 same session — knowledge library + earnings + /stats added)
handoff_target: fresh Claude Code session opened in C:\FinanceReporter\
source_of_truth: OPERATOR_SPEC.md (this repo root) — verbatim operator spec + decision locks
universal_discipline: C:\Users\farha\OneDrive\Desktop\bluechipsignal\research\library\janus_universal_discipline_export.md
constraints_headline: zero recurring monthly cost — all APIs and services must be free tier or free forever
---

# FinanceReporter — Reporter-Claude standing brief

You are the AI implementer building this project. This document is your operating charter. Read it top-to-bottom before touching code, then re-read Section E every time you're about to ship.

---

## A. Mandatory reads (before any work)

Read these three files, in order, before Session 0 Step 1:

1. **`OPERATOR_SPEC.md`** (this repo root) — the operator's verbatim ask, decision locks, and the answered-questions record. This is the source-of-truth. When the operator's future ask conflicts with this document, surface the conflict — do not silently drift.
2. **`C:\Users\farha\OneDrive\Desktop\bluechipsignal\research\library\janus_universal_discipline_export.md`** — Janus universal discipline (preservation, self-audit, escape rules, operator collaboration). Adopt these disciplines fully; they are paid for in real errors on other projects.
3. **This file (CLAUDE.md)** in full again after the first two.

Your first tool call in this project should be `Read` on OPERATOR_SPEC.md.

---

## B. Session 0 — setup steps (execute in order, produce `session_0_report.md` at end)

**B.0 — Verify environment.** Confirm Python 3.11+ installed. Confirm you can create a venv at `C:\FinanceReporter\.venv\`. Confirm network egress to `api.telegram.org` and `generativelanguage.googleapis.com` (Gemini API — free tier). Do NOT touch OneDrive-synced paths — this project intentionally lives at `C:\FinanceReporter\` (bare C: root) to avoid OneDrive lock/sync fights on `.venv`, `__pycache__`, and SQLite journal files.

**Hosting question for Session 0:** the bot needs an always-on host. Propose in `session_0_report.md` one of: (a) friend's or operator's always-on desktop with Windows Task Scheduler or a Python service, (b) Oracle Cloud Always Free VM (ARM Ampere or AMD micro — truly free forever within tier), (c) other free-tier options. Operator picks.

**Telegram bot prerequisite (manual pre-Phase-1 step):** operator (or friend) must create the bot via `@BotFather` in Telegram BEFORE `session_0_report.md` is approved. Steps:
1. Message `@BotFather` → `/newbot` → follow prompts → save the token as `TELEGRAM_BOT_TOKEN`
2. Friend sends at least one message to the created bot (any content). This lets the bot discover its `chat_id` via a one-shot `getUpdates` call — save as `TELEGRAM_CHAT_ID`
3. Reporter-Claude documents these tokens as filled in `.env` (never committed) and confirms both work with a test `sendMessage` call under `DRY_RUN=true`

If the operator wants to test-drive the bot themselves before the friend is looped in, they can substitute their own chat_id temporarily; swap to friend's chat_id when the bot is production-ready.

**B.1 — Scaffold repo.** Create:
```
C:\FinanceReporter\
├── CLAUDE.md                       (this file — do NOT modify without operator ok)
├── OPERATOR_SPEC.md                (frozen spec — do NOT modify)
├── .venv\                          (created in B.0)
├── .env                            (secrets — see B.2)
├── .env.example                    (committed template, no secrets)
├── .gitignore                      (excludes .venv, .env, *.db, __pycache__)
├── requirements.txt
├── src\
│   ├── __init__.py
│   ├── config.py                   (env loader, timezone constants)
│   ├── db.py                       (SQLite schema + connection)
│   ├── scheduler.py                (APScheduler wrapper)
│   ├── calendar_source.py          (economic calendar fetch: ForexFactory primary)
│   ├── market_data.py              (prices via yfinance + CoinGecko)
│   ├── news.py                     (RSS headline aggregation)
│   ├── llm_client.py               (provider-agnostic LLM wrapper; Gemini default, swap-in ready)
│   ├── llm_providers\
│   │   ├── __init__.py
│   │   ├── base.py                 (abstract Provider interface)
│   │   ├── gemini.py               (Google Gemini 2.0 Flash impl)
│   │   └── groq.py                 (Groq Llama 3.3 70B fallback impl)
│   ├── knowledge.py                (knowledge library loader with provenance tagging)
│   ├── earnings.py                 (earnings calendar for pitched tickers, ±3d flag)
│   ├── slash_commands.py           (/stats Telegram command handler; Session 3 hooks stubbed)
│   ├── pitches.py                  (pitch generation logic)
│   ├── trades.py                   (trade generation logic)
│   ├── rubric.py                   (5-factor rubric, 0-5 star scoring in Python)
│   ├── accuracy.py                 (resolution + hit-rate tracking; feeds weekly look-back AND /stats)
│   ├── stars.py                    (star visual rendering: ⭐ / ☆ / 🌟 gold for 5/5)
│   ├── reports\
│   │   ├── daily_morning.py        (07:00 IST Mon-Fri = 04:00 UTC)
│   │   ├── daily_wrap.py           (19:00 IST Mon-Fri = 16:00 UTC)
│   │   ├── weekly_lookback.py      (16:00 IST Sat = 13:00 UTC)
│   │   └── weekly_prep.py          (16:00 IST Sun = 13:00 UTC)
│   ├── telegram_send.py            (send + MarkdownV2 escape helper; also receives /stats + Session 3 reactions)
│   └── main.py                     (scheduler entrypoint)
├── knowledge\                       (curated reference notes — LLM context; version-controlled)
│   ├── macro\                       (event playbooks: cpi, fomc, nfp, fed_speak_taxonomy, etc.)
│   ├── sectors\                     (sector regime reads: energy, tech, financials, healthcare, etc.)
│   ├── blue_chip\                   (one file per ticker in pitch universe — MANDATORY per §E.19)
│   ├── technicals\                  (support/resistance conventions, ATR sizing, volume profile)
│   ├── correlations\                (dxy_gold, vix_spx, 10y_growth, etc.)
│   └── house_view\                  (proprietary views + client-language notes + active themes)
├── tests\
│   ├── test_rubric.py
│   ├── test_stars_render.py
│   ├── test_telegram_escape.py
│   ├── test_calendar_parse.py
│   ├── test_accuracy_resolve.py
│   ├── test_knowledge_load.py
│   ├── test_knowledge_provenance.py
│   ├── test_earnings_flag.py
│   ├── test_stats_command.py
│   └── test_message_length_budget.py
├── data\                            (SQLite db + json cache — gitignored)
└── session_0_report.md              (produced at end of Session 0)
```

**B.2 — Configure `.env.example`** (never commit real secrets):
```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GEMINI_API_KEY=                     # generate free at aistudio.google.com
GROQ_API_KEY=                       # optional fallback, free at console.groq.com
LLM_PROVIDER=gemini                 # 'gemini' (default) or 'groq'
KILL_SWITCH_DAILY_MORNING=false
KILL_SWITCH_DAILY_WRAP=false
KILL_SWITCH_WEEKLY_LOOKBACK=false
KILL_SWITCH_WEEKLY_PREP=false
DRY_RUN=true                        # when true, prints to stdout instead of Telegram
```
Every scheduled report must respect its kill switch AND the global DRY_RUN. Never ship a report path without both.

**No paid API keys are permitted.** The operator locked "everything free" — if any dependency you're about to add has a paid tier that we might hit under normal usage, replace it with a free alternative BEFORE adding it. Free-tier daily-quota limits are acceptable if our usage stays comfortably inside.

**B.3 — Confirm data sources.** For each data source below, in Session 0, either succeed at a real test fetch OR document the fallback:

| Need | Primary (free) | Fallback (free) |
|---|---|---|
| Economic calendar (3-star events, weekly view) | ForexFactory weekly XML at `https://www.forexfactory.com/ffcal_week_this.xml` (100% free, no key, no rate limit) | TradingEconomics guest tier (guest:guest) — heavily rate-limited but works for a test fetch |
| Equity prices + basic fundamentals | `yfinance` (free, unofficial Yahoo Finance scraper) | Stooq free CSV endpoints |
| Crypto prices | CoinGecko free API (30 calls/min, no key) | Binance public endpoints |
| Commodities prices | `yfinance` (GC=F gold, CL=F oil, SI=F silver, HG=F copper, NG=F nat gas) | Stooq futures endpoints |
| Financial news headlines | RSS aggregation via `feedparser`: Reuters biz, Bloomberg headlines RSS, Yahoo Finance news, WSJ market pulse | Google Finance news pane RSS |
| Earnings calendar (blue-chip pitch universe) | `yfinance` `.calendar` and `.earnings_dates` attributes (free) | Nasdaq public earnings calendar RSS |
| LLM reasoning | Google Gemini 2.0 Flash (free tier: 15 RPM, 1M TPM, 1500 req/day — way over our need) | Groq Llama 3.3 70B (free tier: 30 RPM) |

**Investing.com scraping is prohibited** — their ToS blocks it and their front-end is heavily anti-bot. The operator's screenshot was for spec reference only; do not scrape investing.com.

**NewsAPI is prohibited** — its free tier is 100 req/day AND non-commercial only. Use RSS.

**B.4 — Timezone constants (LOCK).** In `src/config.py`:
```python
from zoneinfo import ZoneInfo
TZ_UTC = ZoneInfo("UTC")
TZ_IST = ZoneInfo("Europe/Istanbul")     # display TZ inside every report body
TZ_ET  = ZoneInfo("America/New_York")    # market reference only — NOT displayed in reports

# Schedule (all in UTC — the ONLY canonical scheduling timezone):
CRON_DAILY_MORNING     = "0 4 * * 1-5"    # 04:00 UTC Mon-Fri = 07:00 IST weekdays
CRON_DAILY_WRAP        = "0 16 * * 1-5"   # 16:00 UTC Mon-Fri = 19:00 IST weekdays
CRON_WEEKLY_LOOKBACK   = "0 13 * * 6"     # 13:00 UTC Sat = 16:00 IST Saturday
CRON_WEEKLY_PREP       = "0 13 * * 0"     # 13:00 UTC Sun = 16:00 IST Sunday
```

**Every timestamp displayed in a report body MUST be Istanbul time** (Europe/Istanbul) with the label ` IST`. Operator preference, locked 2026-07-28 (point 1 of the 8-point walkthrough). Do not mix ET and IST in a single message body. ET is used only for internal market-reference calculations (e.g., "is US market open right now for this trade timestamp"); it never appears in report text.

Total scheduled sends per week = **12** (10 daily Mon-Fri + Sat lookback + Sun prep). `/stats` is ad-hoc, not scheduled.

**B.5 — SQLite schema (LOCK v1).** Create at first run:
```sql
CREATE TABLE IF NOT EXISTS pitches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  generated_at TEXT NOT NULL,               -- ISO UTC
  report_date TEXT NOT NULL,                -- YYYY-MM-DD (IST)
  asset_symbol TEXT NOT NULL,
  asset_class TEXT NOT NULL,                -- 'equity_bluechip' for pitches
  direction TEXT NOT NULL,                  -- 'long' / 'short' / 'neutral'
  thesis TEXT NOT NULL,                     -- deep reasoning
  key_factors_json TEXT NOT NULL,           -- JSON array of factor strings
  rough_entry_hint TEXT,                    -- freeform, e.g. "near $185 support"
  star_rating INTEGER NOT NULL CHECK(star_rating BETWEEN 0 AND 5),
  rubric_breakdown_json TEXT NOT NULL,      -- {"macro":1,"technical":1,"catalyst":0,"base_rate":1,"rr":1}
  low_star_warning TEXT,                    -- 1-line warning shown when star_rating <= 1
  earnings_within_3d INTEGER DEFAULT 0,     -- 1 if pitched ticker has earnings within 3 trading days (either side)
  knowledge_sources_used TEXT,              -- JSON array of source_id strings, per §D.7
  horizon_days INTEGER,                     -- typical hold window
  resolved_at TEXT,                         -- nullable
  resolution TEXT,                          -- 'thesis_played_out' / 'thesis_failed' / 'noise' / 'still_open'
  realized_pct REAL                         -- price change vs entry hint at resolution
);

CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  generated_at TEXT NOT NULL,
  report_date TEXT NOT NULL,
  asset_symbol TEXT NOT NULL,
  asset_class TEXT NOT NULL,                -- 'commodity' / 'equity' / 'crypto'
  direction TEXT NOT NULL,
  entry REAL NOT NULL,
  tp REAL NOT NULL,
  sl REAL NOT NULL,
  one_line_reasoning TEXT NOT NULL,
  star_rating INTEGER NOT NULL CHECK(star_rating BETWEEN 0 AND 5),
  rubric_breakdown_json TEXT NOT NULL,
  low_star_warning TEXT,                    -- 1-line warning shown when star_rating <= 1
  knowledge_sources_used TEXT,              -- JSON array of source_id strings
  resolved_at TEXT,
  resolution TEXT,                          -- 'hit_tp' / 'hit_sl' / 'expired' / 'still_open'
  realized_r REAL                           -- (exit-entry)/(entry-sl) in R
);

CREATE TABLE IF NOT EXISTS calendar_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fetched_at TEXT NOT NULL,
  event_date TEXT NOT NULL,                 -- YYYY-MM-DD (IST)
  event_time_ist TEXT,                      -- HH:MM
  country TEXT NOT NULL,
  event_name TEXT NOT NULL,
  importance INTEGER NOT NULL,              -- 1/2/3 stars
  forecast TEXT,
  previous TEXT,
  actual TEXT,                              -- populated post-release
  source TEXT NOT NULL                      -- 'forexfactory' / 'tradingeconomics'
);

CREATE TABLE IF NOT EXISTS report_sends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  report_type TEXT NOT NULL,                -- 'daily_morning' / 'daily_wrap' / 'weekly_lookback' / 'weekly_prep' / 'stats_reply'
  sent_at TEXT NOT NULL,
  telegram_message_id INTEGER,              -- NULL if send failed; populated on success
  char_count INTEGER,
  read_minutes_estimate REAL,
  kill_switch_state TEXT NOT NULL,          -- 'on' / 'off'
  dry_run INTEGER NOT NULL,                 -- 0/1
  llm_provider TEXT,                        -- 'gemini' / 'groq' etc — for cost/quality audit
  llm_tokens_in INTEGER,
  llm_tokens_out INTEGER
);

CREATE TABLE IF NOT EXISTS knowledge_hits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  used_at TEXT NOT NULL,
  report_type TEXT NOT NULL,
  source_id TEXT NOT NULL,                  -- 'knowledge/macro/cpi_playbook.md#historical_reaction'
  pitch_id INTEGER,                         -- nullable link to pitches.id
  trade_id INTEGER                          -- nullable link to trades.id
);

-- Session 3 hooks (schema in place from v1; consumers not yet built)
CREATE TABLE IF NOT EXISTS feedback_reactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  received_at TEXT NOT NULL,
  telegram_message_id INTEGER NOT NULL,     -- links to report_sends.telegram_message_id
  pitch_id INTEGER,                         -- nullable
  trade_id INTEGER,                         -- nullable
  emoji TEXT NOT NULL,                      -- '👍' '👎' '🤔' etc
  note TEXT                                 -- optional 1-word reply
);
```

**B.6 — Pilot: one dry-run of each report type.** Before enabling scheduler:
- Set `DRY_RUN=true`
- Manually invoke each of the 4 report generators
- Output goes to stdout (not Telegram)
- Verify: message respects length budget, all dynamic content escaped, all times shown are **IST**, no timezone confusion (no ET in message body), kill switch respected, star rendering correct (⭐/☆/🌟-gold for 5/5), low-star warning line present when applicable
- **Knowledge library sanity:** every ticker in the blue-chip pitch universe MUST have a `knowledge/blue_chip/{ticker}_facts.md` file. The pilot fails hard if any is missing. Empty stub files with only frontmatter are acceptable at Session 0 (they get populated as knowledge accumulates) but must exist.
- **Knowledge provenance sanity:** verify that at least one pilot report has non-empty `knowledge_sources_used` in DB and `knowledge_hits` rows written. If empty across all 4 pilots, the loader isn't wired.
- **Earnings integration sanity:** confirm at least one pilot pitch triggered `earnings_within_3d=1` (if the calendar has any megacap earnings in the pilot window). If none does, verify the flag is exercisable via a synthetic test date.
- **`/stats` sanity:** trigger `/stats` manually via Telegram (or stdout equivalent under DRY_RUN); verify structured output within budget.
- Produce `session_0_report.md` with:
  - Env verification results
  - Hosting proposal (Section B.0)
  - Data source test-fetch results (with fallback status per source)
  - LLM provider test call (Gemini) + sample structured JSON output showing `knowledge_sources_used` populated
  - 4 dry-run report samples (full text) + `/stats` sample
  - Knowledge library scaffold status (which folders/files created, which are stubs)
  - Any deviations from CLAUDE.md sections C-E (deviations require operator approval before Phase 1)

**Operator approves session_0_report.md → Phase 1 begins (real Telegram sends, kill switches individually flippable, DRY_RUN=false).**

---

## C. Locked design decisions (Janus + operator, 2026-07-28; do not re-litigate without operator)

Point-number references are to the 8-point operator walkthrough (see OPERATOR_SPEC.md §6).

| # | Decision | Reasoning |
|---|---|---|
| C1 | **All schedule times in UTC** in code (`0 4 * * 1-5` etc). **Message body timestamps display Istanbul time (IST) only** — never ET, never mixed. | Point 1 (A1+B2). UTC cron is DST-invariant; IST display is operator preference. |
| C2 | **Trades quantity = 3 always** (1 commodity + 1 stock + 1 crypto). Ship all 3 even when the rubric produces low-star candidates. Low-star (0-1) candidates SHIP with a 1-line warning drawn from `low_star_warning`. Do NOT skip a class slot. Do NOT substitute across classes. Do NOT lower the rubric threshold to fake higher stars. | Point 6 (V5-modified) + operator principle: "always provide something, never nothing." |
| C3 | **Pitches quantity = 2 always** (revised from 3 by operator on 2026-07-28 after pilot review), blue-chip only. Blue chip = S&P 100 constituents + top-15 US large-cap equities by market cap. Ship both with rubric-driven stars; low-star pitches get a 1-line warning. | Point 4 (U1) + Point 7 (PS1 via principle) + operator revision 2026-07-28. |
| C4 | **Star rubric v1 (rubric-in-Python; 0-5 scale).** Each of 5 factors (`macro_alignment`, `technical_setup`, `catalyst_proximity`, `base_rate_support`, `risk_reward`) is a boolean; sum = stars. LLM outputs JSON booleans; Python sums. No LLM freeform scoring. | Point 2 (M1). Prevents hallucination-in-a-star-costume. |
| C5 | **Weekly look-back is the accuracy report.** Every Saturday, resolve open pitches + trades using price data; compute hit rate by star rating, by asset class, by rubric factor; report honestly including negative findings; recalibrate rubric weights only after n≥20 resolved per bucket. | Makes stars mean something over time. |
| C6 | **Compliance banner: single-line footer** on every report: *"Personal research — not investment advice. Verify before acting."* | Operator delegated legal. |
| C7 | **All Telegram dynamic content MarkdownV2-escaped.** Every variable interpolated into a message body wraps through the escape helper. Regression test mandatory. | Pythia project ate the same escape bug 3 times; this project starts with the test. |
| C8 | **Project directory stays at `C:\FinanceReporter\`** — never migrate to OneDrive. | Standing no-OneDrive rule. |
| C9 | **LLM: Google Gemini 2.0 Flash (free tier) via a provider-agnostic wrapper.** `src/llm_client.py` exposes a `generate(system, user, schema) -> dict` interface; provider chosen by `LLM_PROVIDER` env. Ship with Gemini; Groq (Llama 3.3 70B) is a config-swap fallback. Zero recurring cost. | Point 5 (L6 + L2). "Everything free." |
| C10 | **Persistence-first: every pitch and trade written to SQLite BEFORE the Telegram send.** `telegram_message_id` in `report_sends` is populated post-send (NULL when send fails); pitch/trade rows exist regardless. | Point 3 (P1). |
| C11 | **Product principle: "Always surface next-best; never omit."** When a class-slot lacks a high-star candidate, ship the best available with its honest low star rating and a 1-line warning. Never hide, never gap. | Operator locked 2026-07-28. Governs all edge cases. |
| C12 | **Style rule: precise, easy to understand, no jokes.** Applies to warning lines, thesis prose, reasoning notes, weekly recap. | Operator locked 2026-07-28. |
| C13 | **Weekend schedule: daily reports Mon-Fri only.** 10 daily + Sat lookback + Sun prep = 12 messages/week. | Point 8 (W1). |
| C14 | **Star visual convention** (rendered in `src/stars.py`): 0/5 `☆☆☆☆☆`, 1/5 `⭐☆☆☆☆`, 2/5 `⭐⭐☆☆☆`, 3/5 `⭐⭐⭐☆☆`, 4/5 `⭐⭐⭐⭐☆`, **5/5 `🌟🌟🌟🌟🌟` (gold, visually distinct)**. | Point 7 addendum. |
| C15 | **Knowledge library ships in v1.** Curated markdown notes at `knowledge/*` loaded as LLM context per report; provenance-tagged; hits logged to `knowledge_hits`. Every pitched ticker MUST have a `knowledge/blue_chip/{ticker}_facts.md` file (stub OK, absent NOT OK). | Session 3 add via operator ask; boosts consistency and factual grounding, near-zero token cost via Gemini context caching. |
| C16 | **Earnings integration ships in v1.** For pitched tickers, `yfinance` earnings check; if earnings ≤3 trading days out, `earnings_within_3d=1`, `catalyst_proximity=1` auto-triggered (LLM cannot override), thesis MUST mention the earnings date + expected direction. | Prevents "surprise earnings" foot-shot on blue-chip pitches. |
| C17 | **`/stats` slash command ships in v1.** Ad-hoc Telegram command returns running accuracy + open positions + active themes; same accuracy engine as weekly look-back. | Turns bot from one-way broadcast into queryable desk assistant. |
| C18 | **Session 3 features (yesterday's card, emoji feedback, age-of-thesis) are SCOPE-LOCKED as v2.** Schema hooks (`feedback_reactions` table) exist from v1; consumers NOT built until Session 3 unlock criteria met (see §D.10). | Prevents scope creep in Session 0-2; keeps runway clean for the operator-approved bundle. |
| C19 | **Deferred features SCOPE-LOCKED as refused for v1:** portfolio tracking (compliance surface), voice cloning (use `house_view/client_language.md` instead), breaking-news alerts (false-positive risk), bot self-reflection (LLM self-critique unreliable). | Explicit non-scope per operator confirmation 2026-07-28. |

---

## D. Architecture

### D.1 — Four reports, four schedules, four generators

Each report has its own module under `src/reports/` with a single public entrypoint `generate() -> str`. The scheduler calls this, writes result to DB (`report_sends`), then hands the string to `telegram_send.send()`. Reports never write to Telegram directly.

All displayed timestamps in message bodies are **IST** with the ` IST` suffix. Star rendering uses the `stars.render(n)` helper per §C14. Knowledge library loaded per §D.7. Earnings check per §D.8.

**D.1.a — Daily Morning (04:00 UTC Mon-Fri = 07:00 IST)**

Length budget: ~1500 tokens of display text (~5 min read).

Structure (fixed order — do not permute):
```
📅 [Date IST] — Morning Briefing
─────────────────────────────
1. TODAY'S CALENDAR (IST)
   • [HH:MM IST] 🇺🇸 [Event name] ★★★
     Forecast: X | Previous: Y
     Expected consequence: [1 sentence, precise, drawn from knowledge/macro/*]
   ...
   Tomorrow's key events: [1-line teaser]
   Big week-ahead events: [1-line if any not yet named]

2. TODAY'S PITCHES — BLUE CHIP
   ── Pitch 1: [SYMBOL] [LONG/SHORT] ⭐⭐⭐⭐☆
      Thesis: [2-3 sentences deep, client-usable]
      [If earnings_within_3d=1: 📅 Earnings [date IST] — [expected direction impact]]
      Key factors:
        • [factor 1]
        • [factor 2]
        • [factor 3]
      Rough entry: [hint]
   ── Pitch 2 ...
   ── Pitch 3: [SYMBOL] [LONG/SHORT] ⭐☆☆☆☆
      ⚠ Low conviction — [1-line reason, precise]
      Thesis: ...
      ...

3. TODAY'S TRADES — VARIETY
   ── Commodity: [SYMBOL] [LONG/SHORT] ⭐⭐⭐☆☆
      Entry: X | TP: Y | SL: Z
      Why: [1 line, precise]
   ── Stock: [SYMBOL] [LONG/SHORT] 🌟🌟🌟🌟🌟
      Entry: X | TP: Y | SL: Z
      Why: [1 line]
   ── Crypto: [SYMBOL] [LONG/SHORT] ☆☆☆☆☆
      ⚠ No qualifying setup — [1-line reason]
      Entry: X | TP: Y | SL: Z
      Why: [1 line]
─────────────────────────────
Personal research — not investment advice. Verify before acting.
```

**D.1.b — Daily Wrap (16:00 UTC Mon-Fri = 19:00 IST)**

Length budget: ~400 tokens (~1 min read).

Structure:
```
📊 [Date IST] — Day Wrap
Today's tape in one line: [session summary]
Notable / anomalous:
  • [item 1]
  • [item 2 if any]
Tomorrow's key events (IST): [1-2 lines]
─────────────────────────────
Personal research — not investment advice.
```

Note: 19:00 IST is mid-US-session (12:00 ET). Treat as "morning-session wrap + afternoon setup."

**D.1.c — Weekly Look-Back (Saturday 13:00 UTC = 16:00 IST)**

Length budget: ~2000 tokens.

Structure:
```
🔍 Week of [date range IST] — Reflection

CALENDAR HIGHLIGHTS
  • [notable event surprises this week]

PITCH REPORT CARD
  Total pitches: X | Resolved: Y | Still open: Z
  By star rating:
    🌟🌟🌟🌟🌟 (5/5): n=A, thesis_played_out: X%
    ⭐⭐⭐⭐☆ (4/5): n=B, ...
    ...
  Best call: [pitch summary + outcome]
  Worst call: [pitch summary + outcome]

TRADE REPORT CARD
  Total trades: X | Hit TP: A | Hit SL: B | Expired: C
  Win rate: X% | Avg R realized: Y
  By asset class:
    Commodity: ...
    Stock: ...
    Crypto: ...

RUBRIC CALIBRATION
  [Only shown when n≥20 in any bucket]
  Rubric factor 'catalyst_proximity' correlates with hit-rate: r=X
  Rubric factor 'macro_alignment' correlates: r=Y
  Suggested weight adjustment: [proposal, operator-review before applied]

KNOWLEDGE LIBRARY REPORT
  [Only shown when n≥20 pitches have knowledge_sources_used populated]
  Top-cited sources this week: [source_id list with hit_rate correlation]
  Sources appearing in >5 failed pitches: [candidates for review/pruning]

INTERESTING FACTS / ANOMALIES
  • [anything unusual worth noting]
```

**Honesty rule:** if a bucket had 5 five-star pitches and 4 played wrong, the report must say so plainly. No softening. No jokes. No spin.

**D.1.d — Weekly Prep (Sunday 13:00 UTC = 16:00 IST)**

Length budget: ~1200 tokens.

Structure:
```
🎯 Week of [date range IST] — The Horizon

MAJOR EVENTS THIS WEEK (IST times)
  Monday: ...
  Tuesday: ...
  ...
  Friday: ...

3-STAR HEAT MAP
  [Which days carry the highest event load; which mornings need the most attention]

MACRO SETUP GOING IN
  • [Big themes to watch: Fed speak, earnings megacaps, geopolitical]

EARNINGS THIS WEEK (blue-chip universe)
  • [Ticker: date IST + Street consensus if available]

SECTOR/THEME TO WATCH THIS WEEK
  • [1-3 sector angles with rationale, drawn from knowledge/sectors/*]
```

### D.2 — Star rubric v1 (0-5, factor-based)

Each pitch/trade earns 0 or 1 point per factor. Sum = star rating (range 0-5).

**Rubric factors (both pitches and trades):**
| Factor | Point criterion |
|---|---|
| `macro_alignment` | Setup aligns with the day/week's dominant macro read (rates direction, DXY, VIX regime). Boolean. |
| `technical_setup` | Clear structure — near support/resistance, trend intact, or defined breakout level. Boolean. |
| `catalyst_proximity` | Named catalyst within horizon: earnings this week, macro release today, sector-specific news. Boolean. **Auto-set to 1 when `earnings_within_3d=1`; LLM cannot override.** |
| `base_rate_support` | Setup type has been historically playable (post-CPI drift, post-FOMC vol, seasonal). Boolean. |
| `risk_reward` | (For trades) TP/SL ratio ≥ 2:1 AND SL is at a real level not arbitrary. (For pitches) The move has room >2× typical daily ATR. Boolean. |

Every pitch/trade in the DB stores its `rubric_breakdown_json`. This is what the weekly look-back correlates against outcomes.

**When star_rating ≤ 1**, the generator MUST also produce a `low_star_warning` — a 1-line, precise, non-joking explanation of why this candidate is being shipped despite low conviction.

**Do NOT invent factors on the fly.** Do NOT let the LLM freeform-score. The generator prompt hands the LLM the rubric and requires JSON output with named booleans; the star count is computed in Python from the booleans, not from the LLM.

### D.3 — Accuracy resolver

`src/accuracy.py` runs before every weekly look-back AND on-demand for `/stats`. For each `still_open` row:
- **Trades:** query price series since `generated_at`. Did price hit `tp` before `sl` (or vice versa)? Mark resolution + realized R. If neither hit within 5 trading days → `expired`.
- **Pitches:** softer horizon (typically 5-10 trading days per `horizon_days`). Rate against `direction`: did the underlying move ≥2% in the pitched direction (`thesis_played_out`), move ≥2% against (`thesis_failed`), or drift <2% (`noise`)?

The resolver is honest by construction — it has no writeback to the pitch generator; it only records. Never allow a code path where the generator sees prior "failed" scoring and revises its own past record.

### D.4 — Message escaping

`src/telegram_send.py` exposes:
```python
def esc(s: str) -> str:
    """Escape a dynamic string for Telegram MarkdownV2. Every dynamic
    variable interpolated into a message body MUST pass through this."""
```
`test_telegram_escape.py` verifies characters `_ * [ ] ( ) ~ ` > # + - = | { } . !` are all escaped correctly.

### D.5 — LLM provider wrapper

`src/llm_client.py` exposes:
```python
def generate(system: str, user: str, response_schema: dict) -> dict:
    """Call the configured LLM provider with structured-output enforcement.
    Provider chosen by LLM_PROVIDER env var. Returns parsed dict matching schema.
    Retries once on schema validation failure; raises after."""
```
Provider implementations live in `src/llm_providers/`. Adding a new provider = one file, one entry in the factory. Zero refactor to switch providers.

**Gemini context caching:** enable for the knowledge library payload. First call per day warms cache; subsequent calls (up to cache TTL, typically ~1 hour on Gemini free tier) read from cache = near-zero token cost on the knowledge chunks.

### D.6 — Star renderer

`src/stars.py`:
```python
def render(n: int) -> str:
    """Return the star string per CLAUDE.md §C14. n in [0, 5]."""
```
Regression test: `test_stars_render.py` verifies exact byte output for each n ∈ {0, 1, 2, 3, 4, 5}, including the gold-star special case for 5.

### D.7 — Knowledge library (curated LLM context) — v1

`knowledge/` is a version-controlled folder of curated markdown notes. The LLM loads relevant notes as context per report — outputs get more consistent, factually grounded, and (via Gemini's context caching) nearly free at token cost.

**File format:**
```yaml
---
topic_tags: [macro, cpi, inflation]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: YYYY-MM-DD
provenance: "operator-curated from Napier Anatomy of the Bear pp 45-58"
---

# Topic title

Body content in markdown. Section anchors (## Historical reaction, ## Playbook, ## Common wrongness) are cited by the LLM via source_id.
```

**Loader (`src/knowledge.py`):**
```python
def load_for_report(report_type: str, tickers: list[str]) -> dict[str, str]:
    """Return {source_id: chunk_content} for notes relevant to this report.
    source_id format: 'knowledge/{path}#{section_anchor}'.
    Selection:
      - files where applies_to_reports includes report_type
      - PLUS all knowledge/blue_chip/{ticker}_facts.md for pitched tickers
      - PLUS knowledge/house_view/active_themes.md (always)
    """
```

**Provenance in prompts:** every chunk enters the LLM context with its `source_id` visible. The LLM's structured output includes a `knowledge_sources_used: [source_id, ...]` field. Written to both `pitches.knowledge_sources_used` / `trades.knowledge_sources_used` and per-hit rows in `knowledge_hits` on generation.

**Provenance in outputs:** the LLM MUST NOT paste knowledge text verbatim into the report; it must transform/apply it (paraphrase, apply to today's situation, cite the takeaway). But the DB record ties each pitch to the knowledge chunks that shaped it. This is what lets the weekly look-back correlate knowledge sources with outcome quality → prune/correct the library over time.

**Mandatory files (fail-fast at pilot):**
- Every ticker in the pitch universe has `knowledge/blue_chip/{ticker}_facts.md` (stub with frontmatter only is OK; empty file NOT OK; missing file NOT OK)
- `knowledge/house_view/philosophy.md` exists (stub OK)
- `knowledge/house_view/client_language.md` exists (stub OK) — style guidance for pitch prose; the LLM reads this to tune its output voice
- `knowledge/house_view/active_themes.md` exists (stub OK) — current thematic bullets, refreshed weekly by operator/friend

**Content acquisition:** operator-supplied books/articles + free authoritative sources (Fed/BLS/BEA official pages, Investopedia stable terminology). Book asks queued at OPERATOR_SPEC.md §9.

**Adding a new blue-chip ticker to the universe:** must also add the corresponding `knowledge/blue_chip/{ticker}_facts.md` in the same commit. Pilot regression test enforces this.

### D.8 — Earnings calendar integration — v1

Blue-chip pitches are earnings-sensitive. A TSLA long the day before earnings is a fundamentally different pitch than 3 weeks out.

**Rule:** for every pitched ticker, `src/earnings.py` checks `yfinance` `.calendar` and `.earnings_dates`. If the next earnings is within 3 trading days (either side):
1. `earnings_within_3d` column is set to 1 on the pitch row
2. The rubric factor `catalyst_proximity` auto-sets to 1 (LLM cannot override to 0)
3. The pitch thesis MUST include a 1-line mention of the earnings date + expected direction impact
4. Format in report: `📅 Earnings [date IST] — [1-line impact expectation]` inserted between thesis and key factors

If earnings within 3d AND the pitch is a directional bet against the expected earnings direction → add a `low_star_warning` line even if other rubric factors are high (this is a red flag, not a hard block — operator principle: never omit).

**Fallback:** if `yfinance` returns no earnings date, use the Nasdaq calendar RSS. If both fail, log a warning and set `earnings_within_3d = NULL` (don't guess; downstream treats NULL as "unknown, no auto-trigger, no rubric override").

### D.9 — `/stats` slash command — v1

Friend can send `/stats` at any time to Telegram. Bot replies with:

```
📊 Running Stats (as of [now IST])

Pitches: n=X open, n=Y resolved
  By star: 🌟🌟🌟🌟🌟 played_out: A%, ⭐⭐⭐⭐☆ played_out: B%, ...
  By class: [blue-chip breakdown]

Trades: n=X open, n=Y resolved
  Hit rate: TP=A%, SL=B%, expired=C%
  Avg R: Z
  By class: commodity ..., stock ..., crypto ...

Currently open positions:
  [list of still_open trades with age]

Active themes (from knowledge/house_view/active_themes.md):
  [current thematic bullets, ≤5]
```

Same underlying queries as the weekly look-back — one shared `src/accuracy.py` function fed to both surfaces. Length budget for `/stats`: ~600 tokens. Precise, no jokes.

Rate-limit: max 1 `/stats` reply per 60 seconds per chat (prevent spam / cost accidents).

### D.10 — Session 3 features (NOT v1 — planned; scope-locked)

Do not build these in Session 0-2. Documented here so scope stays clear and schema hooks are placed correctly.

**Yesterday's follow-up card in daily-morning (Session 3):**
2-3 line top-of-report summary of yesterday's trades' current state: "Yesterday's trades: AAPL +2.1% open near TP1, Gold -0.4% open, BTC hit SL -1R." Adds daily visibility to the accuracy loop instead of hiding it until Saturday. Uses `src/accuracy.py`; no new schema.

**Emoji feedback loop (Session 3):**
Telegram reactions (👍/👎/🤔) on any pitch/trade message logged to `feedback_reactions` table (schema exists from v1 per B.5). Weekly look-back cross-references human vs auto-resolver: divergence = signal.

**Age-of-thesis warning (Session 3):**
Daily morning flags any pitch open >10 trading days with no meaningful move: "AAPL long — thesis 12 days old, no direction; consider closing." Prevents zombie theses. Uses existing `pitches.resolution='still_open'` + `generated_at` age calc.

**Session 3 unlock criteria (all three must hold):**
- (a) Session 0-2 pilot approved and Phase 1 running
- (b) Real deployment for ≥4 weeks with kill switches off
- (c) Accuracy loop has n≥20 resolved in at least one star bucket

**Session 3 activation:** operator invokes a new walkthrough; Reporter-Claude proposes design updates; operator locks; docs revise to move Session 3 items from §D.10 to §D.11-13.

---

## E. Hard constraints (read before every ship)

1. **Every dynamic string wraps through `esc()` before Telegram send.** No exceptions.
2. **DRY_RUN=true is the default in .env.example.** Real sends require explicit operator flip.
3. **Kill switches per report** — operator can silence any of the 4 report types independently without touching the others.
4. **All timestamps displayed inside a report body are in IST** with the ` IST` label. Never mix ET and IST in a single message. ET is used only for internal market-hours calculation, never in output text.
5. **Persistence before send** — write pitches/trades to SQLite BEFORE calling Telegram.
6. **LLM: free-tier providers only.** Gemini 2.0 Flash by default; Groq Llama 3.3 70B fallback. Log token counts per call to `report_sends`. If free-tier quota alerts fire, drop reasoning depth before falling back to paid — never silently upgrade to a paid provider.
7. **Rubric scoring computed in Python, not by the LLM.** LLM hands you booleans; Python sums them. Range is 0-5.
8. **No writeback from resolver to generator.** Historical record is immutable; only new rows can be added.
9. **No Investing.com scraping. No NewsAPI. No paid API keys.** Use the primary/fallback sources listed in §B.3.
10. **Blue-chip pitches only** — S&P 100 + top 15 US large-cap by market cap. Nothing else.
11. **Always ship 2 pitches + 3 trades. Never gap. Never substitute across classes.** Low-star (0-1) candidates ship with a `low_star_warning` line. Star rating is the honesty signal; the friend decides whether to use it. (Pitch count revised from 3 → 2 by operator 2026-07-28.)
12. **"Always surface next-best; never omit."** (§C11 product principle.) Governs all edge cases: quiet calendar day, thin news week, illiquid crypto tape, etc. When in doubt: ship with honest low stars + warning, not silence.
13. **Style: precise, easy to understand, no jokes.** (§C12.) Applies to warning lines, thesis prose, reasoning notes, weekly recap.
14. **Length budgets enforced by `test_message_length_budget.py`** — morning ≤ ~1500, wrap ≤ ~400, weekly lookback ≤ ~2000, weekly prep ≤ ~1200, `/stats` reply ≤ ~600 tokens.
15. **Every report ends with the compliance one-liner.** Not a paragraph — one line.
16. **Weekend schedule locked: daily reports Mon-Fri only.** 12 total sends/week. No Sat/Sun daily reports.
17. **Star visual convention locked (§C14).** `stars.render()` is the single source of truth; every star display uses it. 5/5 renders as gold star 🌟.
18. **When you're about to modify CLAUDE.md or OPERATOR_SPEC.md — STOP and ask operator.** These are frozen.
19. **Every ticker in the blue-chip pitch universe MUST have a `knowledge/blue_chip/{ticker}_facts.md` file.** Fail fast at pilot if missing. Stub-with-frontmatter OK; absent NOT OK. Adding a ticker to the universe requires the facts file in the same commit.
20. **Knowledge chunks are cited by `source_id`; every pitch and trade in the DB stores `knowledge_sources_used`.** LLM MUST NOT paste verbatim — must transform/apply. Every knowledge hit also logs to `knowledge_hits`.
21. **Earnings within 3 trading days auto-triggers `catalyst_proximity=1` AND MUST be mentioned in the pitch thesis** (with the 📅 line per §D.8). LLM cannot override this rubric factor when the flag is true.
22. **Session 3 features are scope-locked NOT-v1.** Do not build yesterday's-card, emoji feedback, or age-of-thesis in Session 0-2. Schema hooks (`feedback_reactions` table) exist for future; consumers are Session 3.
23. **Deferred features are scope-locked REFUSED-for-v1.** No portfolio tracking, no voice cloning, no breaking-news alerts, no bot self-reflection. See §G for full prohibitions.
24. **Daily SQLite backup discipline.** A scheduled task runs every day at 03:30 UTC (30 min before the daily-morning cron) and copies `data/*.db` to `data/backups/YYYYMMDD_HHMMSS_*.db` via `sqlite3 .backup` (NOT `cp` — SQLite's backup API handles active connections safely). Retention: 30 days rolling; prune older. Backup failure is LOUD (log at ERROR + optional Telegram alert to operator), not silent. The accuracy loop is the load-bearing feature — losing 3 months of pitch history = losing the calibration ground truth that stars depend on.
25. **Bootstrap discipline for early weekly look-backs (first 4 weeks OR until n≥5 in any bucket).** During bootstrap: skip the `By star rating` percentage table (fake precision on n<5 is worse than useless); show raw counts only; add 2-3 qualitative observations; include a 1-liner header: *"Bootstrap week [N] of 4 — accuracy percentages activate once n≥5 in any bucket."* No soft-averaged early-numbers. No trend claims from n<5. The look-back exists during bootstrap as a discipline habit and to warm the reporting muscle, not to produce statistical signal.

---

## F. Working agreement

- **Build small, verify each piece.** Get calendar-fetch working before touching pitch generation. Get pitch generation working with a dry-run before adding trade generation. Session 0 pilots each report separately.
- **Self-audit before every commit.** Discipline export §"self-audit before shipping" — run through it EVERY commit, not just big ones.
- **Honest pushback to the operator.** If a future ask conflicts with a locked decision here (§C) or with a hard constraint (§E), surface the conflict; do not silently comply.
- **Tag enforcement.** Every commit message references the section of CLAUDE.md or OPERATOR_SPEC.md that motivated it, e.g. `feat(knowledge): loader for macro chunks — §D.7`.
- **Cost discipline.** Zero-cost is the constraint. Log token counts per call. If a 24h window shows any recurring paid charge from a service, kill switch it immediately and surface to operator.
- **Knowledge library growth is expected.** As operator supplies books/articles, extract into topic notes. Prefer many small tightly-focused files over few large ones (better retrieval granularity, easier prune).
- **Do not touch bluechipsignal or its memory.** This project is a sibling. The universal discipline export is a read-only reference. Do NOT edit any file under `C:\Users\farha\OneDrive\Desktop\bluechipsignal\`.

---

## G. What you should NOT do

1. Do NOT scrape Investing.com. (Use ForexFactory XML or TradingEconomics guest tier.)
2. Do NOT use NewsAPI. (Free tier too limited AND non-commercial only. Use RSS via `feedparser`.)
3. Do NOT add any paid API dependency. (Everything free — operator constraint 2026-07-28.)
4. Do NOT let the LLM freeform-score stars. (Rubric booleans only; sum in Python.)
5. Do NOT design compliance features beyond the one-line footer. (Operator delegated legal.)
6. Do NOT migrate this project to a OneDrive-synced path.
7. Do NOT combine the Saturday and Sunday reports into one.
8. Do NOT include stocks outside the blue-chip universe in pitches.
9. Do NOT rewrite historical DB rows when resolving outcomes — append-only.
10. Do NOT modify CLAUDE.md or OPERATOR_SPEC.md without operator sign-off.
11. Do NOT ship a report path without a kill switch AND DRY_RUN respect.
12. Do NOT edit anything under bluechipsignal or its memory directory.
13. Do NOT gap a class slot. (Ship low-star candidate + 1-line warning per §C11.)
14. Do NOT substitute across trade classes (never 2 stocks + 1 crypto instead of 1 commod + 1 stock + 1 crypto).
15. Do NOT lower rubric threshold to fake higher star ratings. (Honest 1/5 beats dishonest 3/5.)
16. Do NOT display ET times in message bodies. (§C1 lock: IST only in output.)
17. Do NOT include jokes, hedging language, or filler prose. (§C12 style rule.)
18. Do NOT send daily morning/wrap on Saturday or Sunday. (§C13 weekend lock.)
19. Do NOT display stars any way other than via `stars.render()`. (§C14 visual lock.)
20. Do NOT let the LLM paste knowledge library text verbatim into reports. (§D.7 — must transform/apply.)
21. Do NOT skip the earnings-within-3d check for pitched tickers. (§D.8 — this is a real risk factor.)
22. Do NOT add a ticker to the pitch universe without adding its `knowledge/blue_chip/{ticker}_facts.md` in the same commit. (§E.19 fail-fast.)
23. Do NOT build Session 3 features (yesterday's-card, emoji feedback loop consumer, age-of-thesis warnings) in Session 0-2. (§D.10 scope lock.)
24. Do NOT build portfolio tracking / per-client holdings. (§C19 — compliance surface + PII risk.)
25. Do NOT build voice-cloning / style-transfer. (§C19 — LLMs sound like caricatures. Use `knowledge/house_view/client_language.md` instead.)
26. Do NOT build breaking-news / alert interrupts between scheduled reports. (§C19 — false-positive risk; friend has Bloomberg.)
27. Do NOT build bot self-reflection / meta-analysis loops. (§C19 — LLM self-critique is unreliable; wait until Session 5+ with real accuracy data.)
28. Do NOT ignore the rate limit on `/stats` (1 per 60s per chat). (Cost + spam vector.)

---

## H. Closing reinforcement

This project's whole value proposition is **an honest, calibrated, disciplined daily briefing.** The friend is a busy Wall Street FA who trusts what he reads at breakfast. If the star ratings become vibes, the calendar becomes wrong times, the pitches become vague, the warnings become jokes, or the knowledge library becomes ChatGPT-guessed — the tool is worse than nothing, because it consumes attention without earning it.

**Discipline > velocity. Calibration > confidence. Honesty > polish.**

The operator's core principle governs every edge case: **"Always surface next-best; never omit. Confidence is expressed by star rating, not by withholding. The friend decides."**

The knowledge library is the differentiator vs. generic bots — it's what makes this tool grounded in real curated finance knowledge rather than LLM-guessed patterns. Grow it deliberately, cite it always, prune it honestly.

When Session 0 ends and Phase 1 begins, the operator will be trusting this brief to guide implementation. Re-read Section E every ship.
