---
topic_tags: [macro, nfp, labor, us]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-08-24
provenance: "operator+audit populated 2026-08-24 from BLS Employment Situation methodology + post-NFP reaction studies 2019-2025"
---

# NFP playbook

## What it is
The US Employment Situation report from the Bureau of Labor Statistics, released the **first Friday of each month at 08:30 ET**. Four numbers markets trade off:

1. **Non-Farm Payrolls (headline)** — net new jobs added by US employers excluding farm workers and government-employed uniformed military. From the Establishment Survey (~131k businesses).
2. **Revisions to prior 2 months** — same establishment survey, restated as more data comes in. Increasingly market-moving 2023-2025 as revisions ran consistently negative.
3. **Unemployment Rate** — from the separate Household Survey (~60k households). Different methodology, different definition of "employed."
4. **Average Hourly Earnings (AHE) MoM** — wage growth, feeds directly into services-inflation forecasts.

Consensus is set by Bloomberg/Reuters economist surveys. Whisper number often differs from consensus by 20-40k when ADP (2 days earlier) surprises significantly.

## Historical reaction (post-2022 regime)
- **Hot surprise (headline ≥50k above consensus AND AHE MoM ≥0.4%):** 2Y yield +5-12bps, SPX -0.5% to -1.0% intraday, DXY +30-50bps. Rate-cut odds get pushed further out.
- **In-line print with negative revisions ≥100k combined:** Increasingly common 2024-2025. Bearish for USD, bullish for rates. Bond market treats revisions as more truthful than the headline.
- **Cold surprise (headline ≤50k below consensus, unemployment rate up 0.2pp+):** 2Y -8-15bps, SPX +0.5% to +1.5% (rate-cut relief) — UNLESS unemployment rate move triggers Sahm-rule proximity, in which case growth scare wins and SPX sells with rates.
- **Sahm-rule trigger** (3mo-avg unemployment rate ≥0.5pp above prior 12mo low): historically has never fired outside a recession start. When it triggers, "bad news is bad news" — rate-cut rally lasts 1 day then reverses.

## Playbook
- **The three-line read:** headline, revisions, AHE. Watch the sign combination:
  - Headline hot + revisions negative + AHE tame → net dovish (market discounts headline)
  - Headline in-line + revisions negative + AHE tame → clearly dovish
  - Headline hot + revisions positive + AHE hot → clearly hawkish (rare 2024-2025)
- **Household vs establishment divergence:** When they diverge >200k in the same month, the Household Survey has been more accurate at cycle turns 2007, 2020. Don't dismiss it.
- **Sector map:**
  - Hot NFP → banks + industrials + energy outperform. Long-duration tech + REITs lag.
  - Cold NFP (non-Sahm) → tech + REITs + gold outperform. Cyclicals lag.
  - Sahm-trigger NFP → defensives + long-duration Treasuries + gold outperform. Everything cyclical sells.
- **AHE dominance:** AHE MoM surprise moves 2Y yield more than headline surprise once headline is within ±80k of consensus. AHE is the sticky-services-inflation feed the Fed cares about.

## Common wrongness
- **Trading first-print gyration; the durable move happens after revisions.** 2024 saw multiple months where the first-hour reaction on the headline fully reversed after the initial revision. Sizing pre-revision is trading a signal that will re-write.
- **Treating a headline miss as bullish without the AHE.** Weak jobs + hot wages = stagflationary and hurts everything. This was the Q3 2024 print sequence.
- **Ignoring the establishment/household divergence at cycle turns.** Historically the Household Survey has been the leading signal at inflection.
- **Fading the Sahm-rule trigger day.** When the 3mo-avg unemployment rate crosses the 0.5pp threshold, the historical record is 100% recession-linked (11-of-11 since 1970). Don't dismiss.

## Reference dates for base-rate anchoring
- NFP Jul 2024 (headline miss -114k, unemployment rate 4.3%, Sahm triggered): SPX -1.9%, 2Y -30bps, VIX 20→65 within 2 days.
- NFP Feb 2023 (headline hot +311k, wages tame): SPX +1.6% (rate-cut relief).
- NFP Jul 2022 (headline hot +528k, wages hot): SPX -1.0%, 2Y +20bps.
- NFP May 2024 (headline in-line, prior revisions -111k): USD sold hard, SPX flat.
- NFP Aug 2025 (revisions -258k confirmed cooling narrative): rate-cut Sep pricing locked in.

## /stats-relevant note
Prior audit found trades placed pre-NFP with SL <1.2× typical daily ATR failed 6-of-8 times due to the 08:30 spike breaching the level and reversing later. If a trade must span an NFP release, invalidation must survive the 15-minute vol window (approximate as 1.8× 20-day ATR).
