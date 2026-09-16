# TUGAS AKTIF Hermes — Watch-Queue + Self-Learn verifikasi (16 Sep)

> Demo Week tetap berjalan. Setelah selesai & terverifikasi: hapus file
> ini, catat di SESSION-LOG.
> Jika error -> laporkan verbatim, JANGAN patch sendiri.

## A. GIT PULL (WAJIB DULU)

cd ~/hermes-bundle && git pull origin main
Harus dapat commit 3ad0fea (fix learn.py) — yang juga membawa 270525a
(watchqueue) dan a05230a (learn + /learn).

## B. VERIFIKASI WATCH-QUEUE (commit 270525a)

1. RESTART web: systemctl --user restart hermes-web
   Uji: curl -s 127.0.0.1:8080/api/watchqueue  (awalnya [] — normal)

2. UJI MODUL: ./hermes-env/bin/python -m hermes_bot.core.watchqueue
   Harus cetak "watchqueue smoke PASS".

3. DENYUT :05 BERIKUTNYA: ./hermes-env/bin/python -m hermes_bot.run_scan
   - output denyut berisi baris "watchqueue: BTC 2.3h(mendekat), ..."
   - curl -s 127.0.0.1:8080/api/watchqueue | head -c 300 -> JSON per koin
   - denyut TETAP 0 token tambahan (watchqueue tidak manggil GLM)

4. Denyut berikutnya lagi: ETA koin harus BERUBAH (adaptif dari
   cache/dist_history.json). Laporkan dua baris watchqueue berturut-turut
   verbatim.

5. DASHBOARD: panel "Watch-Queue" tampil (Koin/Jarak/ETA/Arah; hijau
   mendekat, merah menjauh, kuning datar).

## C. VERIFIKASI SELF-LEARN (commit 3ad0fea)

1. UJI OFFLINE: ./hermes-env/bin/python -m hermes_bot.core.learn
   Harus cetak "learn smoke PASS (offline)".

2. UJI LIVE:
   touch LEARN
   ./hermes-env/bin/python -m hermes_bot.core.learn --run
   - Normal: "🎓 sesi belajar selesai" + 1 artikel HNRSS dirangkum.
   - Cek MIND/PEMBELAJARAN.md -> entry baru.
   - Jika "learn: gagal (...)" -> laporkan verbatim, lanjut langkah 3
     (gagal hanya memblokir 1 jam, bukan 24 jam).
   rm cache/learn_last.json  (reset agar uji Telegram bisa jalan)

3. UJI TELEGRAM:
   - /learn -> mode aktif + sesi pertama langsung jalan.
   - /status -> baris "mode belajar: 🎓 AKTIF (1 sesi/hari)".
   - /learn off -> mode mati, jurnal tetap ada.
   - /status -> "mode belajar: mati (/learn)".
   - rm LEARN  (flag bersih — cron :20 tidak boleh jalan saat off)

4. UJI CRON:
   crontab -l | grep learn
   Harus ada ":20 * * * * ... hermes_bot.core.learn ..."
   (belum ada? jalankan bash scripts/update_cron.sh lalu cek lagi)

## D. PENUTUP

1. Append MIND/SESSION-LOG.md (pola entri 2026-09-15): Apa / Keputusan /
   Alasan / Verifikasi verbatim (langkah B.2-B.5 dan C.1-C.4).
2. git add -A && git commit -m "verify: watchqueue + self-learn lulus" \
   && git push origin main
3. rm MIND/TUGAS-AKTIF.md ini.

DILARANG: ubah config.yaml, engine, sizing, logika entry. Watch-queue dan
learn = REPORT-ONLY; usulan learn hanya masuk BACKLOG menunggu bukti
(backtest n>=100/PF>=1.1/totR>0) + persetujuan Nahkoda.
