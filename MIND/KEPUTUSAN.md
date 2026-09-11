# KEPUTUSAN Hermes — Keputusan Penting + Alasan

> Hanya keputusan berdampak (parameter, arsitektur, gerbang). Fakta harian masuk SESSION-LOG.

| Tanggal | Keputusan | Alasan | Sumber Otoritas |
|---|---|---|---|
| 2026-09-11 | Backtest engine memanggil modul core ASLI | duplikasi logika = backtest berbohong | protokol vault §7 |
| 2026-09-11 | R-multiple dari SL awal, bukan SL trailing | definisi R baku; trailing mengubah exit, bukan risiko awal | Referensi-Probabilitas.md |
| 2026-09-11 | MC 1000 shuffle, sizing lihat p95 | satu backtest = satu urutan | Referensi-Probabilitas.md §6 |
| 2026-09-11 | Dashboard bind 127.0.0.1 saja | local-only, nol permukaan serangan | keputusan Nahkoda |
| 2026-09-11 | Saldo real = n/a hingga Tahap B | testnet dulu; tidak ada key HL di VPS | protokol vault |
