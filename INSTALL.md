# INSTALL — VPS Ubuntu 24.04
1. Upload:  scp -P 49500 hermes-bundle.zip ubuntu@IP:~   lalu ssh -p 49500 ubuntu@IP
2. Ekstrak: unzip hermes-bundle.zip && cd hermes-bundle
3. Setup:   chmod +x scripts/*.sh && ./scripts/setup_vps.sh
4. Kredensial: nano .env  (LLM_BASE_URL/LLM_API_KEY dari juan router;
   TELEGRAM_BOT_TOKEN dari @BotFather; TELEGRAM_CHAT_ID dari getUpdates)
5. Fase 0:  ./scripts/test_latency.sh   -> wajib semua HTTP 200 & median <400ms
6. Uji:     ./hermes-env/bin/python -m hermes_bot.run_scan
7. Aktif:   ./scripts/update_cron.sh

TROUBLESHOOT:
- NO_DATA banyak -> endpoint diblokir; cek test_latency.sh, cek cache/
- Telegram gagal -> kirim /start ke bot dulu; cek token/chat
- Cron mati -> crontab -l; lihat log/cron.log
- Stop darurat -> touch KILL (di root bundle); resume: rm KILL
