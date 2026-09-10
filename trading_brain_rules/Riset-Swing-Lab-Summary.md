# 🔬 Riset #003 — Swing Lab: Regime Detector + 12.465 Simulasi Lintas 8 Tahun

> **Tanggal:** 2026-08-25 | **Data:** D1 × 20 aset × 2018–2026 (38.000+ bar; mencakup bear '18 & '22,
> crash COVID '20, bull '21, sideways '23–'25) | **Biaya dimodelkan:** 0.14% RT
> **Total trade tersimulasi: 12.465**

---

## 1️⃣ Regime Detector (BARU — tervalidasi)

```
ER      = Kaufman Efficiency Ratio 20d (|Δc20| / Σ|Δc harian|)
erp     = percentile rank ER vs 252 hari terakhir
Regime  : UP   jika erp ≥ 0.55 dan close > SMA100
          DN   jika erp ≥ 0.55 dan close < SMA100
          CHOP jika erp < 0.55
```
Bukti nilai: entry breakout LONG di regime UP menghasilkan +73.4R,
di DN hanya +5.3R — deteksi regime punya daya pisah nyata.

## 2️⃣ Hasil Grid (12.465 trade)

| Keluarga | Verdict |
|:---|:---|
| **DON breakout (lb40, SL3×ATR, trail3.5×ATR)** | 🏆 JUARA — lihat §3 |
| PB pullback uptrend (trail3.5) | PF 1.77 tapi profit terkonsentrasi 2020–21; rapuh sebagai standalone (satelit opsional) |
| Mean-Reversion di CHOP | ❌ Semua varian rugi (PF 0.67–0.93) — dibuang |

## 3️⃣ Juara: DON-lb40-tr3.5 — Profil Per Tahun

| Tahun | n | WR | PF | totR |
|:---|---:|---:|---:|---:|
| 2018 | 13 | 69.2% | 3.73 | +7.1 |
| 2019 | 42 | 33.3% | 0.99 | −0.2 |
| 2020 | 70 | 54.3% | 2.49 | +32.1 |
| 2021 | 95 | 45.3% | 1.96 | +27.7 |
| 2022 (bear) | 102 | 34.3% | 1.01 | **+0.3** |
| 2023 | 134 | 36.6% | 0.88 | −6.5 |
| 2024 | 139 | 35.3% | 1.29 | +17.3 |
| 2025 | 120 | 36.7% | 0.67 | −12.7 |
| 2026 YTD | 93 | 52.7% | 1.55 | +13.5 |

**TOTAL +78.6R | 6 tahun profit / 3 rugi (terburuk hanya −12.7R) | maxDD kronologis −12.7R**

Ini profil trend-following sejati: equity naik bertangga, tidak ada tahun katastropik,
ekspektansi portofolio ±+8.7R/tahun lintas 20 aset.

## 4️⃣ Probabilitas Kondisional di Level Swing — MASIH GAGAL

P(win|regime) rolling-origin per tahun: 2022 katastropik (filter malah menyeleksi
−152.6R). Kesimpulan konsisten dengan riset M15: **gating keras sederhana (UP-only untuk
long) mengalahkan pembobotan probabilistik lunak**. Modul probabilitas tetap 🔒 TERKUNCI.

## 5️⃣ Keputusan

| Item | Keputusan |
|:---|:---|
| Sistem swing inti | **DON-D1: long breakout 40d-hari + regime UP + trail 3.5×ATR** — paper dulu via Signal Log |
| Short | Ukuran minimal (DN regime cuma breakeven +5.3R) |
| MR | Dihentikan permanen |
| PB | Satelit opsional setengah size, hanya regime UP |
| Evaluasi | Review tiap kuartal; kill-switch −15R / 4-quarter PF<1.0 |

⚠️ Catatan kejujuran: hasil backtest ≠ janji masa depan. 2025 rugi menunjukkan sistem ini
bisa kalah berbulan-bulan; yang membuatnya layak adalah profil risiko-imbalan 9 tahunannya.

---
*[[🧪 Testing Lab/Pending-Tracker|Pending Tracker]] • [[📚 Knowledge Base/02-Quantitative/🎲 Probabilitas-Kondisional-SWING-ONLY|Probabilitas 🔒]] • [[🧪 Testing Lab/2026-08-25-Audit-Algo-Scalping|Audit Scalping]] • [[🏠 HOME|← HOME]]*
