---
topic_tags: [macro, bear_market, bottoms, napier, cycle_recognition]
applies_to_reports: [weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Napier, Anatomy of the Bear (4th ed., 2016), cross-cutting themes across 1921/1932/1949/1982 bottoms — 'Good news' + 'Price stability' + 'Bulls and the bear' chapters + Conclusions, pp 40-370"
---

# Bear market patterns — recurring signals across the four great bottoms

Napier studied the four US bear-market bottoms of the 20th century: **August 1921, July 1932, June 1949, August 1982**. Despite very different macro regimes (deflation, Depression, post-war reset, stagflation), the bottoms share a small cluster of recurring signals. This is the regime-recognition framework the bot should apply in weekly synthesis.

## The paradox: good news precedes the bottom

Popular myth says bottoms come in universal despair. Napier's evidence contradicts this: **positive economic data arrives before the price bottom, and the market ignores it.**

- **1921** — WSJ ran steady coverage of stabilizing commodity prices (copper, cotton, wool), rising auto production, Fed commentary affirming recovery — all while the Dow was still falling. Bottom Aug 24, 1921. Good news visible 2-3 months prior.
- **1932** — Rising auto sales, cement price hikes, building permits gains, crop conditions improving in May-Aug. Bottom July 8, 1932 — after 77% decline. Good news buried by banking-crisis noise.
- **1949** — Technical analysts noted the market's *refusal to decline on bad news* in April-May was itself the bullish signal. Bottom June 13, 1949.
- **1982** — End of runaway inflation was the "good news" — Volcker's tightening finally broke the price spiral. Bottom August 1982.

**The mechanism:** bottoms happen when the market has exhausted its ability to be disappointed. Good news doesn't cause the bottom — good news arrival coincides with the exhaustion of bad-news elasticity.

## The "no bad news left to price in" moment

Behavioral signal: **the market stops making new lows despite continuing negative headlines.**

- 1921: volume patterns shifted — very low volumes on down days (panic exhausted), then expanded on up days.
- 1932: after 77% decline and three banking-crisis waves, the market's failure to react to a late-summer bank crisis was the tell.
- 1949: commentators noted indifference to labor strikes, geopolitical tensions, earnings misses. Short interest at levels not seen since Feb 1933, but shorts losing conviction.
- 1982: repeated failure to break below key support despite recession-deepening headlines.

**Pattern for a bot in 2026:** watch for **sequential negative catalysts that fail to produce new lows**. Three bad news items in 2-3 weeks that don't break support → bad-news elasticity is exhausted.

## Price stability arrives before the bottom

Before each equity bottom, the underlying price regime stabilized:

- **1921** — commodity prices (broadest deflation gauge) stabilized in late June-July; corporate bond prices began rising in June while equities were still falling. Deflationary downspiral ending.
- **1932** — corporate bond yields began rising (risk-premium compression) before the equity bottom, indicating default fear was easing despite the ongoing Depression.
- **1949** — government bond yields stabilized near 2.0-2.1% by Q1; the *absence of violent swings* was the signal.
- **1982** — end of runaway inflation. Once CPI momentum broke and Fed policy stance shifted from tightening to maintenance, the equity bottom was weeks away.

**Applies today:** commodity CRB stability + credit spreads narrowing + bond yields range-bound for 6+ weeks = price stability regime shift. Not necessarily the trough, but the pre-condition.

## The convergence checklist (all four bottoms)

No single signal is sufficient. Napier finds bottoms announce themselves through **convergence** of the following, typically within a 2-8 week window:

1. **Volume behavior** — declining volume on down days (panic exhausted); rising volume on up days (constructive accumulation).
2. **Short interest at multi-year highs** — AND showing decline over 2-3 reporting periods (shorts covering slowly, not in panic).
3. **Valuation metrics at historic-cheap extremes** — see `macro/valuation_bottoms.md` for numbers.
4. **Bond stabilization** — corporate and government bonds trading in tight ranges, ideally with yields peaking before the equity low.
5. **Commodity stabilization** — CRB/oil/copper stop making new lows.
6. **Fed policy inflection** — visible shift from tightening to maintenance or easing (rate cuts, reserve reductions, open-market operations).
7. **Sector rotation into quality** — early institutional accumulation shows up as breadth in higher-quality names; investment trusts and insurance companies shift allocations.
8. **Dow-Theory-style confirmation** — parallel indices (industrials + railroads historically, now industrials + transports + financials) hold support without violent penetration.

## The 2-8 week lead

Signals cluster **2-8 weeks BEFORE the actual price bottom, not at it.** In 1921, signals visible in June-early July; bottom late August. In 1949, valuation + sentiment turned April-May; bottom June 13.

The market repricing lags the fundamental turn because it's repricing *past disappointments*, not current conditions.

**For a pitch bot:** when convergence appears, this is a **"gather intelligence" signal, not "buy today."** The buy trigger is:
- Valuation floor **confirmed** (metrics stop deteriorating)
- Volume breakout on a multi-week high
- Fed or credit market signal of policy inflection

## Common wrongness

- **Waiting for universal despair.** Bottoms come with rising good news, not silence.
- **Treating a single signal as the bottom call.** Napier repeatedly emphasizes convergence.
- **Buying on the first good-news day.** The market often continues down for weeks after good news starts arriving. The pattern is *cumulative* good news + *exhaustion* of bad-news elasticity.
- **Ignoring credit stabilization.** Bond markets lead equity bottoms by weeks to months. See `macro/credit_cycle_playbook.md`.
- **Assuming the current regime is unlike all four.** Napier's regimes were wildly different (gold standard, Bretton Woods, floating). The pattern held anyway. Only truly unlimited currency debasement without external anchor might invalidate.

## How to apply in reports

- **Weekly prep** — when macro cluster suggests we're mid-drawdown, apply the checklist. Note which signals are firing and which are absent. Communicate posture: "gather intelligence" vs "positioning phase" vs "post-bottom accumulation."
- **Weekly look-back** — when a defensive tilt worked (or didn't), attribute to which of the 8 convergence signals were firing at the time. Builds calibration over time.
- **Pitch generation impact** — during mid-drawdown weeks, tilt weekly pitches toward Napier's "post-bottom" archetypes (quality names at deep book-value discount, high dividend yield relative to bonds, low short-covering resistance).
- **Do NOT use these signals to override cycle-position read in stable regimes.** They apply specifically to bear-market bottom recognition, not routine bull-cycle positioning.
