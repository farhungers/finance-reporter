---
topic_tags: [correlations, commodities, dxy, dollar]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-07-29
provenance: "curated 2026-07-29 from established commodity-macro literature (Roubini, Rogers) + FX-commodity correlation practice"
---

# Commodities and DXY

## Core rule
The US Dollar Index inversely correlates with USD-priced commodities — a weaker DXY makes commodities cheaper for non-USD buyers, boosting demand. Strength varies by commodity: strongest for oil and industrial metals, weakest for agriculturals and gold in specific regimes.

## Base rates
- Broad commodity index (Bloomberg Commodity Index) vs DXY: rolling 90-day correlation typically -0.5 to -0.7 in normal regimes.
- Oil (WTI, Brent) vs DXY: -0.4 to -0.6 rolling correlation; weakens during supply-shock regimes (2022 Russia invasion decoupled temporarily).
- Industrial metals (copper, aluminum): -0.5 to -0.7; strongest inverse correlation.
- Gold vs DXY: -0.3 to -0.5 in normal regimes; correlation can flatten or invert during fear spikes when both rally as safe havens.
- Agricultural commodities (corn, wheat, soy): weaker DXY correlation (-0.2 to -0.4) because weather and crop cycles dominate.

## When it works
- Clear FX regime — Fed hiking vs cutting cycle produces sustained DXY moves that drag commodities.
- Broad-based DXY moves — a rally driven by ALL DXY components (EUR, JPY, GBP weakness together) is meaningful; a move driven only by JPY collapse is not broad USD strength.
- Multi-week horizons — the correlation shows up on weekly/monthly scale better than daily.
- Combined with real-yield direction — 10Y real yields and DXY often move together; both up = commodity headwind.

## When it fails
- Supply shocks — 2022 oil price spike happened alongside DXY strength (both reflecting geopolitics).
- Commodity-specific stories dominate — a copper mine shutdown decouples copper from DXY temporarily.
- Fear spikes — gold and DXY can both rally in extreme risk-off (2008, March 2020).
- Range-bound DXY periods — when DXY chops in a 2% band, correlation-based trades have no edge.

## Timing and lag
- DXY moves tend to LEAD commodity price responses by 1-5 sessions on average.
- Weekly DXY inflection points are more meaningful than daily wiggles.
- Fed statement days can compress this lag to same-session moves.

## Application
- Commodity trade rubric: `macro_alignment` for a commodity long requires DXY not-rising or weakening trend; long commodity into rising DXY needs explicit override rationale.
- Warning line trigger: long oil / long copper into a DXY breakout deserves `low_star_warning` mention.
- Weekly prep: DXY 20-day direction and any breakout of a key level (DXY 100, 105) belongs in macro setup.
- For gold specifically, note the regime — in fear regimes the DXY correlation weakens or inverts; thesis must state which regime is assumed.
