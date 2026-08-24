---
topic_tags: [macro, treasury, auctions, rates, us]
applies_to_reports: [daily_morning, weekly_prep]
last_reviewed: 2026-08-24
provenance: "operator+audit populated 2026-08-24 from TreasuryDirect auction results + primary dealer commentary"
---

# Treasury auctions playbook

## What they are
The US Treasury regularly auctions new debt to fund the government. Markets watch three tenors closely, released via TreasuryDirect at **13:00 ET on auction day**:

- **3-year note** — auctioned monthly, typically Tuesday of "refunding week" (roughly first full week of Feb/May/Aug/Nov plus a mid-quarter one).
- **10-year note** — auctioned Wednesday of refunding weeks.
- **30-year bond** — auctioned Thursday of refunding weeks (the long-end demand read).

Also matters but lower impact:
- 2-year, 5-year, 7-year notes (monthly).
- Bill auctions (weekly, low impact except when funding-stress signal).
- TIPS (Treasury Inflation-Protected Securities) — quarterly, moves breakevens.

## What to watch on results
Three numbers set the tone at 13:00:

1. **Stop-out yield vs when-issued (WI)** — the "tail." Auction cleared at a yield higher than pre-auction WI = "tailed" = weak demand. Cleared lower = "stopped through" = strong demand.
   - Tail ≥1bp = weak.
   - Stopped through ≥0.5bp = strong.
   - Right on the WI = in-line.

2. **Bid-to-cover ratio** — total bids ÷ amount offered. Higher = more competitive demand.
   - Recent norms: 3Y around 2.5x, 10Y around 2.4x, 30Y around 2.3x. Below 2.2x on any tenor = weak.

3. **Indirect bidder share** — proxy for foreign central bank + fund manager demand. Higher = healthier structural demand.
   - Recent norms: 60-70% typical for 10Y and 30Y. Below 55% = weak foreign demand (often USD-negative and rate-negative).
   - Above 75% = strong (bullish for duration).

## Historical reaction
- **Weak 30-year auction (tail ≥3bps + indirect <55%):** 30Y yield +5-10bps immediately, 10Y +3-6bps, SPX -0.5% (equity duration hit), USD reaction mixed (weak demand suggests weak dollar, but higher yields support dollar — usually flat).
- **Strong 10-year (stopped through ≥1bp + indirect >70%):** 10Y yield -3-6bps, SPX +0.3% to +0.6%, USD softens marginally.
- **In-line result:** minimal reaction. Bond market's positioning was correct.
- **After a series of weak auctions (2+ in a month):** the "supply concern" narrative activates. Term premium rises broadly; long-duration equities lag; gold sometimes catches a bid.

## Playbook
- **Refunding week is a scheduled 3-day vol window.** 3Y Tuesday → 10Y Wednesday → 30Y Thursday. Positioning shifts through the week based on prior day's results.
- **Foreign demand signal via indirects.** Chronic weakness in indirect share (multi-month trend) = structural USD-negative and rate-positive. This is the "de-dollarization" concern in specific form.
- **Auction size matters.** Treasury announces upcoming auction sizes at the Quarterly Refunding Announcement (QRA, released Monday before refunding week). Larger-than-expected sizes = pre-auction rates+ / equities- reaction; smaller = the opposite.
- **QRA misreads.** Markets sometimes react to gross vs net supply confusion. Net new supply matters (accounting for maturities); gross does not.
- **Auction concessions.** In the 24-48 hours pre-auction, yields typically drift 2-5bps higher (dealers cheapen the sector to make room). This is the "concession" — the reverse move post-auction if demand is strong.

## Common wrongness
- **Reading bid-to-cover as the primary signal.** Tail vs WI is more accurate — bid-to-cover includes weak bids that don't clear.
- **Assuming a weak auction = imminent yield spike.** One weak auction is a data point; the pattern over a month is the signal.
- **Ignoring bill auctions except in crisis.** During funding stress (Sep 2019, Mar 2020), bill auction dynamics preceded equity vol.
- **Reading only one tenor.** Cross-tenor comparison (weak 30Y + strong 3Y = curve-steepening signal) is where the narrative sits.

## Reference dates for base-rate anchoring
- 20-year Bond auction May 2023 (weak, tailed 3.4bps): 20Y yield +12bps intraday, 10Y +6bps.
- 30-year Bond auction Aug 2023 (weak, indirect share dropped to 60% from 75% prior): 30Y +7bps, contributed to summer bond rout.
- 10-year Note auction Nov 2024 (strong, stopped through 1.6bps): 10Y yield -5bps, SPX +0.4%.
- QRA Nov 2023 (Treasury shifted issuance to bills from coupons): long-end rallied hard (30Y -15bps), sparked "peak yields" narrative.
- QRA Feb 2024 (higher coupon sizes than expected): 10Y +8bps in the immediate aftermath.
