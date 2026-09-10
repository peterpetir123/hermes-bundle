"""HERMES backtest.validate — gerbang bukti sebelum parameter berubah.
Replay DON-D1 pada cache; biaya 0.14% RT (model riset vault).
Gerbang naik: n>=100, PF>=1.1, totR>0.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from hermes_bot.core.data import fetch
from hermes_bot.core.indicators import atr, er_percentile, sma, high_n

FEE_RT = 0.0014
ASSETS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "LTC", "AVAX", "LINK"]


def replay(rows, lb=40, sl_m=3.0, trail_m=3.5, vol_min=1.5):
    closes = [r[4] for r in rows]
    trades, pos = [], None
    for i in range(260, len(rows) - 1):
        win = rows[: i + 1]
        a = atr(win, 14)
        erp = er_percentile(closes[: i + 1])
        s100 = sma(closes[: i + 1], 100)
        hi = high_n(win, lb)
        if not a or not erp or not s100 or not hi:
            continue
        up = erp >= 0.55 and closes[i] > s100
        vr = win[-1][5] / (sum(r[5] for r in win[-21:-1]) / 20 or 1)
        if pos:
            if win[i][2] > pos["hh"]:
                pos["hh"] = win[i][2]
            if pos["hh"] - trail_m * a > pos["sl"]:
                pos["sl"] = pos["hh"] - trail_m * a
            if win[i][3] <= pos["sl"]:
                r = (pos["sl"] - pos["entry"]) / pos["risk_d"] \
                    - FEE_RT * pos["entry"] / pos["risk_d"]
                trades.append(round(r, 3))
                pos = None
            continue
        if up and closes[i] > hi + 0.15 * a and vr >= vol_min:
            e = rows[i + 1][1]
            pos = {"entry": e, "sl": e - sl_m * a, "hh": e, "risk_d": sl_m * a}
    return trades


def run():
    all_r = []
    for c in ASSETS:
        rows = fetch(c, "1d", "1D", 1200)
        if len(rows) > 400:
            rs = replay(rows)
            all_r += rs
            print(f"{c}: n={len(rs)} totR={sum(rs):+.1f}")
    if not all_r:
        print("cache kosong — jalankan scan dulu"); return
    w = [r for r in all_r if r > 0]
    l = [r for r in all_r if r <= 0]
    pf = sum(w) / abs(sum(l)) if l and sum(l) != 0 else 99
    print(f"\nTOTAL n={len(all_r)} WR={len(w)/len(all_r)*100:.1f}% PF={pf:.2f} totR={sum(all_r):+.1f}")
    print("GERBANG:", "LULUS — parameter kandidat boleh aktif"
          if len(all_r) >= 100 and pf >= 1.1 and sum(all_r) > 0
          else "GAGAL — parameter tetap beku")


if __name__ == "__main__":
    run()
