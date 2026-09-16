# KEPUTUSAN Hermes — Keputusan Penting + Alasan

> Hanya keputusan berdampak (parameter, arsitektur, gerbang). Fakta harian masuk SESSION-LOG.

| Tanggal | Keputusan | Alasan | Sumber Otoritas |
|---|---|---|---|
| 2026-09-16 | REVISI klausa 2026-09-13 "report-only SELAMANYA": narasi (F&G) boleh MEMODULASI ketatan trigger DON (bukan membuka entry), HANYA setelah varian menang backtest vs BASE (gerbang: totR pooled > BASE, PF >= BASE, MC p95 tidak memburuk, n >= 80% BASE). Dua varian diadu: CONF2 (2 close konfirmasi saat F&G<25) vs BUF (buffer 0.5 ATR saat F&G<25, 0.3 saat 25-44). Pemenang diputuskan data; seri/gagal = status quo. TANPA level harga manual (soal BTC 82k ditolak — konfirmasi ketat membuat entry efektif menunggu lebih rendah secara alami) | arahan Nahkoda: "trigger adaptif dari narasi, keputusan diolah data kuantitatif" | Nahkoda |
| 2026-09-16 | Self-learning mode: `/learn` = on, `/learn off` = off; 1 sesi/hari via cron, sumber dari internet (HNRSS, 10 topik berputar) → jurnal MIND/PEMBELAJARAN.md; usulan inovasi → MIND/BACKLOG.md dengan syarat bukti (backtest n≥100/PF≥1.1/totR>0) + persetujuan Nahkoda | belajar mandiri tanpa membeli beban modal; report-only untuk parameter/engine/sizing — tidak pernah auto-apply | Nahkoda |
| 2026-09-16 | Tambah DeepSeek v4.1 Flash ke model pool (glm_client MODELS); default tetap glm-5.3-flash, deepseek bisa dipanggil via `model="deepseek-v4.1-flash"` | DeepSeek didukung router juan.web.id, terverifikasi; memberi opsi comparison GLM vs DeepSeek dalam satu tempat tanpa ubah infrastruktur | Nahkoda |
| 2026-09-14 | Watch-Queue Protocol: ETA adaptif (kecepatan dist_atr antar denyut) + fallback 1 ATR/hari, ranking terdekat dulu, REPORT-ONLY — tidak pernah gate eksekusi | permintaan Nahkoda ("koin A 3 hari lagi, cari yang lebih cepat"); ETA = estimasi prioritas perhatian, BUKAN janji harga | Nahkoda |
| 2026-09-13 | Narasi (Fear&Greed + RSS berita) masuk digest + dashboard, REPORT-ONLY SELAMANYA hingga ada backtest yang membuktikan nilai prediktifnya | pelajaran M15: 24.560 trade negatif — menambah sinyal tanpa bukti = membakar modal; narasi tidak pernah gate eksekusi | Nahkoda + vault §7 |
| 2026-09-13 | Cache sentimen/berita 1 jam (cache/fng.json, cache/news.json) | denyut tiap 30 mnt tidak boleh boros API; digest 1x/hari yang merangkum via GLM | efisiensi token |
| 2026-09-13 | Telegram kontrol /stop /on /status = /stop hanya touch KILL (bukan kill proses) | denyut tetap jalan (data tercatat), hanya eksekusi entry dibekukan; mekanisme KILL sudah ada di risk.py | desain minimal |
| 2026-09-12 | Tafsir gerbang backtest: n≥100 didesain utk 20 aset × 9 thn; utk 5 aset × ~6 thn, n=8–13/asets = WAJAR. Kolom FAIL per-aset = informatif, BUKAN pemblokir. Kriteria keputusan aset = arah totR + PF + MC p95 | gerbang baku tidak boleh dibongkar; tafsir konteks = wewenang Nahkoda | Nahkoda 2026-09-12 |
| 2026-09-12 | 4/5 aset lolos tafsir (BTC/ETH/SOL/DOGE: totR positif, PF>2). XRP merah di kedua window (PF 0.56, -3.2R, MC p95 6.9) | bukti dual-window reproducible lintas mesin | SUMMARY.md ec2903e |
| 2026-09-12 | Semua fase 0–3 dinyatakan SELESAI & TERVERIFIKASI -> TUGAS-AKTIF.md dihapus sesuai aturannya | laporan Hermes verbatim + reproducible + engine/config tak tersentuh | Nahkoda 2026-09-12 |
| 2026-09-11 | Backtest engine memanggil modul core ASLI | duplikasi logika = backtest berbohong | protokol vault §7 |
| 2026-09-11 | R-multiple dari SL awal, bukan SL trailing | definisi R baku; trailing mengubah exit, bukan risiko awal | Referensi-Probabilitas.md |
| 2026-09-11 | MC 1000 shuffle, sizing lihat p95 | satu backtest = satu urutan | Referensi-Probabilitas.md §6 |
| 2026-09-11 | Dashboard bind 127.0.0.1 saja | local-only, nol permukaan serangan | keputusan Nahkoda |
| 2026-09-11 | Saldo real = n/a hingga Tahap B | testnet dulu; tidak ada key HL di VPS | protokol vault |
