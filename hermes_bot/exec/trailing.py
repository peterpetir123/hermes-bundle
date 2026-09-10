"""HERMES exec.trailing — SL = HH - trail*ATR, hanya naik; close saat tersapu."""
from .hl_exec import close_position
from .risk import load_state, save_state
from ..core.indicators import atr


def manage(cfg, rows_map):
    s = load_state()
    events = []
    for pos in list(s["positions"]):
        rows = rows_map.get(pos["coin"])
        if not rows or len(rows) < 15:
            continue
        a = atr(rows, 14)
        if not a:
            continue
        if rows[-1][2] > pos["hh"]:
            pos["hh"] = rows[-1][2]
            s["positions"] = [p if p["id"] != pos["id"] else pos for p in s["positions"]]
        new_sl = pos["hh"] - pos["trail_atr"] * a
        if new_sl > pos["sl"]:
            pos["sl"] = new_sl
            save_state(s)
            events.append(dict(pos, event="TRAIL_UP", sl=round(new_sl, 6)))
        if rows[-1][3] <= pos["sl"]:
            c, msg = close_position(pos, pos["sl"], "trail-hit", cfg)
            events.append(dict(c or pos, event="CLOSED_TRAIL" if c else "CLOSE_FAIL",
                               r=c.get("r") if c else msg))
    save_state(s)
    return events
