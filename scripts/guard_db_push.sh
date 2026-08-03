#!/usr/bin/env bash
# Guard: refuse to push data/finance_reporter.db to origin/data-store when the
# push would empty or regress the remote. Exits 1 (blocking) on regression,
# 0 (proceed) on healthy state or legitimate bootstrap.
#
# Design context (2026-08-03): the original workflows used `git init -q -b
# data-store` + `git push -f origin data-store`, which force-rewrites the
# branch to a single-commit history every run. When any run started with an
# empty DB (restore fail, first-time bootstrap misdetection, etc.), the push
# permanently destroyed all prior state. This guard closes that hole.
#
# Contract:
#   - If no local DB file exists: exit 0 (nothing to push, upstream should skip).
#   - If local count >= remote count: exit 0 (proceed).
#   - If remote branch does not exist yet: exit 0 (bootstrap).
#   - If local count < remote count: exit 1 (refuse; preserve remote history).
#
# "Count" here means pitches + trades + report_sends. These are the tables
# whose loss breaks the accuracy loop (§E.24, §C5).
set -euo pipefail

LOCAL_DB="data/finance_reporter.db"

# Fail loud if sqlite3 is missing — otherwise `|| echo 0` in count_db swallows
# every query error and the guard silently passes empty pushes. That is exactly
# the failure mode this script exists to prevent.
if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "guard: FATAL — sqlite3 CLI not available; cannot verify row counts. Aborting push."
  exit 2
fi

if [ ! -f "$LOCAL_DB" ]; then
  echo "guard: no local DB file — nothing to push"
  exit 0
fi

count_db() {
  # Sums pitches + trades + report_sends. Any missing table → 0 (safe default).
  local db_path="$1"
  local count
  count=$(sqlite3 "$db_path" \
    "SELECT (SELECT COUNT(*) FROM pitches) + (SELECT COUNT(*) FROM trades) + (SELECT COUNT(*) FROM report_sends);" \
    2>/dev/null || echo 0)
  # Strip whitespace and default to 0 if empty
  count=$(echo "$count" | tr -d '[:space:]')
  echo "${count:-0}"
}

LOCAL_COUNT=$(count_db "$LOCAL_DB")

REMOTE_COUNT=0
if git ls-remote --exit-code --heads origin data-store >/dev/null 2>&1; then
  # Ensure we have origin/data-store ref locally. Some workflows already fetch;
  # this is idempotent and cheap when already present.
  git fetch origin data-store --depth=1 >/dev/null 2>&1 || true
  REMOTE_DB=$(mktemp)
  if git show origin/data-store:data/finance_reporter.db > "$REMOTE_DB" 2>/dev/null && [ -s "$REMOTE_DB" ]; then
    REMOTE_COUNT=$(count_db "$REMOTE_DB")
  fi
  rm -f "$REMOTE_DB"
fi

echo "guard: local_count=$LOCAL_COUNT remote_count=$REMOTE_COUNT"

if [ "$LOCAL_COUNT" -lt "$REMOTE_COUNT" ]; then
  echo "guard: REFUSING PUSH — local ($LOCAL_COUNT) < remote ($REMOTE_COUNT)."
  echo "guard: This matches the wipe pattern that took out data-store on 2026-08-03."
  echo "guard: Aborting to preserve remote history. Investigate before manual push."
  exit 1
fi

echo "guard: OK — proceeding with push"
exit 0
