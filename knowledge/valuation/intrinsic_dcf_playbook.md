---
topic_tags: [valuation, dcf, intrinsic_value, cost_of_capital, terminal_value]
applies_to_reports: [daily_morning, weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Damodaran, The Little Book of Valuation (2024 ed.), Ch 3 'Yes, Virginia, Every Asset Has an Intrinsic Value', pp 41-130"
---

# Intrinsic DCF valuation — the discipline

Intrinsic valuation asks *what a business is worth based on its cash flows, growth, and risk*. Unlike multiples (see `valuation/multiples_playbook.md`), it forces you to state every assumption explicitly. Use it when you want to know the number, not the relative position.

## The choice: FCFE or FCFF

- **FCFE** (Free Cash Flow to Equity) — discount at cost of equity. Values the equity directly.
- **FCFF** (Free Cash Flow to Firm) — discount at cost of capital. Values the whole business; subtract net debt after.

Pick one and stay consistent throughout. Mixing cash-flow and discount-rate definitions is the #1 rookie error.

## The five-step process

1. **Project explicit-period cash flows** (5-10 years). Cash flow = after-tax operating income − reinvestment − change in working capital.
2. **Estimate terminal value** using perpetuity: `TV = CF_{n+1} / (r − g)`. Terminal growth `g` MUST be ≤ long-term nominal GDP growth (~2.5-3% for the US).
3. **Discount** cash flows + TV to present at the appropriate risk-adjusted rate.
4. **Adjust** for cash, debt, minority interests, options.
5. **Per-share value** = adjusted equity value / diluted shares.

## Estimating the key inputs

### Cost of equity
`Ke = Rf + β × ERP`. As of 2023: Rf ≈ 3.8%, ERP ≈ 5-6%, so typical Ke lands in 8-11% depending on beta.

- Prefer **sector-average beta** adjusted for the company's financial leverage over raw regression betas from noisy historicals.
- ERP is **forward-looking**. Use the current implied ERP (Damodaran publishes this monthly), not the 1928-present average.

### Cost of capital
`WACC = (E/V) × Ke + (D/V) × Kd × (1−t)`. Use **market weights** for equity and debt, not book weights.

### Growth rate — the most abused input
Historical growth is a **poor predictor** — high-growth firms mature fast. Analyst forecasts carry bias. Instead:

- **Sustainable growth = Reinvestment rate × ROIC** (or ROE for equity).
- If ROIC ≈ cost of capital, terminal growth should equal nominal GDP growth.
- If ROIC > cost of capital, excess returns justify slightly higher terminal growth — but competitive advantages don't last forever; model them fading.
- For the near-term high-growth window (say 5 years), forecast explicitly based on TAM + market share + competitive position, then converge to stable growth.

### Reinvestment rate
`(Capex − Depreciation + ΔWC) / after-tax operating income`. Tie this to the revenue growth you're forecasting. If you're forecasting 5% growth with 15% margins but the company's sales-to-capital ratio is 1.5, reinvestment must be about 3.3% of operating income — not 0.5%.

## Terminal value discipline

The TV is often 40-70% of total value. Sanity-check every terminal:

- Is terminal growth ≤ nominal GDP growth?
- Given the terminal growth `g` and terminal ROIC, is required reinvestment `g/ROIC` ≤ 100% of operating income? If not, growth is unsustainable.
- Does terminal margin match a mature-industry margin, not a peak-cycle margin?

## Common wrongness (Damodaran's three cardinal sins)

1. **Stale or wrong risk measures** — raw historical betas, book-weight WACC, out-of-date ERP.
2. **Terminal fantasy** — 3% terminal growth + 2% reinvestment + 8% ROIC. The math doesn't work. Reinvestment must fund growth.
3. **Capex-growth mismatch** — assuming margins expand while reinvestment stays flat. Growth costs money; forecast the money.

Bonus: **confusing volatility with risk**. Backward-looking vol premiums for a company whose risk profile has changed.

## When intrinsic beats multiples

Reach for DCF (don't just default to multiples) when any of these hold:

- **No clean comparables** — young firms, unique business models, distressed firms, cyclicals mid-cycle.
- **Large gap between multiple-implied and fundamental value** — the KHC 2023 example: $36 market price vs $20.60 intrinsic. Multiples hid the overvaluation.
- **Decisions need the real number** — buybacks, M&A, strategic reviews. "How does this compare to peers" is not enough.

## How to apply in a pitch

- If your pitch thesis is *"the market is missing X"*, DCF the company under your assumptions vs. the market's implied assumptions. Quantify the gap.
- Never hand-wave "trades at 15× when peers trade at 20×" without asking whether peer earnings are sustainable.
- If terminal value is >70% of your intrinsic, your assumptions are load-bearing and should be defended in the thesis.
- Sanity: implied `g/ROIC` reinvestment must ≤ 100%; ERP within current published range; beta within sector band.

Reject pitches where the analyst refuses to write down the DCF because "the multiple tells the whole story." Multiples embed assumptions; DCF exposes them.
