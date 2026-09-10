# ⚖️ Leverage–Stop Distance Compatibility Rule

> **Tanggal:** 2026-08-25 | **Pemicu:** temuan user — sinyal INJ (SL −19.7%) tidak executable
> di leverage 10x karena likuidasi (~−9%) menyentuh lebih dulu daripada SL.
> Status: **ATURAN WAJIB** — berlaku untuk SEMUA sistem (scalp/intraday/swing).

---

## Rumus Wajib Sebelum Eksekusi

```
1. Lev_likuidasi  = 80% / SL_dist%        # sisakan 20% buffer sebelum likuidasi
2. Lev_risk       = Risk$ / (Notional × SL_dist%)   # dari sizing formula
3. Lev_final      = MIN( Lev_modal_tabel , Lev_likuidasi , Lev_risk )
4. VALIDASI: SL_dist% < 80%/Lev_final  → jika GAGAL, trade TIDAK BOLEH dieksekusi
```

## Tabel Kompatibilitas (modal $4, risk 6.7% = $0.268)

| SL dist | Notional maks | Lev efektif | Lev aman maks | Mode cocok |
|---:|---:|---:|---:|:---|
| ≤1% | $26.8+ | hingga 6.7× | 10× ✅ | Scalping/intraday (jika edge terbukti) |
| 2% | $13.4 | 3.4× | 10× ✅ | Intraday H1 |
| 5% | $5.36 | 1.3× | 10× ✅ | Swing ringan |
| 10% | $2.68 | 0.67× | 5× ⚠️ | Swing D1 standar |
| 20% | $1.34 | 0.34× | **4× ❗** | Swing volatil (INJ-like) |

## Implikasi Per Mode

| Mode | SL khas | Leverage realistis | Catatan |
|:---|:---|:---|:---|
| Scalping M15 | 0.5–2% | 5–10× | Tapi metode M15 sudah DIHENTIKAN (riset) |
| Intraday H1-Trailing | 2–6% | 2–6× | Sesuai tabel, cek rumus per sinyal |
| Swing DON-D1 | 9–25% | **0.3–4×** | Leverage tinggi MATHEMATICALLY IMPOSSIBLE tanpa likuidasi |

## Filosofi (selaras [[📋 Trading System/📐 Risk-Management-Plan|Risk Management Plan]])
Leverage bukan tujuan — proteksi modal adalah. Efektif leverage otomatis menurun
saat volatilitas/stop melebar; itu BUKAN kelemahan sistem, melainkan fitur pengaman.
Yang dilarang: memaksa leverage tabel dengan mengecilkan SL sembarangan (sweep wick),
atau mengabaikan rumus di atas (risiko likuidasi sebelum SL).

---
*[[📋 Trading System/🤖 AI-Quant-Protocol|Protocol]] • [[❌ Lessons Learned/📝 Mistakes-Index|Mistakes Index]] • [[🏠 HOME|← HOME]]*
