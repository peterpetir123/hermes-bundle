# TUGAS AKTIF Hermes — 4 Fase (sumber kebenaran tugas berjalan)

> Ditetapkan Nahkoda 2026-09-11. Kerjakan berurutan, laporkan tiap fase
> verbatim sebelum lanjut. Setelah selesai (atau mentok): append
> MIND/SESSION-LOG.md, commit + push. Hapus file ini saat SEMUA fase selesai.

=== FASE 0: SINKRON ===
1. cd ~/hermes-bundle && git pull
2. Verifikasi minimal 3 commit terbaru hadir: 88c76ee (OKX pagination +
   digest persist), a577c15 (hardening), f805b59 (backtest + MIND/).
3. Laporkan: git log --oneline -3

=== FASE 1: VERIFIKASI 24/7 ===
1. crontab -l  -> 3 entry (run_scan :05 tiap jam; run_scan --digest 00:15;
   watchdog */30). Laporkan.
2. cat log/last_scan.json -> timestamp < 2 jam. Laporkan.
3. ./hermes-env/bin/python -m hermes_bot.watchdog -> laporkan output.
4. ls -la state/state.json.bak -> harus ada, timestamp denyut terakhir.
DILARANG: ubah config.yaml, jalankan setup_vps.sh, sentuh kredensial.

=== FASE 2: DASHBOARD WEB (local-only) ===
1. Buat hermes_bot/web/server.py — http.server stdlib murni, TANPA
   dependensi baru, bind WAJIB 127.0.0.1:8080 (DILARANG 0.0.0.0):
   GET /                      -> index.html (static)
   GET /api/state             -> state/state.json + field "saldo_real": null
   GET /api/scan              -> log/last_scan.json
   GET /api/candles?coin=BTC  -> cache/BTC-1d.json
   GET /api/mind              -> MIND/SESSION-LOG.md
   GET /api/backtest?coin=BTC -> backtest_results/BTC.json
2. Buat hermes_bot/web/index.html — vanilla JS, tanpa CDN:
   - kartu: SALDO DEMO | SALDO REAL (n/a) | day PnL | mode TESTNET
   - tabel posisi terbuka: koin / entry / SL / PnL
   - candlestick canvas murni + pilih aset
   - panel backtest per aset: n, WR, PF, totR, maxDD, MC p95
   - auto-refresh 30 detik via fetch (bukan reload)
   - Tidak ada kredensial di file mana pun.
3. Agar hidup 24/7 tanpa sesi SSH: ~/.config/systemd/user/hermes-web.service
   (Restart=always, ExecStart=<venv python> -m hermes_bot.web.server,
   WorkingDirectory=~/hermes-bundle), lalu:
   systemctl --user daemon-reload && systemctl --user enable --now hermes-web
   && loginctl enable-linger ubuntu
4. Uji & laporkan verbatim: curl -s 127.0.0.1:8080/api/state | head -c 300
   dan curl -s -o /dev/null -w "%{http_code}" 127.0.0.1:8080/

=== FASE 3: BACKTEST DUAL-WINDOW (9y penuh + 3y terakhir) ===
1. Jalankan (engine + report SUDAH ada upstream — JANGAN ubah logikanya):
   ./hermes-env/bin/python -m hermes_bot.backtest.run_backtest --all
2. Laporkan tabel hasil. Data HL asli = uji pertama engine. Jika ada aset
   NO_DATA: laporkan jumlah bar diterima, BERHENTI, jangan patch sendiri.
3. Commit + push: backtest_results/ (termasuk SUMMARY.md) dan append
   MIND/SESSION-LOG.md (apa yang dikerjakan, hasil, kendala, keputusan +
   alasan). Push gagal -> catat log/alarm.log, jangan retry tanpa batas.
4. DILARANG: menaikkan sizing / mengubah config berdasar hasil.
   Laporan = tugasmu; keputusan = Nahkoda.

=== ATURAN GLOBAL ===
- Konstitusi: trading_brain_rules/ (parameter beku, Referensi-Probabilitas).
- Keputusan terkunci: lihat MIND/KEPUTUSAN.md — jangan batalkan tanpa
  instruksi Nahkoda.
- Langkah ambigu / data aneh -> BERHENTI, laporkan, tunggu Nahkoda.
