---
topic_tags: [sector, energy, oil, gas, cyclicals, commodities]
applies_to_reports: [weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Damodaran, The Little Book of Valuation (2024 ed.), Ch 11 'Roller Coaster Investing' (Shell case) pp 300-325; sector convention notes"
---

# Energy sector — regime, cyclical valuation, and common errors

Energy is the archetypal **cyclical + commodity** sector. Value moves as a near-linear function of the underlying commodity price (oil, gas, refined products). Trailing PE and current-year margins are systematically misleading. Every energy pitch must run through **normalized-earnings** discipline.

## The normalization requirement

Trailing PE at cycle peak looks CHEAP (earnings are peak, price hasn't caught up). Trailing PE at cycle trough looks EXPENSIVE (earnings are depressed). Both signals lie.

Three normalization techniques (Damodaran):

1. **Simple time-average earnings** — average across a full cycle (5-10 years). Best when the business hasn't structurally changed.
2. **Scaled margin average** — average operating margin over the cycle, applied to current revenues. Adjusts for scale changes; typically the right choice for large integrated names.
3. **Sector-average margins** — when firm history is thin or unrepresentative, use peer-group averages.

For pitches, always state: (a) the historical margin used, (b) the commodity price assumption, and (c) how sensitive per-share value is to a ±20% commodity move.

## The commodity-price coupling

Value scales with the underlying commodity. Damodaran's Shell 2023 regression: revenue ≈ $4,172 × oil price + $27.8B base. Per-share value:

- $30/bbl oil → ~$30/share
- $80/bbl oil (Aug 2023) → ~$75/share
- $100/bbl → ~$90/share
- $150/bbl → ~$130/share

Roughly linear with slight convexity at high prices. Hedging flattens it; production growth steepens it.

**Direction of pitch depends on the commodity view first, the company second.** No amount of company-specific analysis salvages a long oil-major pitch if your commodity view is falling.

## The real-option value of undeveloped reserves

Undeveloped reserves are **out-of-the-money call options on the commodity**:

- Higher commodity-price **volatility** raises option value (independent of level).
- Firms with large undeveloped resource bases (some E&Ps, deep-water explorers) get non-linear upside in volatile regimes; integrated majors with mostly-developed reserves get linear exposure.
- When prices are low but volatile, undeveloped reserves are near-the-money and highly valuable — a bear case for the commodity is not necessarily a bear case for the equity if optionality is large.
- Standard DCF using a single normalized commodity price systematically undervalues optionality-heavy names in volatile regimes.

## Regime drivers

- **WTI vs Brent spread** — narrow spread = US export arbitrage closed. Wide spread = US refiners benefit; producers less so.
- **OPEC+ discipline** — production cuts support price; cheating (or Saudi price war) crushes it. Watch member-country fiscal breakevens (Saudi ~$85, Russia ~$70, Iran higher).
- **EIA weekly inventory cadence** — Wed 15:30 UTC (10:30 ET) release. Draw > forecast = bullish; build > forecast = bearish. Front-of-curve is most sensitive.
- **Refining crack spreads** — 3-2-1 crack for gasoline/diesel margin. Widening = refiner margin tailwind (VLO, MPC, PSX equivalents); narrowing = headwind.
- **Nat gas** — seasonal (heating demand winter, cooling summer, injection shoulders spring/fall). Storage cadence Thu 15:30 UTC. Much more localized than oil (US vs Europe vs Asia are distinct markets).

## Base-rate patterns

- **Inflationary regimes** — energy tends to outperform SPX (real-asset hedge). Not automatic; only when inflation is *commodity-driven*, not services-driven.
- **XLE beta to WTI** — historically ~0.4-0.6. Higher when curve is in backwardation (spot > forward). Lower when producers hedge aggressively.
- **Post-drawdown recovery** — E&Ps outperform integrated majors during recovery (higher torque). Integrated majors outperform on the way down (diversification + refining + trading offset upstream).

## Valuation approach — decision tree

- **Integrated major** (XOM, CVX, RDS-eq) → normalized-earnings DCF at cycle-average margin + oil-price assumption. Cross-check with EV/EBITDA and EV/Proven Reserves against peer table.
- **Pure E&P upstream** → focus on production per share, F&D cost, reserve replacement. Real-option value is significant when prices are volatile. Watch balance-sheet dispersion (debt load determines survival in downturn).
- **Midstream / MLPs** → toll-road model; DCF on fee-based cash flows. Less commodity-price sensitive.
- **Refiners** (VLO, MPC, PSX) → crack-spread-driven. Valuation on mid-cycle crack + throughput.
- **Oil-services** (SLB, HAL) → highly cyclical; capex-cycle-driven (E&P capex → services revenue). Longer cycle lag than upstream.

## Common wrongness

- **Peak-cycle margins as terminal.** Applying 15-20% operating margins from the peak into perpetuity produces fantasy valuations. Cycle-average is 8-12% for integrated majors.
- **"Cheap at 6× PE" at cycle top.** Trailing PE is at cycle-peak earnings. Forward PE on normalized earnings is often 12-15× — fair or expensive.
- **Ignoring capex cyclicality.** E&Ps over-invest at peaks (locking in high F&D costs), under-invest at troughs. Model 5-year forward capex as % of cash flow, not current-year rate.
- **Stock volatility ≠ business risk.** Cyclical stocks are volatile because earnings are volatile. A stable 8% return on normalized capital can generate 30-40% annualized stock vol without fundamentally elevated risk.
- **Trading E&P as pure oil beta.** Balance-sheet dispersion matters enormously. Two E&Ps with identical production can have 5× different equity values based on debt load.
- **Nat-gas majors valued off oil-price WTI regression.** Nat gas trades separately (Henry Hub); use the right commodity for the price coupling.

## How to apply in a pitch

1. **State the commodity price assumption first.** "Long XOM assumes WTI stays >$70 through Q1." Without this, the pitch is empty.
2. **Use normalized margins.** Not trailing. Cite the historical range.
3. **For E&Ps, name the balance-sheet position.** Debt/EBITDA at normalized commodity price. Survival matters more than upside for the bear-case downside scenario.
4. **For commodity trades (gold, oil, silver, copper, nat gas) separately** — the trade is on the commodity directly, not the equity. Different rubric weights: `macro_alignment` becomes dominant; `catalyst_proximity` shifts to inventory-report / OPEC-meeting cadences.
5. **Weekly look-back on energy** — when a pitch played out, was it the commodity move OR the company-specific alpha? Different attribution.
