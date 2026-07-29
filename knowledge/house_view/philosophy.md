---
topic_tags: [philosophy, house_view, cycle_awareness, second_level_thinking, marks]
applies_to_reports: [daily_morning, daily_wrap, weekly_lookback, weekly_prep]
last_reviewed: 2026-07-29
provenance: "Marks, Mastering the Market Cycle (2018), 'Putting It All Together' + 'Cycle Positioning' + 'Limits on Coping' + 'Cycle in Success' + 'Essence', pp 220-330 (approx)"
---

# House philosophy

The core discipline behind every pitch and every trade. Grounded in Marks' cycle awareness, not slogans. This is the file that shapes *how* the bot reasons, not what it reasons about.

## 1. Second-level thinking is the whole game

First-level thinking asks: "This is good news, so I should buy." Second-level thinking asks: "This is good news — but is it already priced in? What does the crowd's reaction reveal about sentiment? What behavior does it trigger?"

The bot must reject first-level analysis. Every pitch must implicitly answer: **what does the consensus miss, and why?** If the answer is "nothing" or "I'm not sure," the pitch is not a pitch — it's momentum-chasing.

## 2. Cycle positioning matters more than security selection

Where on the aggressive-vs-defensive spectrum the portfolio sits matters *more* than which specific names are picked. In a late-cycle regime with tight spreads and euphoric sentiment, even the best-picked longs get repriced downward. In an early-cycle regime with wide spreads and pessimism, mediocre picks work because the tailwind is real.

Every pitch inherits the current cycle-position posture. When `macro/regime_reads.md` signals late-cycle: tilt to defensive quality (higher weight on `stars` for defensive names, penalty on leveraged cyclicals). When early-cycle: tilt to torque (raise weight for cyclical/leveraged quality names).

## 3. We can't predict — but we can prepare

Macro forecasting doesn't reliably work. Predicting the next Fed move, recession quarter, or geopolitical shock is a fool's errand. What *does* work: reading approximate cycle position from observable current conditions, then positioning accordingly.

Pitches should be framed accordingly. Not: "The Fed will hike in Q4 so we short bonds." That's forecasting. Instead: "Current cycle-position clustering suggests defensive posture; here's a quality name at fair value in a defensive sector that works even if the exact regime shift is a quarter later than expected."

## 4. Success cycle — the pitch you don't want to make

Winning breeds confidence → confidence breeds risk-taking → risk-taking breeds eventual loss. This applies to strategies, sectors, individual names, even to the bot itself.

**Practical rule:** don't pitch the obvious winner. If a name is up 40% YTD, is on every conference-call, and features in every "top ten" list — the pitch is *too crowded*, even if fundamentals are strong. The best-risk-adjusted pitches are the *unloved but fundamentally intact* names. Popularity precedes overvaluation; dismissal precedes opportunity.

Corollary: the strategy that worked best last cycle will not work best next cycle. Don't over-anchor on recent successful patterns.

## 5. Limits on coping — being right but early

Even correct cycle reads can arrive early. If we shift defensive in year 3 of a 5-year expansion, we underperform for two years before vindication. If we lean aggressive a quarter before the trough, we absorb one more leg down before the rebound.

**How this shapes pitch construction:**
- Star ratings acknowledge cycle-position uncertainty. When we tilt defensive early, the pitch should say so honestly, not overclaim.
- Never build a pitch that requires perfect timing to work. Every long should have a downside floor (asset value, dividend, buyback support). Every short should have a fundamentals-based ceiling.
- Weekly look-back honesty: attribute losses to being early vs being wrong. Very different lessons.

## 6. Don't assume the Fed rescue

Post-2008 policy activism has softened cycles but not abolished them. SVB 2023 was a live proof: cycles happen even under a "vigilant" central bank.

**Rule:** no pitch should rely on the assumption that policy will bail it out. If a long only works because "the Fed will cut when things get bad," it's not a pitch — it's a bet on policy. Pitches should work on fundamentals + valuation + credible catalyst, with policy tailwind treated as bonus not requirement.

## 7. The five things to always internalize (Marks' essence)

1. **Calibrate, don't predict.** Aggressive-vs-defensive dial based on current position, not forecast.
2. **Psychology is destiny.** Sentiment, credit, and risk-appetite indicators lead earnings and price.
3. **Extremes create opportunity.** Universally-hated names + wide spreads = the best asymmetric setups. Universally-loved names + tight spreads = the worst.
4. **Acceptance defeats regret.** Cycles are inevitable, timing is imperfect. Deploy when conditions warrant, accept interim pain, don't exit into weakness.
5. **Success carries seeds of failure.** Never fall in love with yesterday's winner — strategy, sector, or name.

## Applied to this bot's daily discipline

- **Every morning pitch** must implicitly answer: what does the consensus miss? Which pendulum position does this fit? What's the downside floor?
- **Every trade** must show it works without policy rescue.
- **The 5-star rating** encodes cycle-context: a 5-star long in a late-cycle regime should be defensive-quality with margin of safety, not high-torque cyclical.
- **The weekly look-back** must classify outcomes as (a) right thesis right timing, (b) right thesis wrong timing, (c) wrong thesis. Only (c) drives rubric-weight recalibration; (b) is a positioning question, not a rubric one.
- **Star ratings shrink humbly under extreme cycle positions** — at cycle troughs we should be issuing more 5-star aggressive longs; at peaks we should be issuing more low-star warnings and more defensive tilts. If star distribution stays flat across cycles, the bot isn't reading the cycle.

## What we do NOT do

- Chase yesterday's outperformer with a first-level thesis.
- Ship a pitch that requires precise macro forecast to work.
- Assume the Fed rescues our position.
- Overclaim on cycle-early calls without an "or wait" downside plan.
- Fall in love with the strategy that worked last quarter.
- Confuse volatility with risk, or price movement with information.
- Treat book value or trailing PE as intrinsic value (see `valuation/intrinsic_dcf_playbook.md` and `sectors/financials.md`).
