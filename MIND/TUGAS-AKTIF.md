# TUGAS AKTIF Hermes — Self-Learn + DeepSeek verifikasi (16 Sep)

> Demo Week tetap berjalan. Setelah selesai & terverifikasi: hapus file
> ini, catat di SESSION-LOG.

## A. Self-Learning Module

1. cd ~/hermes-bundle && git pull
   Baca MIND/KEPUTUSAN.md entri self-learning: REPORT-ONLY, proposal masuk
   BACKLOG, butuh backtest + persetujuan Nahkoda.

2. UJI MODUL OFFLINE: ./hermes-env/bin/python -m hermes_bot.core.learn
   Harus cetak "learn smoke PASS (offline)".

3. UJI MODUL LIVE (with flag):
   touch LEARN
   ./hermes-env/bin/python -m hermes_bot.core.learn --run
   - Harus mengembalikan balasan GLM tentang 1 artikel dari internet.
   - Periksa MIND/PEMBELAJARAN.md — harus ada entry baru.
   - Cegah dobel sesi: jalankan lagi — harus balas "sudah jalan, besok lagi".
   rm LEARN cache/learn_last.json

4. UJI TELEGRAM: kirim /learn di Telegram
   - Hermes harus aktifkan LEARN + langsung jalankan sesi pertama.
   - /status harus tampilkan "mode belajar: AKTIF (1 sesi/hari)".
   - /learn off harus matikan mode.
   - /status harus tampilkan "mode belajar: mati".

5. CRON: pastikan cron entry ":20 * * * * learn" ada di crontab.

## B. DeepSeek v4.1 Flash

6. UJI MODEL: ./hermes-env/bin/python -c "
import sys; sys.path.insert(0,'.'); import os
for line in open('.env'):
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        k,v=line.split('=',1); os.environ.setdefault(k.strip(), v.strip())
from hermes_bot.report.glm_client import chat
print(chat([{'role':'user','content':'balas: siap'}], model='deepseek-v4.1-flash'))
"
   Harus cetak "siap" atau jawaban (bukan GLM_ERROR).

7. PENUTUP: append SESSION-LOG (bukti verbatim langkah 2-6), commit+push,
   hapus TUGAS-AKTIF.md ini.

DILARANG: ubah config.yaml, engine, sizing, logika entry; belajar TIDAK
pernah mengubah mesin tanpa backtest + persetujuan Nahkoda.
Jika error -> laporkan verbatim, JANGAN patch sendiri.
