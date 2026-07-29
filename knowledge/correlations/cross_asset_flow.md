---
topic_tags: [correlations, cross_asset, risk_on_risk_off]
applies_to_reports: [weekly_prep]
last_reviewed: 2026-07-29
provenance: "curated 2026-07-29 from established macro literature (Bridgewater All Weather, Ilmanen) + cross-asset flow practice"
---

# Cross-asset flow: risk-on / risk-off

## Core rule
Correlations are regime-dependent, not constant. In risk-on regimes, equities and cyclical commodities rally together while gold and Treasuries lag; in risk-off regimes, Treasuries and gold rally while equities and credit sell off. When historical correlations break, that IS the signal.

## Base rates
- SPY / QQQ / IWM alignment (all three trending together) confirms the equity trend; divergence between them is a leading tell of rotation.
- Gold-Treasury correlation is positive in fear regimes (~+0.4 to +0.7 rolling), near zero in normal regimes, and can turn negative during stagflation fears.
- Crypto (BTC) correlated ~+0.4 to +0.6 to Nasdaq during 2022-2024 tightening cycles — the "digital gold" narrative broke during that period.
- Bond-equity correlation flipped from negative (2000s-2010s) to positive (2022-2023 inflation era) — the classic 60/40 diversification argument depends on this correlation.
- HYG (high-yield credit) leads equities by 1-5 sessions at inflection points ~55-65% of the time.

## When it works
- Clear macro regime (tightening, easing, expansion, contraction) — correlations behave textbook.
- Cross-asset confirmation on breakouts — SPY breakout + falling DXY + falling VIX = higher-quality signal.
- Divergence signals — IWM lagging SPY into a rally = narrow leadership warning.
- Credit-equity divergence — HYG topping while SPY makes new highs is a classic warning.

## When it fails
- Regime transitions — old correlations break weeks before the new regime is obvious.
- Idiosyncratic events (single-stock crash, specific commodity shock) — cross-asset signal is uninformative.
- Central-bank surprise days — all correlations get distorted for 24-72 hours.
- Very low realized volatility periods — correlations get noisy and unreliable.

## Application
- Rubric use: `macro_alignment` gets its point when the trade direction matches the prevailing cross-asset regime (long equity in risk-on, long gold in risk-off, etc.).
- Warning line trigger: pitch direction that contradicts current cross-asset flow deserves a `low_star_warning`.
- Pair-check for crypto trades: BTC-Nasdaq correlation regime affects whether crypto is trading on macro or on idiosyncratic flow.
- Weekly prep highlight: any correlation break vs. 20-day norm gets a mention in "macro setup going in."
