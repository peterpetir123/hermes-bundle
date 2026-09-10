# HERMES BUNDLE — Bot Trading Otomatis 24/7 (Hyperliquid + Polymarket overlay)

Fondasi: DON-D1 breakout 40d + regime gate + trailing 3.5xATR
= +78.6R / 12.465 trade / 9 tahun (PF 1.28, maxDD -12.7R) — lihat trading_brain_rules/.

ARSITEKTUR:
- Mesin aturan (0 token) = PEMUTUS: data -> regime -> sinyal -> risk -> exec
- GLM 5.3 (juan router)  = PELAPOR: digest harian + telaah tesis Nahkoda
- Telegram               = MATA: alert template (buka/tutup/CB), digest
- Polymarket             = KONTEKS: implied probability (report-only, bukan gate)

LARANGAN PERMANEN: LLM tidak pernah mengirim order. Parameter berubah hanya
lewat gerbang bukti (backtest/validate.py LULUS -> baru edit config.yaml).

QUICK START (VPS Ubuntu 24.04):
  scp -P <PORT> hermes-bundle.zip ubuntu@<IP>:~
  ssh -p <PORT> ubuntu@<IP>
  unzip hermes-bundle.zip && cd hermes-bundle
  chmod +x scripts/*.sh && ./scripts/setup_vps.sh
  nano .env                          # isi API keys
  ./scripts/test_latency.sh          # Fase 0 wajib LULUS
  ./hermes-env/bin/python -m hermes_bot.run_scan     # uji manual (paper)
  ./scripts/update_cron.sh           # denyut 24/7

HARD RAILS: CB harian 15% | maks 3 posisi | KILL-switch file | leverage-stop
| long-only | data basi = NO TRADE | Polymarket tak pernah memicu eksekusi.

TAHAP: A testnet ($0) -> B live kecil (agent key) -> C skala. Gerbang bukti
di DEPLOY_GUIDE.md. Bukan nasihat keuangan; modal = uang siap hilang.
