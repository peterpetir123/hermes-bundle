# TUGAS AKTIF Hermes — DEMO WEEK (Tahap A smoke)

> Ditetapkan Nahkoda 2026-09-13. Periode: 2026-09-13 -> 2026-09-20.
> Tujuan minggu ini = uji OPERASIONAL (denyut hidup 24/7, nol error, log rapi,
> digest terbit, entry tercatat benar) — BUKAN membuktikan profit.
> Strategi D1 lambat: 0-2 entry dalam seminggu = NORMAL, nol entry pun bukan
> kegagalan selama denyut & log sehat.

=== RUTIN HARIAN (cron sudah jalan — JANGAN diubah) ===
- Denyut per jam (:05), digest harian (00:15), watchdog (*/30) — biarkan.
- Tugasmu TAMBAHAN:
  a. Tiap hari 00:15 (selepas digest): append MIND/SESSION-LOG.md dengan
     ringkasan 1 hari:
     - jumlah denyut tercatat (dari log/last_scan.json mtime history/cron.log)
     - sinyal per aset (regime/status)
     - entry/close jika ada — dua-track (SINYAL-SISTEM + KEPUTUSAN-NAHKODA)
     - error/alarm yang muncul
     - uptime denyut hari itu (denyut tercatat / 24)
  b. Commit + push harian: "mind: demo-day <tanggal>".
  c. Setiap TRIGGER -> pastikan entry testnet tercatat di state + baris
     Signal-Log dua track ditulis.
- DILARANG: ubah config.yaml/sizing/watchlist, isi kredensial, jalankan
  setup_vps.sh, ubah bind dashboard. Keputusan = Nahkoda.

=== LAPORAN AKHIR: 2026-09-20 ===
Buat MIND/WEEK-REPORT.md berisi:
1. Uptime % seminggu (total denyut tercatat / 168)
2. Jumlah sinyal per aset + jumlah trade (open/closed)
3. Daftar error/alarm + penanganannya
4. sha256sum config.yaml hari pertama vs terakhir (HARUS identik)
5. Ekuitas demo akhir vs awal
Commit + push, lalu lapor ke Nahkoda. Hapus TUGAS-AKTIF.md ini HANYA
setelah WEEK-REPORT.md ter-push.

=== CATATAN ===
- BACKLOG (Telegram alert + kontrol /stop /on /status) lihat MIND/BACKLOG.md
  — JANGAN kerjakan sekarang; tunggu tugas eksplisit Nahkoda.
- Langkah ambigu / error tak dipahami -> BERHENTI, laporkan, tunggu.
