#!/usr/bin/env bash
# HERMES setup — Ubuntu 24.04
set -e
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip git ufw fail2ban unattended-upgrades mosh tmux
sudo ufw allow 49500/tcp; sudo ufw --force enable
# mosh butuh UDP 60000-61000 (anti-lag SSH dari Indonesia->EU)
sudo ufw allow 60000:61000/udp
cd "$(dirname "$0")/.."
python3 -m venv hermes-env
./hermes-env/bin/pip install --upgrade pip
./hermes-env/bin/pip install -r hermes_bot/requirements.txt
[ -f .env ] || cp .env.example .env
echo "SELESAI -> edit .env -> scripts/test_latency.sh -> scripts/update_cron.sh"
