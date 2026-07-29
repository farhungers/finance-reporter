---
topic_tags: [valuation, narrative, thesis_discipline, story_reset]
applies_to_reports: [daily_morning, weekly_prep, weekly_lookback]
last_reviewed: 2026-07-29
provenance: "Damodaran, The Little Book of Valuation (2024 ed.), Ch 5 'Stories and Numbers', pp 165-195 (approx)"
---

# Stories and numbers — the pitch discipline

Valuation is a bridge between narrative and numbers. Numbers without a story are spreadsheet fantasy — they bend to whatever assumption you want. Stories without numbers are pitch fluff. Every pitch this bot ships must **explicitly link both sides of the bridge**.

## The 3P test — before writing a single number

Before converting any story into a valuation input, subject it to three progressively harder gates:

1. **Possible** (weakest) — Is there any pathway for the story to hold? Rules out logical impossibilities. "Company X invents room-temperature superconductor" is possible; "Company X reverses entropy" is not.

2. **Plausible** (middle) — Is there credible early evidence? Proof-of-concept, small-scale success, market test, or precedent from analogous firms. Zomato expanding into groceries was plausible because Zomato had proven restaurant delivery worked and could reuse the driver network.

3. **Probable** (strongest) — Does the story scale without breaking? Can the firm hold margins, defend against competition, and execute at 10× current size? *Most valuation errors pass "possible" and "plausible" but fail here.*

If a thesis rests on step 3 without evidence, downgrade star rating and flag in the low-star warning.

## Three developments to watch after the pitch ships

Once a pitch is out, incoming news falls into three categories:

- **Story reset** — the fundamental thesis is invalidated. Regulatory ban, catastrophic product failure, loss of critical license, competitive moat collapse. **Action:** exit or aggressive downgrade.

- **Story change** — the thesis is reframed but not destroyed. TAM expands, margin trajectory shifts, new revenue leg opens. **Action:** re-value, adjust position but don't exit.

- **Story noise** — earnings beat/miss by a few cents, CEO reshuffles, macro chatter. **Action:** hold; do not re-price.

The rubric factor `catalyst_proximity` cares about **story-affecting** events, not noise. When resolving pitches in the weekly look-back, use this taxonomy to explain what killed a thesis — "reset" vs "noise the market got wrong" have very different lessons.

## The three drivers every pitch must name

A story-to-number bridge always crosses these three girders. If your pitch doesn't specify a view on each, it's incomplete:

1. **Revenue growth** — driven by TAM × market share × pricing. Explicitly: what's the addressable market, what share can they take, and what happens to price as they scale.

2. **Operating margin** — driven by pricing power, cost efficiency, competitive durability. Commodity businesses cannot sustain high margins; brand/network/switching-cost businesses can. State which the company is.

3. **Reinvestment efficiency** — how much capital per dollar of growth. Software: near-zero. Manufacturing: heavy. Pipeline businesses: enormous. This is what turns growth into cash flow (or doesn't).

## Common pitch pathologies

- **Numbers without story** — a spreadsheet linearly extending historical margins forward, no narrative for why they should hold.
- **Story without numbers** — "AI will transform this business" with no revenue path, no margin assumption, no reinvestment budget.
- **Backwards assembly** — analyst starts from target price, back-solves growth/margin/discount rate to justify it. Every input becomes a plug. **The tell:** unusually round or convenient numbers; assumptions right at the edge of plausible in the direction of the pre-decided answer.
- **Optimism asymmetry** — bullish pitches assume terminal margins expand; bearish pitches assume they compress. Pitches should hold the *same rigor on the same variable in both directions*.

## How to apply in a pitch

- State the story in one sentence at the top: what does the company do differently from consensus expectation?
- Run the 3P test explicitly and pick a level — "This is *plausible* but not yet *probable* — hence 3-star."
- Name the three drivers with a specific view on each.
- Identify one **story-reset watchlist item** for the next 30 days — the single event that would kill the thesis. This is what turns `catalyst_proximity` from a checkbox into a real risk factor.
- On weekly look-back, classify resolved outcomes as reset / change / noise. The **noise** column is where the LLM's calibration mistakes live and should shrink over time.
