#!/bin/bash
# Daily cron job: pull latest Google Scholar metrics into index.html and push if they changed.
# Installed in crontab (see README). Log: scripts/daily_stats.log (not committed).
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO" || exit 1
echo "=== $(date '+%F %T')"
git pull --rebase -q origin main || { echo "pull failed"; exit 1; }
/usr/bin/python3 -I scripts/update_stats.py
if ! git diff --quiet -- index.html; then
  git add index.html scripts/scholar-cache.json
  git commit -q -m "Home: refresh Google Scholar statistics" && git push -q origin main && echo "pushed"
else
  # Numbers unchanged: drop the cache's new fetch date so the tree stays clean
  git checkout -q -- scripts/scholar-cache.json 2>/dev/null
  echo "no change"
fi
