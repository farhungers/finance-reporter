---
topic_tags: [valuation, multiples, pe_ratio, ev_ebitda, pbv, ps_ratio, relative_value]
applies_to_reports: [daily_morning, weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Damodaran, The Little Book of Valuation (2024 ed.), Ch 4 'It's All Relative!', pp 130-165 (approx)"
---

# Multiples — how to use them without getting fooled

Multiples answer *"what would the market pay for this asset given what it pays for similar assets?"* — a pricing question, not a value question. Use them when comparables are clean and the market is largely right on the peer group. Verify against DCF (`valuation/intrinsic_dcf_playbook.md`) when either assumption is shaky.

## The four keys (Damodaran's framework)

Every multiple must clear all four gates or the comparison is noise.

1. **Consistent definition** — same numerator and denominator scaling. PE compares equity price to per-share earnings; EV/EBITDA compares whole-business value to whole-business earnings before capital-structure choices. Don't mix (e.g., dividing market cap by EBITDA is a category error).

2. **Consistent timing** — trailing, current, or forward. Pick one and hold it across the entire peer group. Mixing trailing PE for one firm with forward PE for another destroys the comparison.

3. **Comparable peer group** — same industry AND similar size, growth, risk. "Same GICS code" is a starting filter, not an ending one. A 30%-growth SaaS shop and a 3%-growth legacy software vendor share a code but not a peer group.

4. **Adjust for real differences** — if two "comparables" differ on growth, margin, or risk, use PEG, regression, or explicit adjustment. Never assume the median peer multiple is the right multiple.

## The main multiples

| Multiple | Drivers (↑ raises it) | Distorted by | Fails for |
|---|---|---|---|
| **PE** | Expected growth, payout ratio; risk lowers it | Negative earnings, depreciation policy, cyclical earnings | Unprofitable firms, distressed firms |
| **PBV** | ROE, growth; risk lowers it | Accounting for intangibles, buybacks reducing book | Asset-light businesses (software) |
| **PS** | Net margin, growth; reinvestment lowers it | (Least distorted — revenue is hardest to game) | Doesn't reflect profitability |
| **EV/EBITDA** | Growth; cost of capital and reinvestment lower it | Depreciation policy differences, asset intensity gaps | Financial firms (EBITDA meaningless) |

## Distribution anchors — US stocks January 2023 (Table 4.1)

These distributions are **heavily right-skewed**. Means are misleading; **use medians as anchors**.

| Multiple | Median | Mean | Skewness |
|---|---|---|---|
| PE | 13.92 | 109.25 | 37.69 |
| PBV | 1.59 | 12.40 | 26.22 |
| EV/EBITDA | 13.30 | 323.31 | 34.25 |
| EV/Sales | 2.70 | 89.04 | 31.13 |

Only ~43% of US firms had a computable PE in Jan 2023 — the rest reported losses. When someone says "the market trades at X" always ask: median or mean, and which slice.

## Historical PE regime (Table 4.2, 2004-2023)

Median PE by year ranged from **9.80 (2009 crisis low)** to **23.21 (2005)**. In 2023 median was 13.92.

- "Expensive" regime: PE 20-23 during stable, low-rate years.
- "Cheap" regime: PE 9-16 during recessions or crisis lows.

The distribution *itself shifts* with rates and risk appetite. Don't call today expensive by comparing to a 2005 median.

## Six common mismatches (Table 4.4) — the setup patterns that flag mispricing

Low multiple + strong companion variable = undervalued signal. High multiple + weak companion = overvalued signal.

| Signal (LOW multiple + HIGH companion) | Interpretation |
|---|---|
| Low PE + high expected growth | Cheap growth |
| Low PBV + high ROE | Cheap quality — market underpricing capital efficiency |
| Low PS + high net margin | Cheap profitability |
| Low EV/EBITDA + low reinvestment need | Cheap cash flow |
| Low EV/Capital + high ROC | Cheap value creation |
| Low EV/Sales + high operating margin | Cheap operating quality |

Always identify the *companion variable* before calling anything cheap or expensive. A low PE with declining growth is not cheap — it's correctly priced for decay.

## Intrinsic vs pricing — pick your posture

**Intrinsic** assumes markets eventually correct mistakes. **Relative** assumes markets are efficient on average and you're exploiting temporary local mispricings against peers.

Both can be right; they can also disagree. In 2000, Amazon was overvalued intrinsically but undervalued relative to other internet stocks (which were even more insane). Neither posture wins in every regime — but be **explicit about which posture your pitch is taking**.

## How to apply in a pitch

- State the multiple, the peer group, the timing (trailing/forward), and the companion variable justifying the cheap/expensive call.
- If your comp list has >5x range in multiples, the peer group is wrong. Narrow it.
- If your pitch is "trades at 15× vs peers at 20×", explicitly ask: are peer earnings sustainable? Is our earnings quality the same?
- Reference the median historical multiple for the industry, not just current peers — regime matters.
- Never lead a pitch with a mismatch pattern (low PE + high growth) without ruling out the obvious alternative — that consensus already sees the deceleration coming.
