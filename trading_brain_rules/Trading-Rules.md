# 📜 Trading Rules — Aturan Besi

> **Aturan ini TIDAK BOLEH dilanggar dalam kondisi apapun.**
> Setiap pelanggaran harus dicatat di [[❌ Lessons Learned/📝 Mistakes-Index]] dan dianalisis.

---

## 🔴 Aturan Utama

### 1. Risk Management
- **Risk per trade:** 5-10% dari total modal
- **Risk/Reward minimum:** 3:1 (tidak ada pengecualian)
- **Leverage:** 5-10x (menurun saat modal naik)
- **Stop Loss:** WAJIB dipasang SEBELUM entry, berdasarkan struktur teknikal

### 2. Frekuensi Trading
- **Max 2 trade per hari** (saat real trading)
- **Jika 1 trade LOSS:** STOP trading hari itu, langsung analisis kesalahan
- **Jika 1 trade PROFIT:** Boleh ambil 1 trade lagi jika setup valid
- **Testing/Paper trade:** Tidak ada batas frekuensi

### 3. Pre-Trade Checklist (WAJIB ✅)
Sebelum setiap trade, jawab SEMUA pertanyaan ini:

- [ ] **Trend:** Apa trend di timeframe 1H/4H? (Bullish/Bearish/Sideways)
- [ ] **Setup:** Apakah ada setup valid dari [[📋 Trading System/📊 Strategy-Playbook|Playbook]]?
- [ ] **Confluence:** Apakah ada minimal 3 konfirmasi? (Indikator, S/R, Pattern, Volume)
- [ ] **Entry:** Di mana entry point yang tepat?
- [ ] **Stop Loss:** Di mana SL berdasarkan struktur? (bukan angka random)
- [ ] **Take Profit:** Di mana TP? Apakah RR ≥ 3:1?
- [ ] **Position Size:** Berapa ukuran posisi? (max 5-10% risk)
- [ ] **Emosi:** Apakah saya trading berdasarkan analisis atau emosi?
- [ ] **Konfirmasi Analis:** Apakah Antigravity sudah review setup ini?
- [ ] **News Check:** Apakah ada event/news besar yang bisa impact?

> [!CAUTION]
> Jika SATU saja checklist tidak terpenuhi → **JANGAN TRADE.**

### 4. Post-Trade Checklist
Setelah setiap trade (win ATAU loss):

- [ ] Catat di [[📓 Trade Journal/📊 Journal-Dashboard|Trade Journal]]
- [ ] Screenshot chart di TradingView
- [ ] Analisis: Apakah entry sesuai plan?
- [ ] Analisis: Apakah exit sesuai plan?
- [ ] Jika LOSS: Catat di [[❌ Lessons Learned/📝 Mistakes-Index|Lessons Learned]]
- [ ] Update [[📊 Performance/Equity-Curve|Equity Curve]]

---

## 📊 Scaling Rules — Leverage & Target

| Modal | Leverage | Risk/Trade | Target Bulanan |
|:---|:---|:---|:---|
| $4 - $20 | 10x | 10% ($0.40-$2.00) | 5x (400%) |
| $20 - $100 | 7x | 7% ($1.40-$7.00) | 3x (200%) |
| $100 - $500 | 5x | 5% ($5-$25) | 2x (100%) |
| $500 - $2000 | 3x | 3% ($15-$60) | 1.5x (50%) |
| $2000+ | 2x | 2% ($40+) | 1.3x (30%) |

> [!NOTE]
> Target keuntungan bulanan MENURUN seiring modal bertambah. Ini karena:
> 1. Semakin besar modal, semakin penting proteksi capital
> 2. Risiko ruin harus mendekati 0% saat modal signifikan
> 3. Compound effect sudah bekerja dengan % lebih kecil

---

## 🎯 Readiness Criteria — Kapan Mulai Real Trading

| Metric | Target Minimum |
|:---|:---|
| Total Paper Trades | ≥ 50 |
| Win Rate | ≥ 45% |
| Profit Factor | ≥ 1.5 |
| Max Consecutive Losses | ≤ 4 |
| Checklist Compliance | ≥ 90% |
| Consistent Profitability | ≥ 2 minggu berturut-turut profit |

> [!IMPORTANT]
> **JANGAN mulai real trading sebelum SEMUA kriteria terpenuhi.**
> Patience adalah skill trading yang paling penting.

---

## ⚙️ Platform & Tools

| Tool | Fungsi | Link |
|:---|:---|:---|
| **TradingView** | Charting & analisis | tradingview.com |
| **Phantom** | Wallet Solana | phantom.app |
| **Jupiter Perps** | DEX Perpetuals | perps.jup.ag |
| **Drift Protocol** | DEX Perpetuals | drift.trade |
| **CoinGlass** | Funding Rate, OI, Liquidation | coinglass.com |
| **Arkham** | Whale tracking | arkham.intelligence |
| **DexScreener** | Altcoin monitoring | dexscreener.com |

---

## 📐 Formula Quick Reference

### Position Size
```
Position Size = (Modal × Risk%) / (Entry - SL)
Contoh: ($4 × 10%) / ($100 - $97) = $0.40 / $3 = 0.133 unit
Dengan leverage 10x: Margin needed = 0.133 × $100 / 10 = $1.33
```

### Risk/Reward Ratio
```
RR = (TP - Entry) / (Entry - SL)
Harus ≥ 3.0
```

### Expected Value per Trade
```
EV = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
Contoh: (45% × $1.20) - (55% × $0.40) = $0.54 - $0.22 = +$0.32
```

---

*Terakhir diupdate: 2026-08-22*
*[[🏠 HOME|← Kembali ke HOME]]*
