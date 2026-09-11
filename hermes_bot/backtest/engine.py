"""HERMES backtest.engine — replay D1 memakai modul core ASLI.
TANPA duplikasi logika strategi: sinyal = scan_don() persis live.
Aturan anti-lookahead: sinyal terbaca di close bar i, ENTRY di open bar i+1.
Biaya jujur: fee 0.045% + slippage 0.05% per sisi (config BEKU).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from hermes_bot.core.signals_don import scan_don

FEE_PCT = 0.00045     # taker Hyperliquid
SLIP_PCT = 0.0005     # slippage per sisi
COST = FEE_PCT + SLIP_PCT


def run(rows, sl_atr=3.0, trail_atr=3.5, vol_min=1.5, erp_min=0.55):
    """Walk-forward satu aset, D1, long-only, satu posisi per aset.
    Return list trade: dict(ts_in, ts_out, entry, exit, r, bars)."""
    trades = []
    pos = None
    min_hist = 260  # er_percentile butuh lookback 252 + win 20
    for i in range(min_hist, len(rows) - 1):
        bar = rows[i]
        nxt = rows[i + 1]
        if pos:
            # trailing pakai modul indikator yang sama via scan param:
            # HH naik dengan high, SL = HH - trail_atr*ATR(14) saat ini
            from hermes_bot.core.indicators import atr as _atr
            a = _atr(rows[:i + 1], 14)
            if bar[2] > pos["hh"]:
                pos["hh"] = bar[2]
            if a:
                new_sl = pos["hh"] - trail_atr * a
                if new_sl > pos["sl"]:
                    pos["sl"] = new_sl
            if bar[3] <= pos["sl"]:  # low tersapu -> exit di SL
                _close(trades, pos, pos["sl"], bar[0])
                pos = None
            continue
        sig = scan_don(rows[:i + 1], sl_atr, trail_atr, vol_min, erp_min)
        if sig.get("status") != "TRIGGER":
            continue
        entry = nxt[1] * (1 + COST)          # open bar berikut + biaya masuk
        sl0 = entry - sl_atr * sig["atr"]
        pos = {"entry": entry, "sl": sl0, "sl0": sl0, "hh": nxt[2],
               "atr0": sig["atr"], "ts_in": nxt[0]}
    if pos:  # sisa posisi terbuka -> tutup di close terakhir (ditandai)
        _close(trades, pos, rows[-1][4], rows[-1][0], open_end=True)
    return trades


def _close(trades, pos, exit_px, ts_out, open_end=False):
    exit_eff = exit_px * (1 - COST)
    risk = pos["entry"] - pos["sl0"]   # R selalu dari SL AWAL, bukan SL trailing
    r = (exit_eff - pos["entry"]) / risk if risk > 0 else 0.0
    trades.append({"ts_in": pos["ts_in"], "ts_out": ts_out,
                   "entry": round(pos["entry"], 8), "exit": round(exit_eff, 8),
                   "r": round(r, 4), "bars": None, "open_end": open_end})
