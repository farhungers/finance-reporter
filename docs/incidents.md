# FinanceReporter — incident log & recurring failure modes

Purpose: when a similar failure recurs, future-you or future-me needs the
shape of what happened without archaeology through git log. Each entry is a
short capsule with the symptom, the mechanism, the fix, and the guard that's
supposed to catch a recurrence.

Entries are newest-first.

---

## 2026-08-03 — data-store branch wiped by force-push architecture

**Symptom.** After daily performance audit on 2026-08-03, `origin/data-store`
head was a single-commit history (`dc60aec DB snapshot: stats_poller
2026-08-03T13:31:51Z`) containing a valid but **empty** SQLite file — zero
tables, zero rows. All pilot activity since 2026-07-31 was gone from the DB.
Reports had been landing on the operator's Telegram channel through Fri–Mon
morning, but none of that activity was recorded.

**Mechanism.** Every workflow ended with the same pattern:

```bash
TMPDIR=$(mktemp -d)
cp data/finance_reporter.db "$TMPDIR/finance_reporter.db"
cd "$TMPDIR"
git init -q -b data-store          # fresh single-commit repo
git add data/finance_reporter.db
git commit -q -m "DB snapshot: ..."
git push -f origin data-store      # force-overwrites the branch
```

Every push destroys prior history by design. Combined with a soft-fail restore
step (`git show data-store:data/finance_reporter.db > ... || echo "no DB blob
yet"` — the `||` swallows any error), one failed restore anywhere in the chain
started the workflow with an empty DB, Python `init_db()` created fresh
tables, the job ran on empty state, and the commit-step pushed empty back.
From that point every workflow inherited empty state and reinforced it.

Which restore actually failed is not fully knowable — the pre-guard workflow
logs were rotated out of GH Actions by the time we noticed. The candidate
scenarios: a transient `git fetch` failure, a race between two workflows
fetching+pushing near-simultaneously, or a bad-actor push from a manual test.
Doesn't matter — the architecture made a single-point failure catastrophic.

**Recovery.** Local dev DB (`data/finance_reporter.db`, last touched
2026-07-30 09:44) had all pilot data through that date. Force-pushed to
`origin/data-store` as commit `efec3d0`. Activity between 2026-07-31 and
2026-08-03 is lost from the DB but the Telegram messages themselves survived
on the operator's phone.

**Guard.** `scripts/guard_db_push.sh` (commit 5112882) runs before every
workflow's push-to-data-store step. Counts `pitches + trades + report_sends`
locally vs on remote; refuses push if local < remote. Bootstrap-safe (empty
remote → passes). Also refuses when `sqlite3` CLI is missing (commit
12facf1), because a silently-defaulting-to-zero guard is worse than no guard.
Extended in commit 4434b3b to protect the `finance-reporter-backups` mirror
via a `--local-only` mode.

**Watch for recurrence.** Guard step named "Guard DB before push (refuse
empty/regressing state)" in daily_morning, daily_wrap, weekly_lookback,
weekly_prep, stats_poller; and "Guard DB before mirror push" in daily_backup.
If any workflow adds a new push-to-data-store without this step, it reopens
the hole. Regression: `scripts/guard_db_push.sh` behavior is untested — worth
adding a docker-container test that fails when guard is bypassed.

**Longer-term followup.** The `git init` + force-push pattern is inherently
fragile. A better architecture would use a normal commit-on-top of the
existing branch (fetch + commit + push without `--force`) so history is
preserved and merge conflicts surface real state divergence. This has been
deferred because the guard closes the acute failure mode and the operator's
zero-cost constraint restricts state-store options.

---

## 2026-07-29 through 2026-08-03 — GitHub Actions cron drops

**Symptom.** Scheduled workflows fire far less often than their cron
expression says. Sample from 2026-08-03: `stats_poller` cron
`13,43 3-22 * * *` should fire ~40 times/day but produced 2 successes.
`daily_morning` cron `7 0 * * 1-5` frequently deferred multiple hours past
the scheduled time or dropped entirely.

**Mechanism.** GitHub Actions is a best-effort scheduler on private repos —
cron slots contend with the broader queue and are the first thing dropped
under load. Off-peak minutes help but don't fix it. Sibling repo
`farhungers/defi-investor` (also private) fires normally, so it's
finance-reporter-specific, not account-wide. Suspected cause: new-repo
warmup or force-push-to-orphan-branch pattern triggering silent abuse
throttling.

**Recovery / defense.** Two-layer trigger:
- **Plan A (primary):** external `cron-job.org` POSTs `workflow_dispatch`
  at 00:03 UTC Mon-Fri for `daily_morning`. ~99.9% reliability.
- **Plan B (fallback):** GH-native cron kept at 00:07 UTC for the rare
  cron-job.org outage day (~1/year).

Both layers can fire the same workflow; idempotency guard inside
daily_morning.yml (SQL check: `SELECT COUNT(*) FROM report_sends WHERE
report_type='daily_morning' AND sent_at LIKE '<today>%' AND
telegram_message_id IS NOT NULL`) exits before Python setup if the report
already went out.

**Watch for recurrence.** If Tuesday morning's daily_morning report doesn't
land within 15 min of 07:00 IST (03:30 UTC), check cron-job.org dashboard
first (Plan A dropped) and GH Actions run list second. The `heartbeat_*`
workflows were retired 2026-08-03 in commit `a344491` — do not resurrect
without operator sign-off.

---

## Template for new entries

Copy this when adding an incident:

```
## YYYY-MM-DD — short title

**Symptom.** What the operator or the DB or the reports looked like when
something was wrong. What triggered the investigation.

**Mechanism.** The actual cause, ideally down to the code path or workflow
step that failed. Reference commit SHAs when the fix was already shipped.

**Recovery.** What you did to restore state. Command-level detail helps —
future-you should be able to re-execute if the same failure hits again.

**Guard.** What test, script, workflow step, or convention exists now to
detect a recurrence early. If nothing exists yet, name it as a TODO.

**Watch for recurrence.** The specific observable symptom that would tell
you it's happening again. This is the checklist for the next post-mortem.
```
