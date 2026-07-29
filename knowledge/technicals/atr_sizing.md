---
topic_tags: [technicals, atr, position_sizing, stops]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-07-29
provenance: "curated 2026-07-29 from established technical analysis literature (Wilder, van Tharp) + market microstructure practice"
---

# ATR-based stops and TP placement

## Core rule
Position stops and targets as multiples of Average True Range (ATR-14), not as arbitrary price distances. ATR encodes recent volatility, so a "2× ATR stop" scales automatically to the instrument's current tape.

## Base rates
- ATR(14) is the workhorse — 14-period smoothing balances responsiveness with noise rejection.
- Swing-trade stops typically sit at 1.5-2.5× ATR from entry; too tight = noise-out, too wide = poor R.
- Trend-trade TPs typically sit at 2.5-4× ATR (or wider trailing) — capturing the fat tail is the whole edge.
- Intraday trades compress to 0.5-1× ATR stops but require correspondingly tighter TPs.
- Arbitrary "round-number" stops (e.g., "$5 below entry") get stopped out ~20-40% more often than ATR-scaled stops on identical setups in backtests.

## When it works
- Trending markets with orderly volatility (VIX 12-20 regime for equities).
- Instruments with liquid tape and continuous quotes — commodities, blue-chip equities, top-cap crypto.
- Multi-day swing horizons where 1-2 daily bars of noise are expected.
- After ATR has stabilized (>10 bars of data since a regime shift).

## When it fails
- Immediately after a volatility regime shift — ATR is a lagging measure; use rolling shorter-window ATR or widen multipliers post-event.
- Around scheduled catalysts (earnings, CPI, FOMC) — ATR understates realized event vol by 2-5×.
- In illiquid crypto or small-cap tape where a single print can spike ATR artificially.
- Gap-prone assets — an overnight gap can blow through a 2× ATR stop without a fill.

## Application
- Commodity trades (gold, oil): 1.5-2× ATR stop, 3× ATR TP is a defensible baseline.
- Blue-chip equity trades: 1.5-2× ATR stop, 2.5-3× ATR TP; widen stop to 2.5× ATR if pitched around earnings within the horizon.
- Crypto trades: 2-3× ATR stop (higher noise floor), 3-5× ATR TP; never tighter than 2× ATR.
- Every trade thesis must justify stop placement against a real level (S/R, prior swing) AND the ATR multiplier — both, not either.
