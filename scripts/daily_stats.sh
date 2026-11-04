#!/bin/bash
# Daily cron job: pull latest Google Scholar metrics into index.html and push if they changed.
# Installed in crontab (see README). Log: scripts/daily_stats.log (not committed).
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO" || exit 1
echo "=== $(date '+%F %T')"
for i in 1 2 3 4 5; do git pull --rebase -q origin main && break; [ $i = 5 ] && { echo "pull failed"; exit 1; }; sleep 60; done
/usr/bin/python3 -I scripts/update_stats.py
if ! git diff --quiet -- index.html; then
  git add index.html scripts/scholar-cache.json
  git commit -q -m "Home: refresh Google Scholar statistics"
  # GitHub SSH auth occasionally fails; retry for up to ~10 minutes
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if git push -q origin main 2>/dev/null; then echo "pushed (try $i)"; exit 0; fi
    sleep 60
  done
  echo "push failed; will go out with the next successful push"
else
  # Numbers unchanged: drop the cache's new fetch date so the tree stays clean
  git checkout -q -- scripts/scholar-cache.json 2>/dev/null
  echo "no change"
fi
