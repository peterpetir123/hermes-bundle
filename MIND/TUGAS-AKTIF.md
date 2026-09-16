# TUGAS AKTIF Hermes — Watch-Queue (ETA adaptif) verifikasi (14 Sep)

> Demo Week tetap berjalan. Setelah selesai & terverifikasi: hapus file
> ini, catat di SESSION-LOG.

1. cd ~/hermes-bundle && git pull  (harus dapat commit watchqueue)
   Baca MIND/KEPUTUSAN.md entri watch-queue: REPORT-ONLY, ETA = estimasi
   prioritas perhatian BUKAN janji. Tidak menyentuh eksekusi.

2. RESTART web: systemctl --user restart hermes-web
   Uji: curl -s 127.0.0.1:8080/api/watchqueue  (awalnya [] — normal)

3. UJI MODUL: ./hermes-env/bin/python -m hermes_bot.core.watchqueue
   Harus cetak "watchqueue smoke PASS".

4. DENYUT :05 BERIKUTNYA: ./hermes-env/bin/python -m hermes_bot.run_scan
   - output denyut kini berisi baris "watchqueue: BTC 2.3h(mendekat), ..."
   - curl -s 127.0.0.1:8080/api/watchqueue | head -c 300 -> JSON per koin
   - denyut TETAP 0 token tambahan (watchqueue tidak manggil GLM)

5. Denyut berikutnya lagi: ETA koin harus BERUBAH (adaptif dari history
   cache/dist_history.json) — trend berubah menjauh/mendekat sesuai
   pergerakan. Laporkan dua baris watchqueue berturut-turut verbatim.

6. DASHBOARD: panel "Watch-Queue" tampil (tabel Koin/Jarak/ETA/Arah,
   warna: hijau mendekat, merah menjauh, kuning datar).

7. PENUTUP: append SESSION-LOG (bukti verbatim langkah 3-6), commit+push,
   hapus TUGAS-AKTIF.md ini.

DILARANG: ubah config.yaml, engine, sizing, logika entry; watchqueue
BOLEH tampil di denyut/digest tapi TIDAK BOLEH memicu entry apa pun.
Jika error -> laporkan verbatim, JANGAN patch sendiri.
