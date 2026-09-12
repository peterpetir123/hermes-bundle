# KEPUTUSAN Hermes — Keputusan Penting + Alasan

> Hanya keputusan berdampak (parameter, arsitektur, gerbang). Fakta harian masuk SESSION-LOG.

| Tanggal | Keputusan | Alasan | Sumber Otoritas |
|---|---|---|---|
| 2026-09-12 | Tafsir gerbang backtest: n≥100 didesain utk 20 aset × 9 thn; utk 5 aset × ~6 thn, n=8–13/asets = WAJAR. Kolom FAIL per-aset = informatif, BUKAN pemblokir. Kriteria keputusan aset = arah totR + PF + MC p95 | gerbang baku tidak boleh dibongkar; tafsir konteks = wewenang Nahkoda | Nahkoda 2026-09-12 |
| 2026-09-12 | 4/5 aset lolos tafsir (BTC/ETH/SOL/DOGE: totR positif, PF>2). XRP merah di kedua window (PF 0.56, -3.2R, MC p95 6.9) | bukti dual-window reproducible lintas mesin | SUMMARY.md ec2903e |
| 2026-09-12 | Semua fase 0–3 dinyatakan SELESAI & TERVERIFIKASI -> TUGAS-AKTIF.md dihapus sesuai aturannya | laporan Hermes verbatim + reproducible + engine/config tak tersentuh | Nahkoda 2026-09-12 |
| 2026-09-11 | Backtest engine memanggil modul core ASLI | duplikasi logika = backtest berbohong | protokol vault §7 |
| 2026-09-11 | R-multiple dari SL awal, bukan SL trailing | definisi R baku; trailing mengubah exit, bukan risiko awal | Referensi-Probabilitas.md |
| 2026-09-11 | MC 1000 shuffle, sizing lihat p95 | satu backtest = satu urutan | Referensi-Probabilitas.md §6 |
| 2026-09-11 | Dashboard bind 127.0.0.1 saja | local-only, nol permukaan serangan | keputusan Nahkoda |
| 2026-09-11 | Saldo real = n/a hingga Tahap B | testnet dulu; tidak ada key HL di VPS | protokol vault |
