---
topic_tags: [macro, fomc, fed, rates, us]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-08-24
provenance: "operator+audit populated 2026-08-24 from FOMC transcripts + post-decision vol studies 2019-2025"
---

# FOMC playbook

## What it is
The Federal Open Market Committee (FOMC) is the 12-member body inside the Fed that sets US monetary policy. Meets 8 times per year (roughly every 6 weeks). Two-day meetings; policy decision released at **14:00 ET on day 2**, followed by Chair Powell's **press conference at 14:30 ET**. Four of the eight meetings (March, June, September, December) also release the **Summary of Economic Projections (SEP)** and the **dot plot** (each member's projected fed funds rate).

Decision-day sequence:
- **14:00 ET** — Rate decision + written statement drop simultaneously.
- **14:00 ET (SEP meetings only)** — Dot plot and macro forecasts drop with the statement.
- **14:30 ET** — Powell begins prepared remarks. Q&A starts ~14:40.
- **15:15-15:30 ET** — Presser typically ends. Post-presser drift often reverses the initial statement reaction.

## Historical reaction (post-2022 regime)
- **Statement drop (14:00 ET):** Initial 5-15 minute burst of vol. 2Y and dollar move first; equities lag by seconds. Move magnitude ~40-60% of the full FOMC-day range.
- **Presser (14:30-15:15):** Second, often bigger, vol wave. When Powell's tone diverges from the statement (2023 was full of these), presser tone wins.
- **Full-day SPX range:** Averaged ~1.5-2.2% high-to-low on FOMC days 2022-2024. Above 3% only on genuine surprises (2022 hawkish June, 2023 May cut hint).

## Playbook — statement-vs-presser divergence patterns
1. **Statement hawkish, presser dovish** → Initial rates+, equities-. Reverses hard into close as presser lands. Fade the initial move.
2. **Statement dovish, presser hawkish** → Initial rates-, equities+. Reverses similarly. Powell has done this repeatedly (Dec 2023, Mar 2024).
3. **Both aligned hawkish** → Full-day trend move. Don't fade.
4. **Both aligned dovish** → Full-day trend move. Don't fade.
5. **Statement dry, presser neutral** → Vol crush; option sellers win. This is the modal outcome in extended-pause regimes.

## Playbook — dot-plot dynamics (SEP meetings)
See `dot_plot_playbook.md` for full detail. Fast read on decision day:
- **Median 2025 dot down** vs prior SEP → dovish (rates lower, SPX up).
- **Median 2025 dot up** → hawkish (rates up, SPX down).
- **Long-run dot ("neutral rate") up** → structurally hawkish; hurts long-duration assets even if short-run dots unchanged.
- **Dispersion widening** (max-min range) → signals internal disagreement; typically raises IV for the next 3-6 weeks.

## Positioning going in
- **SPX 1-day straddle 24h pre-meeting:** Typical 0.9-1.3%. Above 1.5% = market braced for hawkish action. Below 0.7% = complacency — surprise magnitude gets amplified.
- **Fed funds futures for the meeting:** If <60% pricing of the "expected" decision, high surprise risk.
- **Term SOFR curve steepness:** If 1Y-2Y SOFR curve steep, market pricing cuts; a hawkish hold produces bigger sell-off.

## Common wrongness
- **Reading dots as forecast rather than reaction function anchor.** Members' dots reflect what they'd do IF their forecast played out — the forecast is what to interrogate.
- **Trading the 2:00 spike.** ~40% of the full-day move reverses during the presser. Sizing at 2:00 is trading a partial signal.
- **Ignoring the neutral-rate dot in favor of near-term.** Long-run dot shifts are structurally more important for duration + growth stocks than any 1-year forecast change.
- **Assuming Powell = the statement.** Powell has repeatedly used the presser to soften or firm the written message. Watch the Q&A, not the intro.

## Reference dates for base-rate anchoring
- FOMC Jun 2022 (75bp hike, first since 1994): SPX -3.3%, 2Y +25bps.
- FOMC Dec 2023 (dovish pivot, Powell mentions cuts): SPX +1.4%, 2Y -30bps — set stage for 90bps of cuts pricing in 3 weeks.
- FOMC Mar 2024 (dot-plot median 2024 stayed at 3 cuts vs feared 2): SPX +1.0%, gold + tech ripped.
- FOMC Sep 2024 (50bp cut, first cut of cycle): SPX flat-to-down (buy-the-rumor sell-the-fact); yields rose.
- FOMC Sep 2025 (25bp cut, restart of easing): reactions consistent with dovish-cut playbook — rates down, cyclicals up.

## /stats-relevant note
Prior audit found 4-of-5 five-star FOMC-day pitches under-performed 2023-2024 when the pitch was placed pre-statement without provision for post-presser reversal. Rubric factor `catalyst_proximity` should be 1 but `technical_setup` requires an explicit invalidation level survivable through the 2-hour vol window.
