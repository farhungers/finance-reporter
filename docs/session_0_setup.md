---
title: Session 0 setup — historical archive
status: Session 0 shipped 2026-07-28; kept here for reference / auditability
extracted_from: CLAUDE.md §A + §B (v3, 2026-07-28)
---

# Session 0 setup — historical archive

This file preserves the original mandatory-reads list and Session 0 setup procedure. Session 0 has shipped; the operational spec now lives in `CLAUDE.md`. This archive exists so future re-scaffolds, audits, or onboarding of a fresh Reporter-Claude session have the original setup discipline available verbatim.

The LOCKED items originally in §B.4 (timezone constants) and §B.5 (SQLite schema) are now expressed authoritatively in code:
- Timezone constants + cron: `src/config.py`
- SQLite schema: `src/db.py`

If those diverge from the intent below, treat the code as source-of-truth and the archive as historical context.

---

## A. Mandatory reads (before any work) — original

Read these three files, in order, before Session 0 Step 1:

1. **`OPERATOR_SPEC.md`** (this repo root) — the operator's verbatim ask, decision locks, and the answered-questions record. This is the source-of-truth. When the operator's future ask conflicts with this document, surface the conflict — do not silently drift.
2. **`C:\Users\farha\OneDrive\Desktop\bluechipsignal\research\library\janus_universal_discipline_export.md`** — Janus universal discipline (preservation, self-audit, escape rules, operator collaboration). Adopt these disciplines fully; they are paid for in real errors on other projects.
3. **`CLAUDE.md`** in full again after the first two.

Your first tool call in this project should be `Read` on OPERATOR_SPEC.md.

---

## B. Session 0 — setup steps (executed in order; produced `session_0_report.md`)

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
│   │   ├── weekly_lookback.py     (16:00 IST Sat = 13:00 UTC)
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

# Schedule (all in UTC — the ONLY canonical scheduling timezone).
# Minute is 7/37 not 0/30: GitHub Actions defers/drops top-of-hour crons under load
# (2026-07-29 incident — every :00 and :30 cron missed its first scheduled fire).
# Off-peak minute keeps delivery inside the promised IST window with headroom for
# the additional 5-15 min GH Actions drift documented in each workflow.
CRON_DAILY_MORNING     = "7 4 * * 1-5"    # ~07:07 IST weekdays
CRON_DAILY_WRAP        = "7 16 * * 1-5"   # ~19:07 IST weekdays
CRON_WEEKLY_LOOKBACK   = "7 13 * * 6"     # ~16:07 IST Saturday
CRON_WEEKLY_PREP       = "7 13 * * 0"     # ~16:07 IST Sunday
```
GitHub Actions is the live scheduler (workflow YAML in `.github/workflows/`);
`src/config.py` mirrors these for the currently unused `src/main.py` APScheduler path.
When editing, keep the two in sync.

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
