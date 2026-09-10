==================================================================
REFERENSI PERHITUNGAN PELUANG (PROBABILITY) UNTUK TRADING
Disusun untuk keperluan training AI trading
Tanggal riset: 10 September 2026
Sumber: riset Nahkoda (verbatim) — diadopsi sebagai konstitusi Hermes
==================================================================

CATATAN PENTING SEBELUM MEMBACA:
File ini adalah rangkuman konsep dan formula matematis yang sudah
mapan (established) di dunia trading/quant. Semua formula bersifat
matematis dan dapat diverifikasi langsung dengan kalkulasi manual.
Bagian yang berupa opini/rule-of-thumb industri (misal "gunakan
setengah Kelly") ditandai sebagai praktik umum, bukan hukum pasti.

==================================================================
BAGIAN 1 — KONSEP DASAR PROBABILITAS DALAM TRADING
==================================================================

1.1 Random Walk Theory
Teori yang menyatakan pergerakan harga aset punya distribusi yang
sama dan independen dari waktu ke waktu — sehingga secara teori
sulit memprediksi harga masa depan murni dari pola harga masa lalu.
Relevansi untuk AI: jangan overfit model hanya berdasarkan pola
historis harga tanpa mempertimbangkan noise/randomness.

1.2 Law of Large Numbers (Hukum Bilangan Besar)
Semakin banyak jumlah trial/sampel (trade), hasil aktual akan makin
mendekati nilai ekspektasi (expected value) yang sebenarnya. Artinya
win rate dari 10 trade nyaris tidak bermakna secara statistik;
win rate baru mulai stabil setelah puluhan-ratusan trade.

1.3 Bayesian Probability (Probabilitas Bayesian)
Metode untuk memperbarui estimasi probabilitas suatu kejadian
seiring munculnya data/informasi baru. Sangat relevan untuk AI
trading yang terus belajar dari data real-time (narrative baru,
volume, sentimen sosial media, dsb).

1.4 Monte Carlo Simulation
Teknik komputasi yang menggunakan random sampling berulang kali
(ribuan iterasi) untuk mengestimasi distribusi hasil yang mungkin
terjadi, walau sistem yang disimulasikan sebenarnya deterministik.
Dipakai untuk menguji ketahanan strategi terhadap urutan trade yang
berbeda-beda (bukan cuma satu jalur backtest).

==================================================================
BAGIAN 2 — WIN RATE, RISK/REWARD, DAN EXPECTANCY
==================================================================

2.1 Win Rate (W)
  W = (jumlah trade menang) / (total trade)

2.2 Risk/Reward Ratio (R)
  R = (rata-rata profit trade menang) / (rata-rata rugi trade kalah)

2.3 Expectancy (Ekspektasi Matematis per Trade)
  Expectancy = (W x Avg_Win) - ((1 - W) x Avg_Loss)

Contoh: W=40%, AvgWin=$200, AvgLoss=$100 (R=1:2) → E = 0.4*200 - 0.6*100
= +$20/trade. Win rate tinggi TIDAK WAJIB untuk profitable — yang
penting expectancy > 0.

==================================================================
BAGIAN 3 — KELLY CRITERION (POSITION SIZING OPTIMAL)
==================================================================

3.1 Formula Dasar (Kelly Jr. 1956, akar teori Shannon)
  Kelly % = W - [(1 - W) / R]
  Bentuk biner klasik: f* = (bp - q) / b
    b = payoff ratio, p = P(menang), q = 1 - p
  Maksimalkan E[log(Wealth)] — pertumbuhan geometris jangka panjang.

3.2 Contoh
  WR 55%, avg win $312, avg loss $208 → R = 1.50
  f* = (1.5*0.55 - 0.45)/1.5 = 0.25 → Full Kelly = 25% modal/trade

3.3 Fractional Kelly (praktik umum industri)
  - Half Kelly: ~75% growth optimal, drawdown jauh lebih kecil
  - Quarter Kelly: ~50% growth optimal, paling konservatif
  Mayoritas profesional memakai half-Kelly atau lebih kecil.

3.4 Keterbatasan
  - Asumsi independen; posisi berkorelasi (BTC+altcoin) dihitung dari
    eksposur gabungan.
  - Kelly negatif = expectancy negatif = BERHENTI, bukan naikkan size.
  - Butuh 50-100 trade closed; error WR 5 poin bisa mengubah Kelly 3x.

==================================================================
BAGIAN 4 — RISK OF RUIN (PROBABILITAS "AKUN JEBOL")
==================================================================

4.1 Kasus win/loss sama besar:
  RoR = ((1 - Edge) / (1 + Edge)) ^ CapitalUnits,  Edge = W - L

4.2 Dengan Risk/Reward:
  RoR = (LossRate / (WinRate x R:R)) ^ (Threshold / RiskPerTrade)

4.3 Insight kunci
  - Position sizing = pengungkit terbesar RoR (bukan win rate);
    hubungan sizing-RoR EKSPONENSIAL (2x size bisa 10x+ RoR).
  - Firma profesional mensyaratkan RoR < 1% sebelum alokasi modal.
  - Definisi "ruin" harus eksplisit (50% DD? 10% prop-rule?).

4.4 Losing streak (W=50%, stake sama): P(5 kalah beruntun) = 0.5^5 = 3.125%.

==================================================================
BAGIAN 5 — BAYESIAN UPDATING
==================================================================

5.1  P(A|D) = [P(D|A) x P(A)] / P(D)
5.2  Posterior update-1 menjadi prior update-2, dst.
5.3  Bentuk odds (praktis, P(D) tereliminasi):
       Posterior Odds = Bayes Factor x Prior Odds
5.4  BASE RATE FALLACY: sinyal "akurasi 80%" di backtest TIDAK otomatis
     80% benar live jika base rate skenarionya jarang. Selalu pertanyaan:
     seberapa sering kondisi ini muncul sama sekali?

==================================================================
BAGIAN 6 — MONTE CARLO UNTUK VALIDASI STRATEGI
==================================================================
Satu backtest = SATU urutan. Acak ulang urutan trade (nilai tetap)
1.000+ iterasi → distribusi maxDD p95/p99, RoR riil, recovery time.
Jika backtest maxDD 12% tapi MC-p95 = 28% → sizing live pakai 28%.

==================================================================
BAGIAN 7 — SIGNIFIKANSI STATISTIK & UKURAN SAMPEL
==================================================================
- 10 trade: WR 60% = bisa keberuntungan. 100 trade: mulai bermakna.
  500+: bisa diuji lintas regime.
- Ambang edge nyata: p < 0.05.
- Minimal 30 (ideal 100+) trade sebelum Kelly/RoR dipakai sizing.

==================================================================
BAGIAN 8 — QUICK REFERENCE
==================================================================
| Win Rate (W)       | menang / total                                  |
| Risk/Reward (R)    | avg win / avg loss                              |
| Expectancy         | (W x AvgWin) - ((1-W) x AvgLoss)                |
| Kelly %            | W - [(1-W)/R]  =  (bp - q)/b                    |
| RoR (dasar)        | ((1-Edge)/(1+Edge))^CapitalUnits                |
| RoR (R:R)          | (LossRate/(WinRate x R:R))^(Threshold/RiskTrade)|
| Bayes              | P(A|D) = P(D|A)P(A) / P(D)                      |

==================================================================
BAGIAN 9 — CATATAN IMPLEMENTASI DI HERMES
==================================================================
1. Kelly % / RoR TIDAK dihitung dari <30-50 trade → noise (modul
   core/probability.py menolak otomatis, output "n<30 = noise").
2. Backtest overfit menaikkan WR artifisial → RoR live bisa jauh
   lebih buruk → gerbang drift detector tetap wajib.
3. Default sizing = QUARTER KELLY (6.7%) — sudah terkunci di
   config.yaml risk_pct; dokumen ini adalah justifikasinya.
4. Bayesian updating dipakai Staf untuk menggabungkan estimasi
   independen (regime, volume, Polymarket) menjadi satu telaah.
5. Monte Carlo pada hasil backtest sebelum sizing live.

==================================================================
SUMBER RISET (verifikasi lanjutan oleh Nahkoda)
==================================================================
daytrading.com/probability-theory-trading • ic.com/blog/thinking-in-
probabilities • pyquantnews.com • journalplus.co (kelly/risk-of-ruin/
glossary) • paperswithbacktest.com • tradesearcher.ai • backtestbase.com
• newtraderu.com • traderssecondbrain.com • quantifiedstrategies.com
• fxnx.com • math.mit.edu 18.05 • ocw.mit.edu 18.05 • stat.berkeley.edu
• towardsdatascience.com

CATATAN AKURASI: Formula (Kelly, RoR, Bayes, Expectancy) = baku &
dapat diverifikasi. Angka ilustrasi dari sumber bergantung asumsi —
bukan konstanta universal. Selalu validasi ulang dengan data sendiri.
