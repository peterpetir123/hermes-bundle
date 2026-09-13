## 2026-09-13 — Mode monitor 30-menit aktif + bug installer cron ditemukan & diperbaiki (oleh Hermes)
- Apa: git pull 0afdcae (mode --monitor: cek posisi 2x/jam, 0 token LLM, fetch hanya koin berposisi). Jalankan update_cron.sh -> TEMUAN: crontab jadi 7 entry (run_scan :05 dobel, digest dobel, watchdog dobel) — penyebab: installer menyaring entry lama dengan `grep -v HERMES` (case-sensitive) padahal entry lama tak memuat kata itu -> penyaringan gagal -> duplikasi. RISIKO: dua run_scan bersamaan tiap jam = double-entry saat TRIGGER.
- Keputusan: (a) crontab dirapikan manual ke tepat 4 entry kanonik (end-state yang diminta tugas); (b) patch 1 baris scripts/update_cron.sh: grep -v HERMES -> grep -viE 'hermes[-_]?(bundle|bot|env)|run_scan|watchdog' supaya installer idempoten. Keduanya di luar daftar DILARANG (bukan config/engine/sizing); dilakukan segera karena duplikat = risiko operasional nyata Demo Week. Nahkoda review patch di commit ini.
- Alasan: verifikasi tugas mensyaratkan "4 entry"; installer harus dipakai ulang tanpa menduplikat.
- Verifikasi (verbatim): uji manual `./hermes-env/bin/python -m hermes_bot.run_scan --monitor` -> "monitor: no open positions", EXIT=0. crontab final 4 entry (idempoten diuji jalankan installer 2x: tetap 4 entry, 0 duplikat):
  5 * * * * cd /root/hermes-bundle && /root/hermes-bundle/hermes-env/bin/python -m hermes_bot.run_scan >> log/cron.log 2>&1
  10,40 * * * * cd /root/hermes-bundle && /root/hermes-bundle/hermes-env/bin/python -m hermes_bot.run_scan --monitor >> log/cron.log 2>&1
  15 0 * * * cd /root/hermes-bundle && /root/hermes-bundle/hermes-env/bin/python -m hermes_bot.run_scan --digest >> log/cron.log 2>&1
  */30 * * * * cd /root/hermes-bundle && /root/hermes-bundle/hermes-env/bin/python -m hermes_bot.watchdog >> log/cron.log 2>&1
- Jadwal mesin kini: :05 sinyal/entry · :10 & :40 monitor posisi · 00:15 digest GLM · */30 watchdog. run_scan biasa tidak berubah; config/engine/sizing tidak disentuh.

## 2026-09-13 — Demo Week dimulai + tunnel systemd (oleh Hermes)
- Apa: git pull 9888ef5 (TUGAS-AKTIF demo week + BACKLOG dibaca, backlog TIDAK dikerjakan). Baseline config.yaml sha256 = 76a1c9a1d37bca6800c03caab122f7e9d1bd6d68e3564fec07bc22ac2d05d07e (hari pertama, untuk WEEK-REPORT). Item operasional Nahkoda: cloudflared dipindah dari background process ke systemd user unit `hermes-tunnel.service` (Restart=always, RestartSec=10, wrapper scripts/cloudflared-tunnel.sh menulis URL aktif ke log/tunnel.url tiap denyut tunnel).
- Keputusan: URL tunnel BARU = https://marc-moderator-tournament-utilize.trycloudflare.com (quick tunnel = URL berubah tiap restart; wrapper mencatat URL terkini otomatis). hermes-web-public dinyalakan kembali sebagai target tunnel (bind 0.0.0.0 tetap tak terjangkau langsung dari luar karena VPS di belakang NAT provider).
- Alasan: tugas Nahkoda #4 — tunnel harus hidup otomatis pasca reboot, URL terdokumentasi.
- Verifikasi: systemctl --user is-active hermes-tunnel = active (PID 21288); is-enabled = enabled; cat log/tunnel.url = URL di atas; curl via tunnel = 200; /api/state = 200. Baseline denyut: digest 2026-09-12 & 2026-09-13 terbit (log/digests/), denyut :05 & watchdog */30 jalan (cron.log), sinyal terakhir: BTC/ETH/SOL/XRP/DOGE BLOCKED_REGIME, polymarket n/a (API gagal — diabaikan, bukan error sistem).

## 2026-09-13 — Akses dashboard Nahkoda via Cloudflare quick tunnel (permintaan Nahkoda) (oleh Hermes)
- Apa: Nahkoda menolak SSH tunnel (keseluruhan percobaan gagal) dan minta cara lain. Terpasang cloudflared (apt deb 2026.9.1) dan quick tunnel aktif: `cloudflared tunnel --url http://127.0.0.1:8080 --no-autoupdate` -> https://stakeholders-starring-items-quest.trycloudflare.com — curl dari VPS: 200.
- Keputusan: quick tunnel = ekspos tanpa auth ke internet (siapa pun yang tahu URL bisa buka, walau URL acak dan sementara). Diterima karena permintaan eksplisit Nahkoda & dashboard read-only tanpa kredensial. Alternatif permanen = named tunnel + Cloudflare Access (butuh akun Cloudflare) — catat untuk Nahkoda bila mau URL tetap + proteksi login.
- Alasan: provider NAT tidak menyediakan port publik; SSH tunnel ditolak Nahkoda; tunnel keluar (outbound QUIC) tidak butuh port masuk.
- Verifikasi: cloudflared --version = 2026.9.1; log: "Your quick Tunnel has been created! Visit it at https://stakeholders-starring-items-quest.trycloudflare.com"; curl -o /dev/null -w %{http_code} -> 200. Catatan: URL berubah tiap restart cloudflared; proses berjalan sebagai background process, belum systemd.

## 2026-09-12 — Opsi A DITUTUP: VPS di belakang NAT provider, port publik tak tersedia (oleh Hermes)
- Apa: Diagnostik akhir — VPS hanya pegang IP privat 10.60.107.202; 156.67.24.112 = gateway provider Helipod yang memetakan SEBAGIAN port saja (22, 80, 443, dan 49500->22 terbukti; 8080/8888/49501 refused di gateway, dibuktikan via check-host.net dari 3 node + probe listener lokal). Artinya dashboard di 0.0.0.0:8080 TIDAK AKAN PERNAH terjangkau dari luar di arsitektur ini, apa pun iptables-nya.
- Keputusan: opsi A (allowlist IP) dihentikan karena tujuan tak tercapai; rules iptables HERMES-WEB dipertahankan (tak berbahaya) tapi akses Nahkoda kembali via SSH tunnel: `ssh -N -L 8080:127.0.0.1:8080 root@156.67.24.112 -p 49500` lalu browser http://127.0.0.1:8080. Unit hermes-web-public tetap jalan (dipakai tunnel juga bisa; bind 0.0.0.0 tak terjangkau luar).
- Alasan: provider tidak menyewakan port publik tambahan; satu-satunya jalur masuk yang terbukti hidup = SSH di port 49500.
- Verbatim bukti: check-host 80/443 = {"time":0.115,"address":"156.67.24.112"} OK; 8080 = {"error":"Connection refused"}; 49501 = refused/timeout; probe listener lokal 49501 = tak ada koneksi datang; sshd auth = "Accepted password for root from 180.252.118.92" via -p 49500.

# SESSION-LOG Hermes — Memori Antar-Sesi

> Aturan: SETIAKAR akhir sesi, append entri baru di ATAS, lalu commit+push.
> Format: tanggal | apa yang dikerjakan | keputusan+alasan | bukti verifikasi.

## 2026-09-12 — Opsi A Nahkoda: dashboard dibuka terbatas ke IP rumah (by-request) (oleh Hermes)
- Apa: SSH password dari IP Nahkoda (180.247.60.170) sebenarnya BERHASIL di auth.log tapi tunnel tetap tak terpakai — Nahkoda pilih Opsi A: listener kedua di 0.0.0.0:8080 via unit `hermes-web-public` (Environment HERMES_WEB_BIND), dilindungi iptables chain `HERMES-WEB` (allow 127.0.0.1 + 180.247.60.170, DROP sisanya). Rules disimpan /etc/iptables/rules.v4 + unit oneshot `hermes-iptables-restore.service` enabled untuk persist reboot. server.py default TETAP 127.0.0.1 (commit ea27e4f->eb267e8).
- Keputusan: ini pembukaan sementara atas keputusan "local-only" atas permintaan eksplisit Nahkoda; unit lama hermes-web (127.0.0.1) di-disable dan digantikan instance publik yang sama isinya. Pembatalan = `systemctl --user stop --now hermes-web-public` + `iptables -D INPUT -p tcp --dport 8080 -m conntrack --ctstate NEW -j HERMES-WEB`.
- Alasan: Nahkoda tak bisa akses via tunnel; firewall allowlist membatasi permukaan serangan ke 1 IP.
- Verifikasi: `ss -tlnp` -> 0.0.0.0:8080 (pid python); `curl 127.0.0.1:8080/` -> 200; iptables HERMES-WEB = [accept loopback, accept 180.247.60.170, drop all]. Akses dari browser Nahkoda: http://156.67.24.112:8080 — CATATAN: verifikasi dari luar VPS belum bisa dilakukan dari dalam (hairpin NAT 000), perlu konfirmasi Nahkoda.

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
