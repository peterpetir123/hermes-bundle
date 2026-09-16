
## 2026-09-16 08:57:36 UTC
**Sumber:** [Investing with Martingale – An Experiment with RSI+Martingale Position Sizing](https://www.quantconnect.com/blog/rsi-indicator-with-martingale-position-sizing/)

INSIGHT:
- Konten artikel secara substantif tidak ada di halaman yang dikirim — isinya hanya navigasi, header, dan boilerplate situs QuantConnect (menu, footer, CTA signup).
- Dari judul dan URL dapat disimpulkan topiknya: eksperimen penggabungan indikator RSI dengan position sizing Martingale (menggandakan ukuran posisi setelah loss).
- Halaman berstatus "pending review" di komunitas QuantConnect, artinya belum melewati kurasi kualitas riset komunitas.
- Tidak ada angka hasil backtest, metodologi, atau kesimpulan yang bisa diverifikasi dari teks yang diberikan.

RELEVANSI:
- Konsep Martingale pada dasarnya berlawanan dengan desain Hermes: Hermes sudah punya position sizing terukur (quarter-Kelly 6,7%) dan risk management eksplisit (SL 3 ATR, trailing 3.5 ATR), sedangkan Martingale justru meningkatkan eksposur setelah kerugian — pola yang secara statistik mendorong risiko ruin dan deret loss beruntun yang mematikan akun.
- Karena isi artikel tidak tersedia, tidak ada materi konkret yang bisa diangkat sebagai pembelajaran untuk Hermes.
- Catatan kewaspadaan: strategi berbasis Martingale sering terlihat bagus di backtest (equity curve mulus, drawdown kecil di permukaan) karena tail risk-nya baru muncul di skenario ekstrem — persis tipe overfitting/risiko yang perlu disikapi skeptis.

PROPOSAL: -
