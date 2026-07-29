---
topic_tags: [correlations, rates, growth_stocks, duration]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-07-29
provenance: "curated 2026-07-29 from established rates-equity literature (Damodaran on duration, discount rate mechanics) + 2022-2024 tightening-cycle observed data"
---

# 10-year yield vs growth-stock multiples

## Core rule
Rising 10-year yields compress multiples on long-duration cash flows. Growth stocks — whose value sits mostly in distant future cash flows — are mechanically more sensitive than value stocks. This is math, not sentiment.

## Base rates
- The 10Y yield's rate of change (weekly delta) predicts growth-vs-value relative performance ~60-70% of the time in trending rate regimes.
- Nasdaq / S&P ratio inversely correlates with 10Y yield on multi-month horizons.
- P/E multiple compression per +1% in 10Y yield: rough rule ~1-2 P/E points for high-multiple growth (P/E >30); modest for value (P/E <15).
- Long-duration tech (unprofitable growth, SaaS, biotech) has 2-3× the multiple sensitivity of mature megacap tech (AAPL, MSFT) — profitability shortens effective duration.
- Real yields (10Y TIPS) matter more than nominal — a nominal-yield rise driven purely by inflation expectations hurts growth less than a real-yield rise.

## Rate sensitivity by sector
- Most sensitive to rising rates (long duration, no near-term earnings): unprofitable growth, high-multiple SaaS, biotech, REITs (yield-substitute compression), utilities (yield-substitute compression).
- Moderately sensitive: high-multiple megacap tech (MSFT, AAPL, GOOGL), consumer discretionary.
- Positively correlated with rising rates: financials (NIM expansion), insurers.
- Weakly sensitive: energy (commodity-price-driven), staples, healthcare (idiosyncratic drivers).

## When it works
- Directional, sustained rate moves — a 100bp move over 6 months shows the mechanical relationship clearly.
- Real yield moves — the cleanest signal for growth-multiple compression.
- Combined with credit spreads — rising rates + widening credit spreads = double hit on growth.
- Earnings-season windows where rate-sensitivity gets tested against actual results.

## When it fails
- Rate moves driven by growth surprise (positive real growth) — growth stocks can rally into higher rates when the reason is a strong economy.
- Idiosyncratic name moves — an AI-narrative rally can override rate headwinds.
- Very low absolute rate levels — when 10Y goes from 1.5% to 2%, mechanical impact is small; from 3% to 4.5%, it's material.
- Panic-driven rate spikes — flight-to-quality bid can suppress the equity-rates linkage temporarily.

## Application
- Growth-stock long pitches must reference current 10Y yield direction; long unprofitable growth with 10Y rising deserves `low_star_warning`.
- Rubric use: `macro_alignment` for high-multiple tech longs requires 10Y not-rising trend; violation = point off.
- Duration awareness in thesis: for any growth pitch, note whether it's early-stage (long duration, high sensitivity) or mature-profitable (shorter duration, lower sensitivity).
- Sector pair-trade angle in weekly prep: rate direction defines which side of the growth/value pair to lean.
