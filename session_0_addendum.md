---
title: FinanceReporter — Session 0 Addendum
date: 2026-07-28
status: FORMAT LOCKED — awaiting API key + hosting to finish Session 0
supersedes: nothing in session_0_report.md; adds format/content revisions on top
---

# Session 0 Addendum

Iterated on real Telegram sends 2026-07-28 evening. 21 live messages exchanged with the operator's DM (@Cyberekt, chat_id 226763300) via `@TheCapitalOrder_bot`. Format locked; content style locked; two spec revisions recorded.

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

Live-send msg_ids 6-21 in the operator's DM cover every iteration. Final approved state: msg_ids 18-21.

## 2. Content style locked

**Pitch thesis** rewritten as "ready-to-repeat pitch" prose (`src/pitches.py::_SYSTEM_PROMPT`, mirrored in `src/llm_providers/dummy.py`):
- 3-5 sentences of plain English an FA can read aloud to a client
- Named catalyst by date, named mechanism, named risk
- No jargon (`"trading 12% cheaper than its 5-year average"` not `"12% discount to 5-yr median PE"`)
- No hedging filler, no exclamation points

**Key factors** are ≤12-word plain-English bullets, 3-4 per pitch.

**Calendar friendly-ification** — `src/event_explanations.py::friendly_name()`:
- Expands 30+ acronyms in parens on first occurrence (CPI → Consumer Price Index; NFP, PPI, PCE, GDP, PMI, FOMC, ECB, BOJ, RBA, JOLTS, ADP, etc.)
- Rewrites `m/m` / `y/y` / `q/q` → "monthly" / "yearly" / "quarterly"
- Combined with the 1-line `explain()` gives every event a `WHAT · WHY` reading

**Company names** — `src/company_names.py::name()` maps all 98 tickers in the blue-chip universe to human names ("Apple (AAPL)" not just "AAPL"). Pitch headers use this format.

## 3. Spec revisions (recorded 2026-07-28)

Per operator direction after pilot review:

| Revision | Location | Before | After |
|---|---|---|---|
| **Pitch count** | `CLAUDE.md §C3`, `§E.11`, `§D.1.a Part 2 header`; `OPERATOR_SPEC.md §3.1 Part 2`, `§6.B row 7` | 3 pitches / morning | 2 pitches / morning |

Both spec files edited in place with an inline `(revised 2026-07-28)` note. Trades stay at 3 (1 commodity + 1 stock + 1 crypto — §C2 unchanged). Star rubric + all other §C locks unchanged.

## 4. Additional additive improvements

- **`event_explanations.py`** — 60+ macro events with 1-line meanings, drawn from macro playbook conventions
- **`_style.py`** — shared visual helpers; new reports auto-inherit the vocabulary
- **Weekly Look-Back SECTION 6 "OBSERVATIONS & ANOMALIES"** — now produces real data-driven observations (direction bias, ticker concentration, earnings-flagged outcomes, TP/SL streaks, per-class trade breakdowns) with brief WHY labels
- **`daily_wrap` `TOMORROW` block** — 3-star events for tomorrow with friendly names + explanations, matching morning's calendar style
- **Two Telegram escape bugs fixed** during iteration:
  1. `daily_wrap`: unescaped `-` inside `_· 3-star events · IST_`
  2. `weekly_lookback`: unescaped `(` `)` in `_(populated after n≥20 in one bucket)_`

Tests: **49/49 passing** across all edits.

## 5. Session 0 status summary

| Check | Status |
|---|---|
| Environment + venv + deps | ✅ done (session_0_report §1) |
| Telegram bot created | ✅ `@TheCapitalOrder_bot` (token in `.env`) |
| Telegram chat_id acquired | ✅ 226763300 (@Cyberekt) — operator's DM |
| Real Telegram send working | ✅ 21 live sends 2026-07-28 |
| Format + content approved | ✅ operator confirmed 2026-07-28 |
| Persistence-before-send | ✅ verified via DB inspection |
| Knowledge library (98 blue-chip stubs) | ✅ §E.19 test enforces |
| 49 tests passing | ✅ green |
| Hosting picked | ⏳ awaiting operator (Oracle Cloud Always Free recommended) |
| Real Gemini API call verified | ⏳ awaiting `GEMINI_API_KEY` in `.env` |
| Kill switches wired | ✅ per-report + global DRY_RUN in `.env` |
| Scheduler wired | ✅ `src/scheduler.py` + `src/main.py` |
| `DRY_RUN=false` for production | ⏳ operator flips after key + hosting done |

## 6. Two remaining blockers before Phase 1

1. **Operator provides `GEMINI_API_KEY`** in `.env`. I re-run one pilot with real Gemini and paste the output as a follow-up so we prove the LLM produces the client-ready prose the prompt requests (not just the dummy canned copy).
2. **Operator picks hosting** — my recommendation stands: Oracle Cloud Always Free VM (systemd unit for `python -m src.main`).

Once both close: flip `DRY_RUN=false` in `.env`, deploy to host, kill switches all `false`, cron ticks start. First live report will be next scheduled trigger.

## 7. Follow-ups queued (not blocking)

- Fill `knowledge/house_view/active_themes.md` with real current themes (operator/friend)
- Begin book extraction into `knowledge/macro/*` + `knowledge/blue_chip/*_facts.md` (Damodaran, Marks, Napier per OPERATOR_SPEC.md §9)
- Address `datetime.utcnow()` deprecation warnings from Python 3.14 (cosmetic, non-blocking)

Personal research — not investment advice.
