---
topic_tags: [macro, regime, cycle_position, marks]
applies_to_reports: [daily_morning, daily_wrap, weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Marks, Mastering the Market Cycle (2018), Chs on Why Study Cycles / Nature / Regularity / Economic Cycle / Government / Profits, pp 20-100 (approx)"
---

# Regime reads — where in the cycle, and what to do about it

Marks' central claim: you can't predict *when* the cycle turns, but you can read *approximately where you are*. That's enough. Cycle position should shift portfolio posture between aggressive and defensive — the single biggest lever, larger than security selection.

## Why cycle position matters more than macro forecast

- **Asymmetric payoff.** Overpaying at peaks destroys capital via double-compression (multiple + earnings both fall). Underpaying at troughs compounds via double-expansion (multiple + earnings both rise).
- **You don't need to forecast; you need to observe.** Signal comes from *current conditions*, not predictions of turning points. Most forecasts extrapolate recent trends — they add no edge because they're already priced in.
- **Cycles rhyme, they don't repeat.** Direction and causation are regular; timing, duration, and magnitude are not. Recognize *themes* (euphoria/depression, tightening/easing) not identical patterns.

## The three cycle drivers that never go away

1. **Human psychology** — greed and fear are structural, not temporary.
2. **Credit availability** — see `macro/credit_cycle_playbook.md`.
3. **Government intervention** — dampens some cycles, amplifies others; never abolishes them.

## The economic cycle — what actually swings

Long-run GDP growth (~2-3% US) is set by population + productivity, both slow. Short-run swings around trend come from:

- **Consumption** — mood-driven (wealth effect, confidence), credit-dependent.
- **Business investment** — highly cyclical; over-builds in booms, cuts hard in busts. Bigger amplifier than consumption.
- **Government spending** — attempts counter-cyclicality but usually lags, adding volatility rather than dampening it.
- **Inventory** — over-produced in booms, dumped in busts; amplifies both directions.

Recession = two negative GDP quarters, but that's just the tail of a distribution that normally runs -2% to +5% annually. Most cycles you'll trade never hit technical recession.

## The profit cycle — swings much harder than GDP

Corporate profits amplify GDP moves via two levers:

- **Operating leverage** — fixed costs don't shrink when revenue does. 20% revenue drop can halve profits.
- **Financial leverage** — debt service is fixed. Debt magnifies profits on the way up, destroys them on the way down.

**Practical implication for pitches:** GDP swings ±2-3%; corporate profits swing ±20-30%. A stock at a "cheap" trailing PE is often at peak-cycle earnings that are about to compress. Always ask: is this multiple cheap because it's cheap, or cheap because next year's earnings are half of this year's?

## What to actually watch (cluster of signals, not any single one)

**Investor psychology:**
- Greed vs fear dominance in commentary/positioning
- Willingness to fund weak business models
- IPO volume + first-day pop magnitude
- Willingness to pay for narrative vs cash flow

**Capital availability:**
- HY credit spreads (compression = late; blowout = trough)
- Lending standards (loose = late; tight = trough)
- Covenant-lite share of new issuance
- Default rates + delinquencies

**Valuation vs history:**
- Multiples vs 10-yr distribution (median, not mean — see `valuation/multiples_playbook.md`)
- Cross-asset: earnings yield vs 10Y real
- Sector dispersion — high dispersion = late cycle; low = early

**Profit cycle:**
- Margins vs decade high/low
- Inventory/sales ratio (rising = late cycle warning)
- Capex plans (aggressive = late; cautious = early)

**Policy stance:**
- Rate direction + curve shape
- Fiscal deficit trajectory
- Balance-sheet expansion/contraction

## The cluster rule

No single indicator is definitive. Look for **clustering**:

- Greed + tight credit + peak margins + aggressive capex + tightening policy = **late cycle, defensive posture**
- Fear + wide credit + trough margins + capex cuts + easing policy = **early cycle, aggressive posture**
- Mixed signals = midcycle, normal discipline

## Common wrongness

- **Extrapolating current conditions** — assuming quiet vol persists forever; assuming tight spreads are the new normal; assuming Fed can always suppress crises. Cycles recur.
- **Waiting for perfect confirmation** — by the time all signals align, you're too late. Act on clustered directional evidence.
- **Being right at the wrong time** — cycles can extend beyond your capital or patience. Position size in cycle-early calls should acknowledge this.
- **Assuming this cycle looks like the last one.** Same themes, new details.

## How to apply in reports

- **Daily morning** — pitches should reference current cycle read implicitly (e.g., defensive pitches when late-cycle signals cluster).
- **Weekly prep** — explicitly state current cycle read + which signals are shifting. This is the file the LLM should cite by source_id when framing the week.
- **Weekly look-back** — post-mortem on cycle read: did the signals we identified play out? Update the cluster interpretation over time.
- **Daily wrap** — flag any single-day shift in cluster (e.g., credit spread blowout, IPO pulled) as a potential cycle-position-change signal.
