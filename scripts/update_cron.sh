#!/usr/bin/env bash
# HERMES update_cron.sh — pasang denyut 24/7 (crontab user, tanpa sudo)
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="$DIR/hermes-env/bin/python"
CRON_FILE="/tmp/hermes_cron_$USER"
printf '%s\n' \
"5 * * * * cd $DIR && $PY -m hermes_bot.run_scan >> log/cron.log 2>&1" \
"10,40 * * * * cd $DIR && $PY -m hermes_bot.run_scan --monitor >> log/cron.log 2>&1" \
"15 0 * * * cd $DIR && $PY -m hermes_bot.run_scan --digest >> log/cron.log 2>&1" \
"*/30 * * * * cd $DIR && $PY -m hermes_bot.watchdog >> log/cron.log 2>&1" \
> "$CRON_FILE"
( crontab -l 2>/dev/null | grep -viE 'hermes[-_]?(bundle|bot|env)|run_scan|watchdog' || true ; cat "$CRON_FILE" ) | crontab -
rm -f "$CRON_FILE"
echo "Cron aktif:"
crontab -l
