# BACKLOG Hermes — antrean fitur (BUKAN tugas berjalan)

> Kerjakan HANYA saat Nahkoda memberi tugas eksplisit. Urutan = prioritas.

## 1. [SELESAI 13 Sep] Telegram alert dasar
- alert_open/close/system/digest sudah ada; kredensial di .env VPS (Nahkoda pasang, Hermes verifikasi).

## 2. [SELESAI 13 Sep] Telegram kontrol /off /on /status /ask /learn
- /off (pause total + guard posisi), /on (SOP penuh), /status (mode+equity+posisi), /ask (GLM Q&A)
- /learn (belajar mandiri), /learn off — verifikasi end-to-end 13-14 Sep.

## 1b. [SELESAI 13 Sep — dipindah ke done] Telegram alert dasar
- alert_open/close/system/digest sudah ada; tinggal kredensial di .env VPS
  (Nahkoda sudah pasang — Hermes verifikasi alert nyata ke HP).

## 1c. [13 Sep, DIPASANG] Narasi pasar (F&G + berita)
- core/sentiment.py: fear_greed() + headlines() cache 1 jam, 0 token.
- Digest memuat blok NARASI; dashboard /api/sentiment + panel.
- KEPUTUSAN: report-only selamanya sampai backtest membuktikan nilai.

## 5. [16 Sep, DIPASANG] Self-learning mode (belajar mandiri)
- core/learn.py: HNRSS search (10 topik berputar) → GLM summarize → jurnal MIND/PEMBELAJARAN.md.
- /learn on + /learn off di tg_control.py; cron tiap :20; 1 sesi/hari; 0 token per denyut.
- KEPUTUSAN: report-only — proposal masuk BACKLOG, butuh backtest n≥100/PF≥1.1/totR>0 + persetujuan Nahkoda.
- FIX: model reasoning butuh max_tokens=2000 untuk input panjang; retry 1x pada GLM kosong (router flaky).

## 3. [20 Sep] Evaluasi XRP
- XRP merah di dual-window (PF 0.56, -3.2R, MC p95 6.9).
- Keputusan Nahkoda 13 Sep: PERTAHANKAN selama demo week (gate melindungi,
  biaya ~nol). Evaluasi ulang dengan data minggu ini di WEEK-REPORT.

## 4. [Nanti, Tahap B] Saldo real di dashboard
- Field saldo_real sudah disiapkan (null). Aktif saat private key HL
  agent dipasang — JANGAN isi sebelum Nahkoda membuka Tahap B eksplisit.
