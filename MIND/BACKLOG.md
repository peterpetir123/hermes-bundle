# BACKLOG Hermes — antrean fitur (BUKAN tugas berjalan)

> Kerjakan HANYA saat Nahkoda memberi tugas eksplisit. Urutan = prioritas.

## 1. [Besok, 13-14 Sep] Telegram alert dasar
- Nahkoda buat bot via @BotFather -> token + chat_id-nya -> isi .env VPS
  (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID) — TIDAK di-commit.
- Verifikasi: alert_open/alert_close/digest terkirim nyata ke HP Nahkoda.
- Fungsi kirim sudah ada di notify/telegram_bot.py — tinggal kredensial.

## 2. [Setelah alert dasar jalan] Telegram kontrol /stop /on /status
- /stop  -> touch KILL   (entry dibekukan; denyut tetap jalan — mekanisme
            KILL-switch SUDAH ADA di exec/risk.py + watchdog)
- /on    -> rm KILL
- /status -> balas 3 baris: mode, equity, posisi terbuka, alarm aktif
- WAJIB: whitelist chat_id (hanya chat_id Nahkoda dipatuhi; pesan lain
  diabaikan + dicatat). Balasan konfirmasi tiap perintah.
- Arsitektur: long-polling getUpdates ringan (stdlib), jangan webhook
  (butuh TLS/publik). Poll interval 5s cukup. Resource VPS 2GB aman.
- DILARANG: perintah lain (jangan buat /sell /buy /close — mesin aturan
  yang memutus, bukan chat).

## 3. [20 Sep] Evaluasi XRP
- XRP merah di dual-window (PF 0.56, -3.2R, MC p95 6.9).
- Keputusan Nahkoda 13 Sep: PERTAHANKAN selama demo week (gate melindungi,
  biaya ~nol). Evaluasi ulang dengan data minggu ini di WEEK-REPORT.

## 4. [Nanti, Tahap B] Saldo real di dashboard
- Field saldo_real sudah disiapkan (null). Aktif saat private key HL
  agent dipasang — JANGAN isi sebelum Nahkoda membuka Tahap B eksplisit.
