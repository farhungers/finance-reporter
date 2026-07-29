---
topic_tags: [macro, credit, credit_cycle, hy_spreads, marks]
applies_to_reports: [weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Marks, Mastering the Market Cycle (2018), 'The Credit Cycle' + 'The Distressed Debt Cycle' chapters, pp 160-220 (approx)"
---

# Credit cycle playbook

Credit is Marks' area of deepest expertise, and his single highest-signal claim: **credit leads equity by weeks to quarters**. When credit tightens, equity multiples compress with a lag. A pitch bot that watches credit alongside fundamentals will be ahead of one that watches only PE ratios and earnings.

## The self-reinforcing loop (Marks' credit cycle mechanism)

1. Prosperity → risk appetite rises → HY spreads compress
2. Compressed spreads → lenders compete for volume → standards loosen
3. Loose standards → weak issuers access market (CCCs, cov-lite, PIK toggles) → leverage climbs
4. Extrapolation: "the credit window will always be open" → excess builds
5. Trigger event (default, rate spike, macro shock) → risk aversion returns
6. Spreads widen → refinancing dries up → forced sellers appear
7. Real economy hurt (capex cut, hiring frozen) → earnings decline
8. Equity multiples de-rate with a lag → cycle troughs
9. Wide spreads + pessimism + policy easing → seeds of the next expansion

Note the **lag**: credit contracts in weeks; equity re-rates over months. That gap is where the signal lives.

## Indicators by phase

### Late-cycle / peak (spreads compressed, complacency)
- HY spreads at cycle lows (historically ~250-350 bps for US HY)
- Covenant-lite share of new HY issuance >70%
- B and CCC rated debt volumes surge
- PIK toggles common
- LBO leverage >6× EBITDA
- IPO first-day pops routinely >30%
- Distressed debt trading at low discounts to par

### Contraction (spreads widening, refinancing shut)
- HY spreads widen 200+ bps in weeks
- Issuance volume drops sharply
- IG-HY differential widens (risk premium re-pricing)
- Default rates rise from near-zero
- Distressed debt bid-ask widens; trading volume spikes

### Trough (fear + forced selling)
- HY spreads at cycle highs (800-2000+ bps in crises)
- No new issuance except top-quality IG
- Distressed debt trading 30-50% below par
- Covenants tight; lenders demand maximum protection
- Media unanimity on doom

## Why credit leads equity

Credit provides the funding that supports equity valuations — buybacks, M&A, dividend growth, capex. When credit tightens:
- Buybacks slow (multiple compression)
- M&A dries up (premium arbitrage vanishes)
- Marginal borrowers face refinancing walls (default risk)
- Capex is cut (growth expectations reset lower)

**Equity holders live in denial longer than lenders.** Lenders face real losses on default; equity gets the residual. When equity and credit diverge, credit is right.

## The Fed put — how it distorts the natural cycle

Post-GFC policy has changed the credit-cycle dynamics:
- QE and rate suppression compress spreads artificially, extending the late-cycle phase
- Marginal borrowers survive longer than they otherwise would
- Investors under-price tail risk assuming the Fed will cut on stress
- When correction finally comes, it's sharper (bigger imbalances)

**For a 2026 bot:** don't assume Fed rescue. It happens, but not always in time and not always without collateral damage (SVB 2023 was a real example).

## Using credit signals in an equity pitch

| Credit signal | Equity implication | Timing |
|---|---|---|
| HY spreads widening 50+ bps over 4 weeks | Multiple compression coming; defensive tilt | 6-12 weeks lead |
| IPO market shutting (issuers pulling deals) | Peak multiples; supply/demand tips bearish | 3-6 months lead |
| Distressed volume spiking | Forced selling in credit → cross-asset contagion | 4-8 weeks lead |
| IG-HY differential narrowing to cycle lows | Peak complacency; asymmetry vs downside | 12-24 months lead but very late-cycle |
| Cov-lite share >70% of new HY | Late-cycle euphoria confirmed | Late but still actionable |

## Common wrongness

- **"The Fed will always suppress spreads."** Marks: spreads reflect market psychology; policy can nudge, not dictate. See 2022 (Fed hiking + HY blowout to 550 bps).
- **"Current tight spreads = the new normal."** Cycles are persistent, not permanent. Ban the words "always/never/forever/can't" from cycle analysis.
- **Ignoring cross-market divergence.** Equity rallies while credit widens → credit is right, equity is late. Trade against the equity rally.
- **Historical spread ranges = fair value anchors.** They're not. Spreads compress to lower lows in euphoria and widen to higher highs in crises than any historical range would suggest.
- **Confusing correlation with causation.** Credit and equity move together, but credit turns first. Wait for equity to confirm and you've missed the move.

## How to apply in reports

- **Daily morning** — if the HY spread has moved materially (>25 bps) in the past week, flag it in the calendar/macro read and adjust pitch tilt (defensive if widening, aggressive if compressing from wide levels).
- **Weekly prep** — state the current HY spread level, its 12-month change, and what phase of the credit cycle it implies.
- **Weekly look-back** — when a pitch played out (or failed), was credit condition the leading factor? If yes, upgrade the credit-signal-weight in the rubric interpretation.
- **Trade generation** — for equity trades in cyclical sectors, credit-cycle position is a hard filter: late-cycle + tight spreads = penalize cyclical longs.
