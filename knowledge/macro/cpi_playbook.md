---
topic_tags: [macro, cpi, inflation, us]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-08-24
provenance: "operator+audit populated 2026-08-24 from BLS methodology + historical BLS post-print reaction studies 2019-2025"
---

# CPI playbook

## What it is
Monthly release from the US Bureau of Labor Statistics measuring the change in prices consumers pay for a basket of goods and services (housing, food, energy, medical, transport, apparel, recreation, education). Two headline numbers dominate:
- **Headline CPI** — the whole basket.
- **Core CPI** — excludes food and energy (the volatile items). This is the Fed's day-of-print focus because it isolates the sticky trend.

Both come as MoM (month-on-month, %) and YoY (year-on-year, %). Consensus is set by economist surveys (Bloomberg, Reuters); the "surprise" = actual minus consensus.

Released ~08:30 ET on the second Tuesday or Wednesday of each month. Precedes the following FOMC meeting by 1-3 weeks. Fed sees the report ~1 hour before public release ("lockup") but doesn't act on it publicly.

## Historical reaction (post-2022 regime)
- **Hot surprise (core MoM ≥0.4% or 5bps above consensus):** 2Y yield +5-15bps, DXY +30-60bps intraday, SPX -0.5% to -1.5% in first hour. Reversal begins by lunch if there's no accompanying commentary shift.
- **In-line print:** Muted reaction. Vol collapse in fixed-income intraday; SPX drift depends on positioning going in (rich IV usually crushes).
- **Cool surprise (core MoM ≤0.2%):** 2Y -5-10bps, SPX +0.5% to +1.5%, DXY -30-50bps. "Bad news is good news" only if unemployment is trending down; otherwise growth-scare risk dominates.
- **Big cool surprise + weak labor context:** Rate-cut odds jump; USD sells hard; gold rallies; regional banks + long-duration tech lead.

## Playbook
- **Positioning going in:** Check SPX 1-week straddle; if ≤0.8% expected move, market is complacent — surprise magnitude gets amplified. If ≥1.5%, market is braced — reactions can fade fast.
- **Sector map:**
  - Hot CPI → banks + energy + short-duration bonds outperform; long-duration tech + gold + rate-sensitive REITs underperform (initial move).
  - Cool CPI → homebuilders + regional banks + long-duration tech lead; USD-cyclical staples lag.
- **Signal quality by component:**
  - Owners' equivalent rent (OER) = ~34% of core CPI. Lags market rents by 6-12 months. Big OER print → sticky headline that markets fade quickly.
  - Core services ex housing ("supercore") = Fed's real focus 2022-2024. Deceleration here matters more than shelter noise.
- **Cross-check with PCE:** CPI and core PCE diverge by 0.3-0.7pp yearly. Fed formally targets PCE (see `pce_playbook.md`); big CPI hot print + friendly PCE 2 weeks later = fade the CPI reaction.

## Common wrongness
- **Overweighting single-month prints in slow-trending regimes.** One monthly beat/miss inside a broader deceleration doesn't reverse the trend. Look at 3-month annualized.
- **Reading MoM without checking the base month.** A weak print easily comparing against a strong month a year prior looks like disinflation but isn't.
- **Ignoring shelter's lag.** Real-time market rent (Zillow, Apartment List) leads OER by ~6-12mo; the CPI shelter component doesn't reflect current conditions.
- **Trading the first-hour spike.** Reactions frequently reverse by session close on days without accompanying Fed speak.

## Reference dates for base-rate anchoring
- CPI Oct 2022 (0.6% core MoM hot): SPX -2.1% intraday, 2Y +25bps — set stage for 75bp hike.
- CPI Nov 2022 (0.2% core MoM cool): SPX +5.5% single-day rally.
- CPI Jul 2023 (0.2% cool): peaked "peak rates" narrative, USD sold off, tech ripped for 2 weeks.
- CPI Mar 2024 (0.4% hot 3rd month in a row): rate-cut expectations pushed from Jun to Sep in 90 minutes.
