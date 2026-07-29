---
topic_tags: [sector, financials, banks, insurance, asset_managers]
applies_to_reports: [daily_morning, weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Damodaran, The Little Book of Valuation (2024 ed.), Ch 10 'Bank on It' pp 275-300; sector convention notes"
---

# Financials sector — regime, valuation, and common errors

Financials (banks, insurers, asset managers) break every "normal" valuation approach because their **liabilities are raw material, not debt**. Deposits at banks and premium float at insurers are how the business is funded AND what the business does. You cannot cleanly separate operating from financing activity, which is why EV/EBITDA, EV/Sales, and enterprise-value multiples are meaningless here.

Value equity directly. Use dividends (DDM), FCFE-with-regulatory-capital, or the excess-return model.

## The ROE-vs-cost-of-equity anchor

The single most important number for any bank pitch:

- **If ROE > cost of equity** → price should trade above book (P/B > 1). Growth creates value.
- **If ROE = cost of equity** → price should trade at book (P/B ≈ 1). Growth is neutral.
- **If ROE < cost of equity** → price should trade below book (P/B < 1). Growth destroys value.

A bank at 0.5× P/B with 8% ROE and 12% cost of equity is not cheap — it's correctly discounting perpetual value destruction. A bank at 1.5× P/B with 14% ROE and 10% cost of equity is not expensive — it's fairly valuing durable excess returns.

Reference (May 2023, per Damodaran): JPMorgan 1.53× P/B (14.5% ROE), Citigroup 0.50× P/B (8.8% ROE), large-bank median 1.04× (12% ROE). The dispersion IS the ROE gap, not a mispricing.

## Regime drivers

- **Yield-curve shape** — steepening usually helps NIM (banks borrow short, lend long) but the effect is uneven. Regionals with sticky deposits benefit more than big-banks funded by expensive institutional money.
- **Deposit beta** — how much of a Fed hike passes through to deposit rates. Low deposit beta = margin expansion; high beta = compression.
- **Credit cycle** — loan-loss provisions are pro-cyclical (low in expansions, spike in contractions). Normalize across cycles; don't extrapolate current provisioning as terminal.
- **Regulatory capital regime** — post-2023 SVB failure, regulators raised expected Tier 1 targets industry-wide, which lowered ceiling growth and dividends across the sector.

## Big-bank vs regional split

- **Big banks** (JPM, BAC, C, WFC, GS, MS) — diversified: NIM + capital-markets fees + wealth + trading. Less sensitive to any single line but higher regulatory scrutiny (G-SIB surcharges).
- **Regionals** — NIM-dominant, deposit-franchise-dominant, geographically concentrated. Higher torque to yield curve; higher tail risk on deposit flight (SVB precedent).
- **Payments and card networks** (MA, V, AXP) — behave like consumer-transaction growth stocks, not banks. Different valuation approach (use lifecycle/growth methodology, not DDM).
- **Asset managers** (BLK) — AUM × fee rate business; fees are pro-cyclical with markets. Not really a bank; more like a mature asset-light growth company.
- **Insurers** (PGR, CB, AON, MMC, MET-equiv) — combined ratio is the key metric (<100 = underwriting profit); float is invested and drives investment income.

## Valuation approach — decision tree

- **Traditional bank (deposits + loans + credit)** → DDM as primary; FCFE-with-Tier-1-capital-investment as sanity check.
- **Growth-stage payments / fintech (MA, V, AXP)** → growth-company DCF (see `valuation/lifecycle_valuation.md`). NOT DDM.
- **Insurer** → excess-return model on underwriting + investment income separately. Combined ratio drives underwriting value; float × investment yield drives investment value.
- **Asset manager** → DCF on fee income; mature-company approach with heavy attention to fee compression (passive vs active mix).

## Key inputs to specify in any bank pitch

- **Cost of equity** — use sector beta (not single-firm regression noise), current risk-free + ERP.
- **ROE trend** — trailing 5-year average, current, and what your thesis assumes forward.
- **Tier 1 capital ratio** — vs regulatory minimum AND vs peer target (competitors targeting 15-16% force the same on you).
- **NIM assumption** — current is likely elevated (post-2023 rate hikes). Terminal NIM should revert toward long-run history.
- **Payout ratio** — dividend + buyback / net income, smoothed over 3 years.

## Common wrongness

- **Treating book value as intrinsic value.** Book is accounting cost, not economic value. A bank earning below cost of equity should trade below book — no arbitrage.
- **NIM extrapolation.** 2023-2024 NIMs are cycle-high. Assuming current NIMs into perpetuity assumes rates stay elevated forever.
- **Ignoring off-balance-sheet risk.** Securitized assets, derivatives, and shadow-bank subsidiaries don't show up as deposits but amplify tail risk. Look at risk-weighted assets, not just total assets.
- **"Steepening = good for all banks"** — only partially true. Short-end funding cost matters; a bank paying institutional-money rates on the short end doesn't benefit as much from the long end rising.
- **Cross-comparing US and non-US banks on P/B.** Regulatory regimes and accounting differ enough (goodwill treatment, capital deduction rules) to make cross-border P/B comparison misleading.
- **Payments and card networks valued as banks.** MA/V/AXP have bank-adjacent names but they're growth companies. Don't apply DDM.

## How to apply in a pitch

- Open with the ROE-vs-cost-of-equity gap. That's the whole story for any bank.
- If your thesis is "cheap at 0.5× book" the follow-through MUST be "and here's the ROE recovery path" or "and here's the cost-of-equity contraction path." Otherwise it's a value trap.
- For NIM-based bull cases, state whether you're assuming rates hold or fall, and what NIM the current price implies.
- For payments / asset managers, do NOT use bank rubric factors. Use growth-company lifecycle rubric.
- Weekly look-back: when a bank thesis played out, was it ROE expansion, cost-of-equity contraction, or NIM tailwind? Different answers, different lessons.
