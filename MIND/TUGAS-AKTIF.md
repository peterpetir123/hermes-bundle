# TUGAS AKTIF Hermes — Telegram aktif + Verifikasi Narasi (13 Sep)

> Demo Week tetap berjalan (tugas sebelumnya). Tugas ini PENAMBAHAN.
> Setelah selesai & terverifikasi: hapus file ini, catat di SESSION-LOG.

=== TAHAP 1: TELEGRAM (prioritas) ===
1. Nahkoda sudah mengisi TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID di .env.
   Verifikasi: grep -c "TELEGRAM" .env (harus 2 baris terisi, JANGAN
   tampilkan nilainya di log/laporan, JANGAN commit .env).
2. Uji kirim nyata:
   ./hermes-env/bin/python -c "
   import sys; sys.path.insert(0,'.')
   from hermes_bot.notify.telegram_bot import alert_system
   print('terkirim:', alert_system('tes koneksi Telegram — Hermes aktif'))"
   -> harus True DAN Nahkoda menerima pesan di HP.
3. Catat di SESSION-LOG: timestamp + hasil True/False. Jangan catat token.

=== TAHAP 2: FITUR NARASI (dari upstream, commit ini) ===
1. Baca MIND/KEPUTUSAN.md dulu: narasi = REPORT-ONLY SELAMANYA.
2. Verifikasi denyut :05 berikutnya:
   - cache/fng.json + cache/news.json terisi (ls -la cache/)
   - curl -s 127.0.0.1:8080/api/sentiment | head -c 200 -> JSON fng+news
   - Dashboard (via tunnel) menampilkan badge F&G + panel BERITA 24J
3. Verifikasi digest 00:15 malam ini:
   - TERKIRIM ke Telegram Nahkoda (bukan cuma file)
   - berisi blok NARASI (fear_greed + berita) dirangkum GLM
   - tersimpan di log/digests/

=== ATURAN ===
- Jika fetch F&G/RSS gagal di VPS: jangan patch — fallback kosong adalah
  perilaku benar; laporkan error verbatim.
- DILARANG: ubah config/engine/sizing/logika entry, commit kredensial,
  ubah bind dashboard, kerjakan BACKLOG /stop /on (tunggu tugas eksplisit).
- Append SESSION-LOG + commit + push tiap penyelesaian tahap.
- Langkah ambigu -> BERHENTI, laporkan, tunggu Nahkoda.
