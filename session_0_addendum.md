---
title: FinanceReporter — Session 0 Addendum
date: 2026-07-28
status: SHIPPED — Phase 1 live on GitHub Actions; first scheduled report fires 2026-07-29 04:00 UTC
supersedes: nothing in session_0_report.md; adds format/content revisions + deployment
---

# Session 0 Addendum

Iterated on real Telegram sends 2026-07-28 evening. 24+ live messages exchanged; format locked; content style locked; two spec revisions recorded; **deployed to GitHub Actions and shipped to the friend's Market Report channel**.

## 1. Format locked (operator approved 2026-07-28)

Every report uses the shared visual language in `src/reports/_style.py`:

- **Heavy `━` dividers** (22 chars) between report sections; **thin `╌`** between cards within a section
- **Colored direction dots** — 🟢 long, 🔴 short, 🟡 low-conviction (0-1 stars, overrides direction)
- **Section banners** — numbered format: `{emoji} *SECTION N · TITLE*  _· subtitle_`
- **Three distinct textures per report** to visually separate sections:
  - **Blockquote cards** (`>` indented) — calendar events with what/why lines
  - **Flat prose** — pitch theses + key factors + entry
  - **Code-block cards** (```gray monospace```) — Entry/TP/SL levels with computed %/RR
- **Emoji anchors** on every data label — ☕/🌙/📅/📖/📍/🎯/💡/⚠️/🔒
- **Greetings/wishes** — morning opens with `☕ _Good morning._` + closes with `_Have a productive day._`; wrap closes with `🌙 _Have a good night._`; both weekly reports close with `📅 _Have a good week ahead._`

## 2. Content style locked

**Pitch thesis** rewritten as "ready-to-repeat pitch" prose (`src/pitches.py::_SYSTEM_PROMPT`, mirrored in `src/llm_providers/dummy.py`):
- 3-5 sentences of plain English an FA can read aloud to a client
- Named catalyst by date, named mechanism, named risk
- No jargon, no hedging filler, no exclamation points

**Key factors** are ≤12-word plain-English bullets, 3-4 per pitch.

**Calendar friendly-ification** — `src/event_explanations.py::friendly_name()`:
- Expands 30+ acronyms in parens on first occurrence (CPI → Consumer Price Index; NFP, PPI, PCE, GDP, PMI, FOMC, ECB, BOJ, RBA, JOLTS, ADP, etc.)
- Rewrites `m/m` / `y/y` / `q/q` → "monthly" / "yearly" / "quarterly"
- Combined with the 1-line `explain()` gives every event a `WHAT · WHY` reading

**Company names** — `src/company_names.py::name()` maps all 98 tickers to human names ("Apple (AAPL)" not just "AAPL"). Pitch headers use this format.

## 3. Spec revisions (recorded 2026-07-28)

Per operator direction after pilot review:

| Revision | Location | Before | After |
|---|---|---|---|
| **Pitch count** | `CLAUDE.md §C3`, `§E.11`, `§D.1.a Part 2 header`; `OPERATOR_SPEC.md §3.1 Part 2`, `§6.B row 7` | 3 pitches / morning | 2 pitches / morning |

Both spec files edited inline with `(revised 2026-07-28)` note. Trades stay at 3. Star rubric + all other §C locks unchanged.

## 4. Provider switch — Gemini → Groq

Original plan (§C9) had Gemini 2.0 Flash as default. During deployment:
- Operator's Google Cloud project had billing attached — Gemini would incur ~$0.50/mo charges, violating `§E.6` "everything free" lock
- **Switched to Groq Llama 3.3 70B** (already built as the fallback per §C9)
- One-line env change: `LLM_PROVIDER=groq`
- Real Groq calls verified with msg_ids 22-24 in operator's DM; then all 5 workflow runs from GitHub Actions to the channel

**Groq TPM budget management:** free tier caps at 12K tokens/min. Original knowledge-library payload was 17K tokens because all 98 blue-chip ticker stubs (~500 tokens each of placeholder text) were being sent. Fix in `src/knowledge.py::_is_stub()` — skip files marked as scaffold stubs OR whose body is >60% `(stub` markers. Post-fix payload is ~7K tokens; well under budget with room for expansion as knowledge files get populated.

## 5. Additional improvements shipped

- **`event_explanations.py`** — 60+ macro events with 1-line meanings
- **`_style.py`** — shared visual helpers; new reports auto-inherit the vocabulary
- **Weekly Look-Back SECTION 6 "OBSERVATIONS & ANOMALIES"** — now produces real data-driven observations (direction bias, ticker concentration, earnings-flagged outcomes, TP/SL streaks, per-class trade breakdowns) with brief WHY labels
- **`src/run_report.py`** — CLI entrypoint used by GitHub Actions workflows
- **Two Telegram escape bugs fixed** during iteration (unescaped `-` in daily_wrap; unescaped `(` in weekly_lookback)

Tests: **49/49 passing**.

## 6. Deployment to GitHub Actions

- **Primary repo:** `farhungers/finance-reporter` (private)
- **Backup repo:** `farhungers/finance-reporter-backups` (private) — receives DB mirror on every daily_backup run
- **Data persistence:** `data-store` orphan branch in the primary repo, force-updated by every workflow that produces a DB write
- **Secrets configured (4):** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GROQ_API_KEY`, `BACKUP_REPO_PAT`
- **`TELEGRAM_CHAT_ID` = -1004498574275** — the private "Market Report" channel operator created, with `@TheCapitalOrder_bot` as admin

**Cron schedules (UTC, DST-invariant):**

| Workflow | Cron | IST equivalent | Days |
|---|---|---|---|
| daily_backup | `30 3 * * *` | 06:30 IST | daily |
| daily_morning | `0 4 * * 1-5` | 07:00 IST | Mon-Fri |
| daily_wrap | `0 16 * * 1-5` | 19:00 IST | Mon-Fri |
| weekly_lookback | `0 13 * * 6` | 16:00 IST | Sat |
| weekly_prep | `0 13 * * 0` | 16:00 IST | Sun |

**Smoke tests 2026-07-28:** all 5 workflows manually triggered via `workflow_dispatch`, all completed successfully. First scheduled real run: daily_backup at 03:30 UTC 2026-07-29, then daily_morning at 04:00 UTC 2026-07-29.

**Notable deploy detour:** reusable-workflow permission inheritance caused `startup_failure` on the first attempts. Root cause: caller workflows without explicit `permissions: contents: write` couldn't grant it to the reusable via `secrets: inherit`. Fix: inlined all 5 workflows (drop reusable pattern), each declares its own `permissions:` block. Trade-off: some duplication across YAML files, but zero cross-workflow coupling.

## 7. Session 0 status — SHIPPED

| Check | Status |
|---|---|
| Environment + venv + deps | ✅ |
| Telegram bot created | ✅ `@TheCapitalOrder_bot` |
| Telegram chat_id (channel) | ✅ `-1004498574275` (Market Report channel) |
| Real Telegram send working | ✅ 24 DM sends + 4 channel workflow sends |
| Format + content approved | ✅ operator 2026-07-28 |
| Persistence-before-send | ✅ verified via DB inspection |
| Knowledge library (98 blue-chip stubs) | ✅ §E.19 test enforces |
| 49 tests passing | ✅ |
| Real LLM verified (Groq) | ✅ msg_ids 22-24 + all 5 workflow runs |
| Hosting picked + deployed | ✅ GitHub Actions private repos |
| Kill switches wired | ✅ per-report env vars + global DRY_RUN |
| Scheduler wired | ✅ 5 workflow crons live |
| First live report fires | ⏳ 2026-07-29 04:00 UTC (07:00 IST tomorrow) |

## 8. Follow-ups queued (non-blocking)

- Populate `knowledge/house_view/active_themes.md` with real current themes
- Book extraction into `knowledge/macro/*` + `knowledge/blue_chip/*_facts.md` (Damodaran, Marks, Napier per OPERATOR_SPEC.md §9)
- Address `datetime.utcnow()` deprecation warnings (Python 3.14 — cosmetic)
- MMC, FI yfinance 404s — non-blocking; guarded by defensive None-return in `market_data.yf_quote`
- Add `/stats` webhook handler on Cloudflare Workers free tier (deferred to Session 2)
- Node.js 20 deprecation warning on `actions/checkout@v4` + `actions/setup-python@v5` — cosmetic; GitHub is migrating to Node 24 automatically

Personal research — not investment advice.
