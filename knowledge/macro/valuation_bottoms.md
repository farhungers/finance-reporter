---
topic_tags: [macro, valuation, bear_market_bottoms, cape, tobin_q, napier]
applies_to_reports: [weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Napier, Anatomy of the Bear (4th ed., 2016), 'Structure of the market' + 'The stock market' chapters across 1921/1932/1949/1982, plus Conclusions, pp 60-370"
---

# Valuation bottoms — the quantitative anchors at the four great lows

Napier's central quantitative finding: bear-market bottoms cluster at remarkably consistent valuation levels across radically different macro regimes. When the current market trades near these levels, the probability of a durable bottom is materially higher than at any other time.

## The four bottoms at a glance

| Metric | 1921 (Aug) | 1932 (Jul) | 1949 (Jun) | 1982 (Aug) | Normal (long-run) |
|---|---|---|---|---|---|
| Tobin's Q | ~0.28 | ~0.30 | ~0.29 | ~0.27 | ~1.0 (fair value) |
| CAPE (Shiller PE) | ~7.4× | ~4.7× | ~11.7× | ~9.9× | ~15-17× median |
| Dividend yield | high, > bond yield | > bond yield | 4% (vs 2.46% AAA bond) | very high | ~2% recent decades |
| Short interest | multi-year high | multi-year high | 16-year high, 1.64M shares | multi-year high | — |
| Stocks below book | very high % | very high % | ~18% of NYSE (~225 names) | high % | ~5-10% typical |

**Consistency is the point.** Very different macro backdrops, similar valuation floors.

## Tobin's Q — Napier's favorite

Tobin's Q = market cap ÷ replacement cost of company assets.

- Q < 1: market undervalues companies vs cost to rebuild them.
- Q < 0.3: extreme; bear-market bottom range.
- Q > 1.5: extreme overvaluation; late-cycle warning.

At all four bottoms, Q compressed to 0.27-0.30 — 70%+ discount to replacement cost. This is a floor because at those levels, corporate M&A becomes cheaper than greenfield build, forcing consolidation and floor-setting bids.

**How to read today:** if Q for the S&P is <0.5, we're in "gather intelligence" territory; <0.35 is "positioning phase"; <0.30 is the four-bottom historical floor.

## CAPE (cyclically adjusted PE, Shiller)

Uses 10-year average earnings to smooth cyclical distortions.

- Historic median: ~15-17×
- Peak (2000): ~44×
- 1921 bottom: 7.4×
- 1932 bottom: 4.7× (deepest ever)
- 1949 bottom: 11.7× (post-war anomaly — high earnings recovery masked severity)
- 1982 bottom: 9.9×

**Practical bands** for pitch context:
- CAPE < 12: deep-value regime; overweight cyclicals/leverage
- CAPE 12-17: normal
- CAPE 17-25: expensive; overweight quality/defensive
- CAPE > 25: extreme; defensive posture warranted regardless of narrative

Note: 1949's higher CAPE (11.7×) with a strong equity bottom shows CAPE alone is not sufficient — the *rate of earnings recovery* matters. In 1949, earnings had already recovered from war-year peak, masking the depth of the drawdown.

## Dividend yield vs bond yield — the inversion signal

The single most reliable Napier signal: **equity dividend yield exceeding bond yield.**

- 1949: S&P dividend yield 4.0% vs AAA corporate bond yield 2.46% → 150+ bps equity premium. Historic extreme.
- 1932: stocks yielded more than corporate bonds broadly.
- 1921: dividend yields exceeded bonds by widening margin as prices fell.
- 1982: yields extreme after decades of stagflation-driven equity underperformance.

**Why it matters:** when dividend yields exceed bond yields, income-focused institutional capital (insurers, pension funds) has a mechanical reason to rebalance from bonds into equities. This is what turns capitulation into accumulation.

**Signal for today:** watch S&P 500 dividend yield vs 10Y Treasury. Cross-over is rare in the past 30 years and would be a strong contrarian signal.

## Price-to-book and % of stocks below book

- 1932: extreme % of listed stocks below book value.
- 1949: ~225 NYSE names trading below book (roughly 18% of listed universe).
- 1982: enough sub-book names that institutional accumulation could restore valuations only over multiple years.

**Breadth threshold:** when 15%+ of S&P 500 (or comparable universe) trades below book value, the market is in bear-bottom territory.

**Caveat per Damodaran (`valuation/multiples_playbook.md`):** book value is accounting cost, not economic value. For asset-light businesses (software), sub-book is rare and less meaningful. For asset-heavy businesses (banks, industrials), sub-book is a strong signal.

## Volume patterns at bottoms

- Volume **contracts** on the final decline (panic exhausted).
- Volume **expands at higher prices** on the recovery (institutional accumulation).
- Contrast with false bottoms: volume expands on declines, contracts on rallies.

By 1982, NYSE turnover was 42% annually — nearly double early-1950s levels — signaling institutional participation was already high despite depressed prices. The mismatch between rising liquidity and low prices was itself the signal.

## What would invalidate the historical pattern

Napier is explicit that these thresholds held across gold-standard, Bretton Woods, and floating-exchange-rate regimes. What could break them:

1. **Truly unlimited currency debasement without external anchor** — if central banks commit to unlimited fiat printing with no discipline, Q ratio compression to 0.27 might not happen (nominal prices float up, real Q compression is masked).
2. **Institutional ownership collapse** — if passive index ownership falls back toward 1949 single-digit levels, capitulation mechanics shift. Currently institutional ownership is 60%+, similar to Napier's historical baseline.
3. **Structural change in corporate asset composition** — if the market becomes overwhelmingly asset-light (all software/services), replacement cost loses meaning and Q ratio needs redefinition.

None of these apply cleanly in 2026, so the historical thresholds should still be treated as high-signal.

## How to apply in reports

- **Weekly prep** — every week, snapshot: current S&P CAPE, dividend yield vs 10Y, % of names below book. Compare to the four-bottom table.
- **Weekly look-back** — after any material S&P drawdown (>15%), score against the four-bottom levels. If we're within 20% of the historical bottoms on 2+ metrics, elevate the "post-bottom accumulation" pitch archetype.
- **Individual pitch impact** — for pitches on beaten-down blue chips, cross-reference the ticker's own P/B, dividend yield vs bond, and Tobin's Q. A pitch that's "cheap on peer basis" but only 15% below fair Q is different from one at 60% below.
- **Do NOT use these thresholds to override the convergence-signal discipline in `macro/bear_market_patterns.md`.** Valuation alone was never sufficient — Napier's whole point is convergence.
