# SESSION-LOG Hermes — Memori Antar-Sesi

> Aturan: SETIAKAR akhir sesi, append entri baru di ATAS, lalu commit+push.
> Format: tanggal | apa yang dikerjakan | keputusan+alasan | bukti verifikasi.

## 2026-09-12 — Fase 3-lanjutan dieksekusi (patch upstream afc00f7 dipakai apa adanya) (oleh Hermes)
- Apa: git pull -> afc00f7 + ac113f5 hadir. Baca ulang TUGAS-AKTIF "FASE 3-LANJUTAN". Jalankan `run_backtest --all` dengan data.py hasil patch Nahkoda (startTime-paging). Hasil masuk backtest_results/ (5 JSON + SUMMARY.md). Engine, config, sizing, watchlist, dashboard: TIDAK disentuh.
- Keputusan: report-only sesuai instruksi — TIDAK menafsirkan hasil sebagai dasar ubah sizing/watchlist; TUGAS-AKTIF.md TIDAK dihapus (Nahkoda akan menilai SUMMARY.md dulu). Akar masalah hasil lama (n=1..3) = bug upstream data.py, bukan engine/strategi.
- Alasan: instruksi verbatim Nahkoda (2026-09-12); FULL window = maks historis venue (HL ~6 thn) — opsi provider eksternal DITOLAK Nahkoda.
- Verifikasi (verbatim): "BTC: full n=10 PF=2.05 totR=3.9 | 3y n=9 PF=1.998 totR=3.7 / ETH: full n=10 PF=2.167 totR=3.5 | 3y n=8 PF=4.264 totR=5.0 / SOL: full n=9 PF=5.085 totR=10.4 | 3y n=9 PF=5.085 totR=10.4 / XRP: full n=13 PF=0.563 totR=-3.2 | 3y n=13 PF=0.563 totR=-3.2 / DOGE: full n=11 PF=3.825 totR=10.1 | 3y n=10 PF=4.495 totR=10.7 / SUMMARY -> backtest_results/SUMMARY.md". Data terverifikasi: cache = BTC 2217 bar [2020-08-19..2026-09-12], ETH 2216, SOL 2191 [2020-09-14..], XRP 2183 [2020-09-21..], DOGE 2216 — cocok dengan diagnostik sesi sebelumnya. MC p95: BTC 3.6, ETH 2.8, DOGE 3.6, XRP 6.9 (SOL n<10 -> MC tidak jalan, sesuai guard report.py).

## 2026-09-12 — Eksekusi TUGAS-AKTIF Fase 0-2 selesai; Fase 3 berjalan tapi butuh keputusan data (oleh Hermes)
- Apa: Fase 0 (sinkron ke 89417d2, semua commit hadir) ✓; Fase 1 (cron 3 entry ✓, last_scan 02:05 UTC <2jam ✓, watchdog OK ✓, state.json.bak kini tercipta oleh denyut 03:05 dengan kode a577c15 ✓) ✓; Fase 2 (hermes_bot/web/server.py + index.html, bind 127.0.0.1:8080, systemd user unit hermes-web active+enabled, linger on, curl 200 + saldo_real:null ✓) ✓; Fase 3 (run_backtest --all dieksekusi, hasil FAIL semua aset — n=1..3, data cuma 401 bar per aset).
- Keputusan: (a) TIDAK mengubah core/data.py/backtest engine — wewenang terbatas; (b) backtest_results/SUMMARY.md ditandai "window 9y penuh terbatas data" supaya tidak menyesatkan; (c) Fase 3 dinyatakan BLOKIR data, tunggu Nahkoda (opsi: a2/funding/paginated HL, OKX candles 1440-bar, atau turunkan ekspektasi window); (d) TUGAS-AKTIF.md TIDAK dihapus (belum semua fase selesai terverifikasi).
- Alasan: (a) protokol — langkah ambigu -> BERHENTI, laporkan; (b) jujur pada gerbang n>=100; (c) faktanya API tidak menyediakan 9y; (d) aturan tugas baris 5.
- Verifikasi: crontab -l = 3 entry sesuai spek; syslog CRON fire 02:05:01/02:30 UTC; `watchdog OK` (exit 0); ls -la state/ -> state.json + state.json.bak @03:05; curl -s 127.0.0.1:8080/api/state -> {"positions": [], "closed": [], "equity": 20.0, ..., "saldo_real": null}; curl -s -o /dev/null -w "%{http_code}" 127.0.0.1:8080/ -> 200; systemctl --user is-active hermes-web -> active; run_backtest --all verbatim: "BTC: 9y n=1 PF=inf totR=1.9 | 3y n=1 ... / DOGE: 9y n=1 PF=0.0 totR=-0.7 | 3y ..." (semua FAIL, gate n>=100); git push 89417d2..0f67cb3 (exit 0).
- Bukti diagnostik Fase 3: HL candleSnapshot(startTime) = 2216 bar BTC [2020-08-19..2026-09-12, gap-free]; OKX history-candles 10 halaman = 1000 bar [2023-12-17..]; data.py di HEAD (89417d2) TIDAK punya startTime padahal API sekarang mewajibkannya (di VPS HL API mengembalikan hanya 400 bar default saat startTime span 400 hari) — dari sisi Hermes, itu titik yang perlu keputusan Nahkoda; polymarket.py perlu paging offset untuk pasar koin (terlihat dari cron.log yang tetap menampilkan BTC/ETH).

## 2026-09-11 — Inisialisasi MIND (oleh Nahkoda via opencode)
- Apa: skeleton backtest/ (engine+report+CLI) + hardening (backup state, watchdog alarm) di-push upstream.
- Keputusan: engine backtest WAJIB memanggil scan_don() asli — dilarang menyalin logika; R dihitung dari SL awal (bukan SL trailing); biaya fee 0.045% + slip 0.05%/sisi; dual-window 9y+3y.
- Alasan: satu sumber kebenaran; hasil backtest yang bohong = keputusan yang bohong.
- Verifikasi: smoke test sintetis PASS (3 trade, R terhitung, MC guard n<10 jalan).
