---
topic_tags: [correlations, vix, volatility, regime]
applies_to_reports: [weekly_prep]
last_reviewed: 2026-07-29
provenance: "curated 2026-07-29 from established volatility literature (Cboe VIX methodology, Sinclair Volatility Trading) + term-structure practice"
---

# Volatility regimes: VIX and term structure

## Core rule
VIX level defines the market's implied-vol regime; VIX term structure (contango vs backwardation) tells you whether the market thinks the current vol level will persist. Trade tactics change materially by regime — the same setup has different edge in VIX 12 vs VIX 30.

## Base rates
- VIX <15: complacent regime. Trend-following works; mean-reversion selling of overbought conditions is a trap.
- VIX 15-20: normal regime. Both trend and mean-reversion setups viable; sector rotation is cleanest.
- VIX 20-30: elevated regime. Ranges widen; SL distances need to expand proportionally; correlation across assets rises.
- VIX >30: crisis regime. All correlations approach 1 (everything sells together); mean-reversion trades have highest expected value but hardest to hold.
- VIX >40: extreme fear. Historically these prints resolve upward in equities over 3-6 months ~70-80% of the time; hard to time exact bottom.

## Term structure
- Contango (front-month < 3-month): normal — market prices vol to rise later; consistent with risk-on.
- Backwardation (front-month > 3-month): stress — market prices near-term vol above forward; classic risk-off tell.
- Persistent backwardation (>5 sessions) has historically preceded further downside 60-70% of the time.
- VVIX (vol-of-vol): >120 signals fragility even when VIX itself is contained.

## When it works
- Regime-appropriate tactics — trend-following in low-VIX regimes, mean-reversion in high-VIX regimes.
- VIX spikes accompanied by term-structure inversion — high-conviction risk-off signal.
- Combined with cross-asset confirmation (VIX up + DXY up + Treasuries up + equities down = coherent risk-off).
- Multi-day VIX moves (>15% over 2-3 sessions) are meaningful; single-day spikes often noise.

## When it fails
- VIX manipulation around expiry (monthly VIX settlement) can produce misleading prints.
- VVIX complacency during grinding rallies — vol can compress artificially before regime shifts.
- Idiosyncratic single-name events don't move VIX materially — a stock-specific short thesis doesn't need VIX support.
- Post-crisis "vol crush" periods where VIX overshoots to the downside on the recovery.

## Application
- Rubric use: `macro_alignment` for equity longs needs VIX <25 confirmation; longs in VIX >30 need explicit reason.
- SL sizing: multiply ATR-based SL by 1.3-1.5× in VIX >25 regimes to survive noise.
- Warning trigger: any long pitch with VIX rising through 20 AND term structure flattening needs a mention.
- Weekly prep: current VIX level and 20-day change belong in "macro setup going in."
