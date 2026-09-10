# 🤖 AI-Quant Protocol — Mesin Keputusan Tanpa Bias

> **Prinsip:** AI tidak boleh meniru cara manusia trading. Prediksi, timing, dan intuisi
> diganti dengan **state machine + formula yang parameternya dikunci sebelumnya**.
> Dokumen ini adalah KONTRAK. Mengubah parameter tanpa bukti backtest = pelanggaran.
>
> Dibuat: 2026-08-23 | Versi 1.0 | Status: **⚠️ METODE INTI M15 DIHENTIKAN** (24.560 trade bukti rugi neto) — lihat [[🧪 Testing Lab/2026-08-25-Audit-Algo-Scalping|Audit 18 kekurangan]] • Metode aktif paper: H1-Trailing ([[🧪 Testing Lab/2026-08-24-Riset-Metode-Kuantitatif|riset]]) • Komponen probabilitas = SWING ONLY 🔒 [[📚 Knowledge Base/02-Quantitative/🎲 Probabilitas-Kondisional-SWING-ONLY|dokumen terkunci]]
> **Versi 2.0 (2026-09-02):** Struktur keputusan dirombak — NAHKODA & STAF. Lihat §0.

---

## 0️⃣ Struktur Keputusan: Nahkoda & Staf Analisis (v2.0, 2026-09-02)

**Pemilik keputusan = NAHKODA (manusia).** Engine/sistem tidak lagi menjadi sumber keputusan — ia menjadi **satu input** di antara banyak input. AI berperan sebagai **Staf Analisis**.

### Alur kerja setiap keputusan
1. **Nahkoda sampaikan tesis** (arah, koin, timeframe, size, leverage yang dibayangkan).
2. **Staf telaah 5 lapis data vault:**
   - Regime saat ini (UP/DN/CHOP via ER20+SMA100)
   - Kuintil volatilitas aset (5 volatil teratas = historically breakeven)
   - Preseden backtest (setup serupa, hasilnya apa)
   - Leverage–Stop Compatibility (`SL_dist% < 80%/Leverage`)
   - Volume/momentum terkini
3. **Verdict 3 warna + bukti:**
   - 🟢 **SEPAKAT** — data mendukung
   - 🟡 **BERSYARAT** — setuju JIKA kondisi terdaftar terpenuhi
   - 🔴 **TIDAK SEPAKAT** — data melawan (wajib angka, bukan opini)
   - Wajib ditambah: **kondisi pembatal** — apa yang harus terjadi agar tesis dianggap salah.
4. **Nahkoda putuskan. Staf catat.** Hasil riil masuk log.

### Batas wewenang staf
- Setiap verdict wajib disertai bukti angka dari data vault.
- Pelanggaran aturan vault (leverage berlebih, melawan regime, koin kuintil volatil) → staf **tandai merah sebelum eksekusi**, sekali, dengan data.
- Setelah flag merah dan nahkoda tetap lanjut → keputusan dihormati, dicatat sebagai **KEPUTUSAN-NAHKODA**, hasilnya diukur nanti tanpa drama.
- Staf tidak pernah mengarang data atau menghaluskan analisa demi kesepakatan.

### Pencatatan dua jalur ([[🧪 Testing Lab/Paper-Trades/Signal-Log|Signal Log]])
| Jalur | Isi | Tujuan |
|:---|:---|:---|
| **SINYAL-SISTEM** | Output algoritma apa adanya (#001 dst.) | Benchmark objektif |
| **KEPUTUSAN-NAHKODA** | Tesis + analisa staf + verdict + hasil riil | Mengukur kualitas insting vs sistem |

### Peringatan data (tetap berlaku)
Seluruh backtest tervalidasi (+78.6R, 12.465 trade, 9 thn) adalah **LONG-ONLY spot**. Analisa arah TURUN hanya didukung data regime (filter CHOP/DN) — **bukan edge short teruji**. Staf wajib menyebutkan ini setiap kali nahkoda menimbang short.

---

## 1️⃣ Pemetaan Bias Manusia → Pengganti Kuantitatif

| Elemen Manusia (DIHAPUS) | Pengganti Kuantitatif (WAJIB) |
|:---|:---|
| Prediksi arah & timing pasar | State machine: hitung skor kondisi SAAT INI, eksekusi hanya via trigger IF-THEN |
| SL "di bawah struktur" (subjektif) | `SL = 1.5 × ATR14(15m)` dari entry — formula tetap |
| TP "di resistance" (subjektif) | `TP1 = 1.5R`, `TP2 = 3.0R` — kelipatan risiko, bukan level gambaran |
| Confluence naratif ("kelihatannya support") | Skor komposit berbobot dengan bobot terkunci |
| Baca news secara naratif | Skor sentimen numerik −1..+1, fungsi VETO saja |
| "Kira-kira sudah oversold" | RSI dinormalisasi `(RSI−50)/30`, clamp [−1,+1] |
| Cerita "pump sehat vs distribusi" | Rasio volume naik/turun terukur pada N candle terakhir |
| Emosi / FOMO / revenge | N/A untuk AI — diganti data-quality gate (data basi/invalid → NO TRADE) |

---

## 2️⃣ Lapisan Skor (Semua Numerik)

### Trend Score T ∈ [−1,+1]
Per timeframe (15m, 1H, 4H): `+0.33 jika EMA9>EMA20, +0.33 jika EMA20>EMA50, +0.34 jika close>EMA200(≈)` → jumlah per TF.
`T = 0.25·T₁₅ + 0.35·T₁ₕ + 0.40·T₄ₕ`

### Momentum Score M ∈ [−1,+1]
`M = 0.30·norm(RSI14) + 0.40·slope(MACD-hist,4bar)/2ATR + 0.30·ROC10/6ATR` (semua clamp ±1)

### Flow Score F ∈ [−1,+1]
`F = 0.70·contrarian(funding) + 0.30·OI-delta-score`
Contrarian funding: funding tinggi = long crowding = skor negatif untuk long. `−(funding−0.0001)/0.0005`

### Komposit
```
S = 0.40·T + 0.30·M + 0.30·F
S ≥ +0.35 → LONG ARMED      S ≤ −0.35 → SHORT ARMED      |S| < 0.35 → NO TRADE
```
⚠️ **ARMED ≠ ENTRY.** Arah hanya "diizinkan". Entry butuh trigger model §4.

### Regime Filter (Veto, bukan arah)
Percentile ATR bar terakhir vs 150 bar:
- > 92% → CHAOS → tolak trade baru
- < 8% → DEAD → tolak trade baru
- Else → TRADABLE

---

## 3️⃣ Level Objektif (Bukan Gambaran Manual)
Swing high/low = fraktal lookback 5 bar, cluster jika selisih ≤ 0.15%.
Level hanya dipakai untuk memilih MODEL entry (§4), tidak untuk menaruh SL/TP.

---

## 4️⃣ Model Trigger Entry (IF-THEN Murni)

**PB-LONG:** `S≥0.35` DAN low 3 bar terakhir menyentuh band `[EMA20₁₅ₘ−0.75·ATR, EMA20₁₅ₘ+0.10·ATR]` DAN bar saat ini close di ≥67% range bar-nya.
**BO-LONG:** close > `level_resistensi + 0.15·ATR` DAN volume ≥ 1.5×avg20 DAN `S≥0.35`.
**SHORT:** cermin sempurna (tanda dibalik) dengan `S≤−0.35`.

> Tidak ada model lain. Tidak ada "tunggu dan lihat dulu bentuknya".

---

## 5️⃣ Risk Engine (Formula Terkunci)

> ⚖️ **PRA-SYARAT EKSEKUSI:** cek [[📋 Trading System/⚖️ Leverage-Stop-Compatibility|Leverage–Stop Compatibility]] — `SL_dist% < 80%/Leverage`. Gagal = trade dibatalkan terlepas dari sinyal.

```
SL_dist   = 1.5 × ATR14(15m)
Entry     = harga close bar trigger
TP1       = Entry ± 1.5×SL_dist  → tutup 50% posisi, SL geser ke breakeven
TP2       = Entry ± 3.0×SL_dist  → tutup sisa          (memenuhi aturan RR≥3 vault)
Size      = (Modal × Risk%) / SL_dist , cap: Quarter-Kelly 6.7% & tabel leverage vault
Invalidasi posisi: bar CLOSE melewati SL. Tidak ada SL mental.
```

---

## 6️⃣ News → Angka (Veto Saja)

| Kelas Event | Skor |
|:---|:---|
| Rate decision FOMC/CPI melawan arah trade | −0.8 |
| Hack/regulasi keras exchange besar | −0.7 |
| ETF flow signifikan searah | +0.4 |
| Noise biasa | 0 |

Aturan: `|sentiment| ≥ 0.6 DAN berlawanan arah trade` → **BLOK trade**. News tidak pernah menjadi alasan arah mandiri.

---

## 7️⃣ Tata Kelola Parameter (Anti Curve-Fitting)
1. Semua parameter di dokumen ini BEKU. Perubahan butuh: ≥100 instance historis + walk-forward test positif EV.
2. Setiap keputusan WAJIB menghasilkan audit log lengkap: semua input, semua skor, rule yang menyala. Tidak bisa dihitung → NO TRADE.
3. Evaluasi statistik setiap 30 trades: WR, PF, EV aktual vs asumsi (WR 40–45%, RR 3).

---

## 8️⃣ Case Study #001 — Live 2026-08-23 (BTC/USDT, $78,461)

| Input | Nilai |
|:---|:---|
| T (15m/1H/4H) | 1.00 / 1.00 / 1.00 → **T = 1.000** |
| M (rsi_n/macd_slope/roc) | 0.50 / −0.06 / 0.33 → **M = 0.225** |
| F (funding 0.010%) | **F = 0.00** (netral) |
| **Komposit S** | **0.468 → LONG ARMED** |
| Regime | TRADABLE (vol-rank 77%) |
| PB-band | [77,635 – 77,909] → harga DI LUAR band ❌ |
| Close-position bar terakhir | 0.20 (< 0.67) ❌ |
| **Keputusan sistem** | **NO TRADE — arah long diizinkan, trigger entry BELUM menyala.** Jika trigger PB/BO menyala: Entry=trigger-close, SL=±482 pts (1.5×ATR), TP1/TP2 = 1.5R/3.0R, size per formula §5. |

> Catatan pembelajaran #002: setup manual kemarin (zona 76.3k) arahnya benar,
> tapi entry/SL ditentukan diskresioner → tidak bisa diaudit & direplikasi.
> Solusi sistemik: protokol ini. [[❌ Lessons Learned/Loss-Analysis/2026-08-23-BTC-Koreksi-vs-Distribusi|Ref analisa bias]]

---

*[[📋 Trading System/📜 Trading-Rules|Trading Rules]] • [[🏠 HOME|← HOME]]*
