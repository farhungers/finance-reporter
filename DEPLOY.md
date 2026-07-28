# FinanceReporter — GitHub Actions deployment

Operator-only walkthrough. Takes ~10 minutes. Assumes Session 0 code is on your local disk (`C:\FinanceReporter\`) with the `.env` file already populated.

---

## 1. Create the private GitHub repo (2 min)

1. Go to https://github.com/new
2. Name: `finance-reporter` (or anything you like)
3. **Visibility: Private** — pitch history in the DB will be committed to a `data-store` branch; private keeps that off public search
4. Do **NOT** initialize with a README, .gitignore, or license (you have those already)
5. Click **Create repository**
6. Copy the SSH or HTTPS URL GitHub shows you (e.g., `git@github.com:USERNAME/finance-reporter.git`)

---

## 2. Push local code to GitHub (2 min)

Open a terminal in `C:\FinanceReporter\` and run:

```bash
git init -b main
git add .
git status                                # verify .env is NOT listed (it's gitignored)
git commit -m "initial commit — Session 0 lock"
git remote add origin <PASTE URL FROM STEP 1>
git push -u origin main
```

**Sanity check before push:** run `git status --ignored | grep .env` — you should see `.env` in the ignored list. If `.env` shows in tracked files, STOP — the token is about to be pushed to a public place.

---

## 3. Add 3 GitHub Secrets (2 min)

In your new repo, go to **Settings → Secrets and variables → Actions → New repository secret**. Add these three (names must match exactly):

| Name | Value | Where it came from |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `8912663833:AAFeSka_c3NayDsU1XP597-fhezvxJty3dc` | @BotFather (Session 0 setup) |
| `TELEGRAM_CHAT_ID` | `226763300` | your DM with `@TheCapitalOrder_bot` |
| `GROQ_API_KEY` | `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` | https://console.groq.com/keys |

These are encrypted at rest and only injected into workflow runs. Not visible again after saving (only editable).

---

## 4. Enable Actions (already on by default for new repos)

Go to **Actions** tab. GitHub may show a "Get started" screen — click **"I understand my workflows, go ahead and enable them."**

You should see 5 workflows listed in the left sidebar:
- `daily_morning`
- `daily_wrap`
- `weekly_lookback`
- `weekly_prep`
- `daily_backup`

Plus the reusable `_run_report (reusable)` which never runs on its own.

---

## 5. First smoke test — manual trigger (1 min)

Click **daily_morning → Run workflow → Run workflow** (green button). This uses `workflow_dispatch` to fire the workflow immediately instead of waiting for the 04:00 UTC cron.

Watch the run:
- Should take 30-60 seconds
- Green checkmark = success; a message lands in your Telegram DM
- Red X = failure — click into the run, expand the failing step, screenshot me the error

**First run creates the `data-store` branch automatically.** Verify by looking at Branches → All branches — you'll see `main` and `data-store` after a successful run.

---

## 6. Confirm the scheduled crons are live

- Go to **Actions → daily_morning**
- Below the workflow name you should see: "This workflow has a `schedule` event trigger." with the cron string
- No further action needed — GitHub will auto-fire at 04:00 UTC Mon-Fri going forward

**Known caveat:** GitHub Actions cron can drift 5-15 minutes late during peak times. Your friend may see reports arrive at 07:03 IST or 07:12 IST some days rather than exactly 07:00. Non-fatal.

---

## 7. If you need to pause the bot

Two ways:
- **Nuclear:** Actions tab → each workflow → `...` → **Disable workflow**. Re-enable when done.
- **Per-report kill switch:** edit `_run_report.yml` and set e.g. `KILL_SWITCH_DAILY_MORNING: 'true'` for that report only. Commit → push → cron respects it on the next run.

---

## 8. Ongoing — what to expect

- **11 workflow runs per week** (5 daily_morning + 5 daily_wrap + 1 weekly_lookback + 1 weekly_prep + 7 daily_backup = 19 total, each ~30-60s)
- **Estimated GitHub Actions minutes/month:** ~40 min (private repo free tier allows 2000/mo — ~2% of budget)
- **DB grows** on every run; committed to `data-store` branch. Small (~KB per report), no size concern for years
- **Groq usage:** ~30 calls/week × ~5K tokens each = 150K tokens/week; well under Groq's 12K TPM free tier per-minute limit and 14400 daily request limit

---

## 9. Session 0 close-out checklist

Once step 5 (smoke test) shows a green run + you receive the Telegram message in your DM, Session 0 is fully complete. Sign it off with a message like *"Session 0 shipped; kill switches all off; Phase 1 live."*

Follow-ups still open (not blocking Phase 1):
- Populate `knowledge/house_view/active_themes.md` with current themes (edit the file, commit, push — takes effect next report)
- Populate `knowledge/blue_chip/*_facts.md` with real content as book extractions land
- Address `datetime.utcnow()` deprecation warnings from Python 3.14

---

## Troubleshooting

**Symptom: workflow run fails with `429 rate_limit_exceeded` from Groq**
→ Groq's free tier is 12K TPM. Our reports use ~7K, so this shouldn't happen. If it does, the knowledge library was recently populated with a lot of content. Reduce `knowledge/blue_chip/*_facts.md` verbosity or split by ticker.

**Symptom: message doesn't arrive in Telegram**
→ Check the workflow log for `msg_id=<number>` line. If present, Telegram accepted it; check the DM chat you're using. If `msg_id=None`, look for `telegram send failed:` earlier in the log.

**Symptom: report arrives but formatting is broken**
→ Almost always an unescaped MarkdownV2 character. Copy the raw output from the workflow log; check `src/telegram_send.py::esc()` covers the character. Regression test lives in `tests/test_telegram_escape.py`.

**Symptom: workflow disabled after 60 days**
→ GitHub disables scheduled workflows on repos with no activity for 60 days. Our workflows commit the DB back on every run, so activity is continuous — this shouldn't trigger. If it does, click **"Enable workflow"** in the Actions tab.

**Symptom: DB history in `data-store` branch getting large**
→ Every run creates a new orphan-branch commit that replaces history (force-push). Branch stays at 1 commit deep. No growth concern.
