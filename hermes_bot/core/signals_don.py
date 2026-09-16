"""HERMES core.signals_don — trigger DON breakout (IF-THEN murni)."""
from .indicators import atr, high_n, vol_ratio
from .regime import classify


def scan_don(rows, sl_atr=3.0, trail_atr=3.5, vol_min=1.5, erp_min=0.55,
             buf_atr=0.15):
    """buf_atr = buffer trigger (default 0.15, beku). Varian narasi
    (MIND/KEPUTUSAN.md 2026-09-16) mengubahnya dari CALLER, bukan di sini."""
    if len(rows) < 160:
        return {"status": "INSUFFICIENT_DATA"}
    rg = classify(rows)
    a = atr(rows, 14)
    hi = high_n(rows, 40)
    vr = vol_ratio(rows, 20)
    if not a or hi is None or not rg["valid"]:
        return {"status": "INSUFFICIENT_DATA"}

    px = rows[-1][4]
    trigger = hi + buf_atr * a
    out = {"px": px, "hi40": hi, "trigger": round(trigger, 6), "atr": round(a, 6),
           "vol_ratio": round(vr, 2), "regime": rg["regime"], "erp": rg["erp"],
           "dist_atr": round((trigger - px) / a, 2)}

    if rg["regime"] != "UP" or rg["erp"] < erp_min:
        out["status"] = "BLOCKED_REGIME"
    elif px > trigger and vr >= vol_min:
        out["status"] = "TRIGGER"
        out["sl"] = px - sl_atr * a
        out["trail"] = trail_atr
    elif px > trigger:
        out["status"] = "WAIT_VOLUME"
    else:
        out["status"] = "STANDING"
    return out
