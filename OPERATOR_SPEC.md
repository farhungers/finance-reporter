---
title: FinanceReporter — Operator spec (frozen)
captured_by: Pythia Janus (CEO mode)
date: 2026-07-28
revised: 2026-07-28 same session — added §6.B (8-point walkthrough), §6.C (principles), §3.5 (knowledge library), §6.D (v1 add bundle), §9 (book asks)
source: operator conversation, 2026-07-28
status: FROZEN — do not edit; further clarifications go to a new "spec_addenda.md" file
---

# Operator spec — verbatim capture + decision locks

## Section 1 — Background (operator's context, 2026-07-28)

> "my friend is a financial advisor on Wall Street. He is struggling to get the daily news briefs and preparing his daily pitches ever since he got married and has a few children. So I want to help him out by making a Telegram bot."

**Actual user:** operator's friend (Wall Street FA, US-based).
**Operator's role:** commissioning + reviewing on friend's behalf. Friend is downstream reader; operator is the immediate collaborator.
**Cost constraint:** zero recurring monthly cost — all APIs and services must be free tier or free forever. Operator can purchase books/articles on request.

## Section 2 — Reports and schedule (LOCKED by operator, 2026-07-28)

| Report | Send time (Istanbul, LOCKED) | Send time (UTC, canonical cron) | Days | Purpose |
|---|---|---|---|---|
| Daily Morning | 07:00 IST | 04:00 UTC | **Mon-Fri only** | Executive summary of today's events + pitches + trades. ~5 min read. |
| Daily Wrap | 19:00 IST | 16:00 UTC | **Mon-Fri only** | Mid-US-session wrap: anomalies, notable moves, tomorrow's key events. ~1 min read. |
| Weekly Look-Back | 16:00 IST Saturday | 13:00 UTC Sat | Saturday only | Past-week reflection: pitch/trade accuracy, findings, anomalies. |
| Weekly Prep | 16:00 IST Sunday | 13:00 UTC Sun | Sunday only | Next-week horizon: important events, macro setup, sector angles. |
| `/stats` (ad-hoc, v1) | Any time, on demand | On Telegram command | Any | Queryable accuracy + open positions + active themes. Rate-limited to 1 per 60s per chat. |

**Total scheduled sends per week: 12** (5 daily-morning + 5 daily-wrap + 1 Sat lookback + 1 Sun prep). `/stats` is on-demand, not scheduled.

**Timezone in message bodies:** all displayed timestamps are **Istanbul time (IST)** per operator preference. ET is used only for internal market-hours calculations, never in message text.

Operator quote (times): *"7 am istanbul time, which is 4am UTC, this is for the daily report - 7 pm istanbul time which is 4 pm UTC for the wrap the day report. - for the weekly reports 4 pm saturday which is 1 pm UTC for the weekly wrap report. and 4 pm istanbul time sunday which is 1 pm UTC for the beginning of the week preparation report. these times are final plz remember."*

Operator quote (weekend): *"daily reports are just from monday to friday 5 days a week, and additionaly 2 weekend reports 1 at saturday for the week wrap and 1 for sunday for next week preprations."*

## Section 3 — Report content specs

### 3.1 Daily Morning — three parts

**Part 1: Today's calendar (with brief context)**
- Events happening today; special emphasis on 3-star events per Investing.com convention (source will be ForexFactory RSS, not investing.com)
- Emphasis on high-market-impact releases: CPI, PPI, NFP, FOMC statements, Fed Chair speaking, unemployment claims, GDP, PMI
- Brief explanation of each: what it is, what forecast/previous is, expected market consequence
- Reminder of tomorrow's key events
- Reminder of the week's big events (if any not yet named)
- Times in IST; on quiet days, always show at least the next-tier events (§C11 "never omit")

**Part 2: 2 pitches (client-facing, blue chip) — ALWAYS 2** (revised from 3 on 2026-07-28 per operator after pilot review; see spec_addenda if formalized)
- Blue chip asset universe (S&P 100 + top-15 US large caps by market cap; per CLAUDE.md §C3)
- Star rating (0-5) for pitch quality/confidence; rendering per CLAUDE.md §C14
- Deep reasoning (client-usable) — 2-3 sentences of thesis
- Key factors — bullet list
- Rough entry point hint
- **Earnings within 3 trading days: mandatory `📅 Earnings [date IST]` line + auto-trigger `catalyst_proximity=1` (§C16)**
- Low-star pitches (0-1) SHIP with a 1-line precise warning

Operator quote: *"pitches = deep (client-usable)"*

**Part 3: 3 trades (his own trading; variety) — ALWAYS 3**
- Variety: 1 commodity, 1 stock, 1 crypto — one per class always shipped
- Precise entry, TP, SL
- 1-2 line reasoning (short; his own book, he already reads tape)
- Star rating (0-5); rendering per CLAUDE.md §C14
- Low-star trades (0-1) SHIP with a 1-line precise warning
- Never substitute across classes; never lower rubric to fake higher stars

Operator quote: *"trades = 2-3 with varieties of assets along with entry, tp and sl"*
Operator addendum: *"the star system will be useful here showing the trade with a low star 0/5 or 1/5 and warn him with a 1 line, avoid jokes and make the lines easy to understand and precise"*

### 3.2 Daily Wrap
- 1 min read (~400 tokens display)
- Anomalies / notable moves worth mentioning
- Interesting facts about the tape
- Brief calendar for tomorrow (IST)

### 3.3 Weekly Look-Back (Saturday)
- Reflection on past week
- Highlights, findings, interesting facts, anomalies
- **Accuracy report on past week's pitches and trades** (how accurate they were)
- Rubric calibration proposals (only when n≥20 in a bucket)
- **Knowledge library report** (only when n≥20 with populated `knowledge_sources_used`): top-cited sources by hit rate, sources appearing in >5 failed pitches (prune candidates)
- Honest reporting: no softening of negative findings

### 3.4 Weekly Prep (Sunday)
- Next week's horizon
- Important events (IST times)
- Macro setup going in
- **Earnings this week** (blue-chip universe)
- Sector/theme angles drawn from `knowledge/sectors/*`

Operator quote (single Sunday report): *"just 1 sunday report for preparation of what's coming next"*

### 3.5 Knowledge library — v1 (operator-approved 2026-07-28)

Operator asked: *"would it be helpful to leave it a knowledge library relevant to his work so it doesn't have to research topics we already know?"*
Janus answer: **strong yes.** Approved for v1.

**Purpose:** curated markdown reference notes at `knowledge/*` that get loaded into the LLM's context per report. Grounds outputs in real curated knowledge instead of LLM-guessed patterns; improves consistency across days; via Gemini's context caching adds near-zero token cost.

**Folder structure:**
- `knowledge/macro/` — event playbooks (CPI, FOMC, NFP, fed-speak taxonomy)
- `knowledge/sectors/` — sector regime reads (energy, tech, financials, healthcare)
- `knowledge/blue_chip/` — one file per ticker in the pitch universe (MANDATORY per §E.19)
- `knowledge/technicals/` — support/resistance conventions, ATR sizing
- `knowledge/correlations/` — DXY-gold, VIX-SPX, 10Y-growth, etc.
- `knowledge/house_view/` — proprietary views + `client_language.md` + `active_themes.md`

**Provenance discipline:** every knowledge chunk enters the LLM context with a `source_id` tag; the LLM's output includes `knowledge_sources_used` (JSON array) written to DB. Weekly look-back correlates sources with pitch outcomes → library gets pruned/corrected over time. LLM MUST NOT paste knowledge text verbatim — must transform/apply.

**Content acquisition:** operator-supplied books/articles (see §9 book asks) + free authoritative public sources.

**Growth model:** operator/friend can contribute new files anytime; git version-controlled; adding a blue-chip ticker requires adding its facts file in the same commit.

### 3.6 `/stats` slash command — v1

Ad-hoc Telegram command. Returns running accuracy stats + open positions + active themes. Same accuracy engine as weekly look-back. Rate-limited 1 per 60s per chat.

## Section 4 — Confidence rating system (LOCKED)

Operator asked for 5-star confidence rating on both pitches and trades. Range extended to 0-5 after walkthrough point 6.

**Janus proposal (accepted):** rubric-based scoring + accuracy-loop calibration over 4-8 weeks.

**Rubric factors (each 0 or 1; sum = stars):**
- `macro_alignment`
- `technical_setup`
- `catalyst_proximity` **← auto-set to 1 when `earnings_within_3d=1`; LLM cannot override**
- `base_rate_support`
- `risk_reward`

**Sum computed in Python, not by the LLM.** LLM returns JSON booleans only.

**Visual rendering (locked, walkthrough point 7 addendum):**
- 0/5: ☆☆☆☆☆
- 1/5: ⭐☆☆☆☆
- 2/5: ⭐⭐☆☆☆
- 3/5: ⭐⭐⭐☆☆
- 4/5: ⭐⭐⭐⭐☆
- 5/5: 🌟🌟🌟🌟🌟 (gold — visually distinct)

Operator quote (rubric): *"5- this is fine 'I strongly recommend the first. It also unlocks the weekly look-back's actual value'"*
Operator quote (gold star): *"lets give the 5 start reads a gold start addittionally"*

Rubric detail lives in `CLAUDE.md §D.2`.

## Section 5 — Compliance / legal (LOCKED)

Janus flagged three FINRA/SEC concerns: FINRA Rule 2210 (public communications), Reg BI (recommendation suitability), Off-channel comms (Telegram archival).

Operator response: *"leave the legalities to him and his firm, just focus on making a great product."*

**Locked interpretation:**
- Product is a *personal-use idea generation tool for the friend*.
- Single-line compliance footer on every report: *"Personal research — not investment advice. Verify before acting."*
- No further compliance features designed into the product.
- Any future request that would repurpose reports as direct client communications must be flagged and re-confirmed with operator before shipping.

## Section 6 — Answered clarifying questions (2026-07-28 conversation record)

### 6.A — Initial 5-question surfacing

| # | Janus question | Operator answer | Impact |
|---|---|---|---|
| 1 | "1pm Istanbul" vs "5pm message"? Also — 7am Istanbul = midnight ET, is friend supposed to read while asleep? | Locked schedule: 7am IST daily morning, 7pm IST daily wrap, Sat 4pm IST look-back, Sun 4pm IST prep. Times are final. | Schedule locked in `CLAUDE.md §B.4`. |
| 2 | Trades reasoning depth: "deep" or "1 line"? | Pitches deep, trades: 2-3 with variety of assets + entry/TP/SL. | Trades = 1-2 line reasoning; pitches = deep. |
| 3 | Two Sunday reports at same time — combined or separate? | Only one Sunday report: preparation for what's coming. Weekly wrap is on **Saturday**. | Weekly look-back → Saturday. Weekly prep → Sunday. |
| 4 | Compliance — personal use or client-facing? | "Leave the legalities to him and his firm, just focus on making a great product." | Personal-use tool + single-line footer. |
| 5 | Star calibration approach? | Rubric + accuracy loop approved. | `CLAUDE.md §D.2`. |

### 6.B — 8-point design walkthrough

| # | Topic | Options presented | Operator answer | Impact |
|---|---|---|---|---|
| 1 | Cron TZ + display TZ | A1 (UTC cron) / A2 (IST cron) / A3 (ET cron) × B1 (ET display) / B2 (IST display) / B3 (both) | **A1 + B2** — UTC cron, Istanbul-only display | `C1` locked. |
| 2 | Star rubric mechanism | M1 (Python) / M2 (LLM freeform) / M3 (vibes) / M4 (hybrid) / M5 (weighted) | **M1** — 5 booleans summed in Python | `C4` locked; M5 = upgrade path. |
| 3 | Persistence timing | P1 (before send) / P2 (after send) / P3 (before + confirm) / P4 (transactional) | **P1** — row is truth-of-record | `C10` locked. |
| 4 | Blue-chip universe | U1 (S&P 100+top15) / U2 (S&P 500) / U3 (Dow+Nasdaq) / U4 (custom) / U5 (mkt cap thresh) / U6 (U1+ADRs) | **U1** | `C3` locked. |
| 5 | LLM provider (raised due to "no money") | L1 (Anthropic) / L2 (Gemini) / L3 (Groq) / L4 (Cerebras) / L5 (Ollama) / L6 (agnostic wrapper) | **L6 + L2 default** — provider-agnostic wrapper, Gemini 2.0 Flash default | `C9` locked. |
| 6 | Trade variety enforcement | V1 (gap) / V2 (substitute) / V3 (lower thresh) / V4 (skip section) / V5 (gap + note) | **V5-modified** — always ship 3, low-star get 1-line warning | `C2` locked. Star scale 0-5. |
| 7 | Pitch variety enforcement | PS1 (like trades) / PS2 (gap) / PS3 (hide stars) / PS4 (ship qualified + gap) | **PS1** via principle override — originally 3 pitches; revised to 2 on 2026-07-28 by operator after pilot | `C3` locked (revised 2026-07-28). |
|   | Addendum | Gold star for 5/5 | Added: 5/5 renders as 🌟 | `C14` locked. |
| 8 | Weekend behavior | W1 (Mon-Fri) / W2 (7-day) / W3 (weekend AM only) | **W1** — 12 messages/week | `C13` locked. |

### 6.C — Locked principles from walkthrough (durable)

| Principle | Source | Statement |
|---|---|---|
| Cost constraint | Operator 2026-07-28 | *"everything free... on the other hand the claude agent can ask for any book or articles even if they cost money"* — no paid APIs; books/articles can be requested. `E.6`, `G.3` |
| Product principle | Operator 2026-07-28 | *"we want to always provide him with something never with nothing, always a next best thing that we have, and we will clearly show how confident we are with the star system, so he can decide easily if he will use them or not"* — governs edge cases. `C11`, `E.11`, `E.12` |
| Style rule | Operator 2026-07-28 | *"avoid jokes and make the lines easy to understand and precise"* — applies to all outputs. `C12`, `E.13` |

### 6.D — v1 additions bundle (same session, after walkthrough)

Operator asked: *"is there any other thing you would suggest we add to this project? also would it be helpful to leave it a knowledge library relevant to his work so it doesn't have to research topics we already know?"*

Janus proposed a 5-item add menu ranked by value; operator responded *"go ahead with your recommendation."*

| Feature | v1 or later? | Locked as |
|---|---|---|
| Knowledge library (curated markdown notes; provenance-tagged; loaded per report) | **v1** — Session 0-2 | `C15` |
| Earnings calendar integration (auto-trigger `catalyst_proximity` for pitched tickers within 3d) | **v1** — Session 0-2 | `C16` |
| `/stats` slash command (queryable accuracy + positions + themes) | **v1** — Session 0-2 | `C17` |
| Yesterday's follow-up card in daily-morning | **Session 3** (scope-locked) | `C18`, `D.10` |
| Emoji feedback loop (👍/👎/🤔 on messages) | **Session 3** — schema hooks in v1 | `C18`, `D.10` |
| Age-of-thesis warning (>10 days no-move flag) | **Session 3** (scope-locked) | `C18`, `D.10` |
| Portfolio tracking / per-client holdings | **REFUSED for v1** — compliance surface + PII risk | `C19`, `G.24` |
| Voice cloning / style transfer | **REFUSED for v1** — LLMs sound like caricatures; use `house_view/client_language.md` instead | `C19`, `G.25` |
| Breaking-news / alert interrupts | **REFUSED for v1** — false-positive risk; friend has Bloomberg | `C19`, `G.26` |
| Bot self-reflection / meta-analysis loop | **REFUSED for v1** — LLM self-critique unreliable | `C19`, `G.27` |

**Session 3 unlock criteria (all three required):**
- (a) Session 0-2 pilot approved and Phase 1 running
- (b) Real deployment for ≥4 weeks with kill switches off
- (c) Accuracy loop has n≥20 resolved in at least one star bucket

## Section 7 — Original operator spec (verbatim, for tie-break reference)

> "I want this TG bot give my friend few different reports, 2 daily, 1 at 7am istanbul time and 1 at 1pm istanbul time. this is designed for a financial advisor who is in the states and needs to know important events of that day and that week so big emphasis on knowing 'https://www.investing.com/economic-calendar' [screenshot referenced] especially the 3 star events, and overall the events that have big impact on the market, CPI, chair speaking about rates and etc. so in the morning he should have that day's important events reminded to him, this whole morning message should be a fast and easy read maybe 5 min max, executive summary style where he can read and understand what's coming that day, also aside from the calendar, I want the bot to develop reasoning and analytic abilities to provide 3 pitches for that day and use a star out of 5 system to show the confidence quality of the pitches, the pitches should be made so he can use for clients and also be able to open good quality trades, so it should have reasoning and if possible a rough entry point, these 3 daily pitches/and possible trades should be designed in a way that can be used to present to the clients as possible investments, so it should be brief and key factors should be mentioned so just by reading this report he can easily have enough pitches for that day. - the report should also have 3 trades for that day with precise entry, tp and sl, these trades should have deep reasoning, and good variety, something like 1 commodity, 1 stocks and 1 crypto, not a lot of reasoning is required here maybe just 1 line, and these must also have the star system. - so that's pretty much it for the daily report, it has 3 parts, that day's important events with brief explanations about them, expectations of the consequences, and a short reminder of tomorrow's event and if the week has a major event that should briefly be there as well to cover the calendar bases. part 2 are the possible pitches, for blue chip assets - and part 3 are the trades which anything goes. this is the main idea for the 7am message. now moving on to the 5pm message, this is for wrapping the day, if there was any anomalies that day worth mentioning or anything interesting add it there, this should be a 1 minute read cause it's the end of the day, and it's should briefly mention the calendar for tomorrow. - now moving on to the weekly report, I also want this bot to provide 1 weekly report presented at sunday 4 pm, a report of what's on the horizon for the next week, and important events. - and there should be a second weekly report which is released same time 4pm istanbul time this one designed to close the week and take a look at the past week and highlight findings and interesting facts anomalies a fast read and reflection to the quality of the pitches and trades, and briefly reporting how accurate they were."

Note the surface-level contradictions in the original spec (1pm vs 5pm; deep vs 1-line trades; two Sunday reports; investing.com as reference). Section 6.A/6.B/6.D records how each was resolved via clarification.

## Section 8 — Non-scope (deliberately excluded from v1)

Not requested by operator; do NOT build without explicit ask:

**Refused (per §C19 lock, 2026-07-28):**
- Portfolio tracking / per-client holdings (compliance + PII risk)
- Voice cloning / style transfer (LLM caricature risk; use `house_view/client_language.md`)
- Breaking-news / real-time alert interrupts (false-positive risk; friend has Bloomberg)
- Bot self-reflection / meta-analysis loops (LLM self-critique unreliable)

**Scope-locked NOT-v1 (Session 3 or later, per §C18):**
- Yesterday's follow-up card in daily-morning
- Emoji feedback loop consumer (schema hooks are in v1)
- Age-of-thesis warning

**Structural non-scope (v1+):**
- Options analysis or options-specific pitches
- Portfolio-level suggestions (allocation, rebalancing)
- Multi-user / client management (whitelabeling, per-client customization)
- Web dashboard / non-Telegram UI
- Automated trade execution (bot signals; does not trade)
- Backtest harness for pitches (post-Session 5)
- Any paid API dependency (locked "everything free")

Any of these can be added in a future spec addendum (`spec_addenda.md`); do NOT scope-creep in v1.

## Section 9 — Book asks (operator offered content acquisition, 2026-07-28)

Operator quote: *"the claude agent can ask for any book or articles even if they cost money and ill provide"*

**Janus's initial asks (v1 knowledge library seeding):**

| Book | Author | Priority | Extracts into |
|---|---|---|---|
| The Little Book of Valuation | Aswath Damodaran | HIGH | `knowledge/blue_chip/*_facts.md` valuation notes; sector base rates |
| Mastering the Market Cycle | Howard Marks | HIGH | `knowledge/macro/regime_reads.md`; `knowledge/house_view/philosophy.md` seed |
| Anatomy of the Bear | Russell Napier | MEDIUM | `knowledge/macro/bear_market_patterns.md`; `knowledge/macro/valuation_bottoms.md` |

**How to use:** operator (or friend) acquires; Reporter-Claude extracts 5-15 topic notes per book at operator's pace. Not blocking on Session 0. Knowledge library ships with stubs; content accumulates over weeks.

**Future asks:** Reporter-Claude may request additional books/articles during Sessions 1+ as gaps in the library become clear. Format: propose in `session_N_report.md`, operator decides.
