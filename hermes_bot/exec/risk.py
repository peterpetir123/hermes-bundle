"""HERMES exec.risk — Risk Engine formula vault (CB, maks posisi, leverage-stop,
two-tier margin). Semua nilai dari config.yaml."""
import json, os, time

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
STATE = os.path.join(ROOT, "state", "state.json")
KILL = os.path.join(ROOT, "KILL")


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"positions": [], "closed": [], "equity": 20.0, "day": "",
            "day_pnl": 0.0, "halted": False, "stage": "A"}


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE, "w"), indent=1)


def kill_active():
    return os.path.exists(KILL)


def check_trade(sig, cfg, equity):
    """Return (ok, reason, plan)."""
    r = cfg["risk"]
    s = load_state()
    today = time.strftime("%Y-%m-%d")
    if s["day"] != today:
        s["day"], s["day_pnl"], s["halted"] = today, 0.0, False
        save_state(s)
    if kill_active():
        return False, "KILL_SWITCH", None
    if s["halted"]:
        return False, "HALTED", None
    if s["day_pnl"] <= -r["circuit_breaker_daily"] * max(equity, 1e-9):
        s["halted"] = True
        save_state(s)
        return False, "CIRCUIT_BREAKER", None
    if len(s["positions"]) >= r["max_positions"]:
        return False, "MAX_POSITIONS", None
    if sig.get("status") != "TRIGGER":
        return False, "NO_TRIGGER", None

    px, sl = sig["px"], sig["sl"]
    sl_pct = abs(px - sl) / px
    if sl_pct * 100 >= 80:
        return False, "SL_TOO_WIDE", None
    lev_cap = min(0.80 / max(sl_pct, 1e-9), 50)

    if equity < r["full_margin_below_equity"]:
        notional = max(equity * min(lev_cap, 5.0), r["min_notional_usd"])
        risk_usd = notional * sl_pct
    else:
        risk_usd = equity * r["risk_pct"]
        notional = risk_usd / sl_pct
    plan = {"px": px, "sl": sl, "trail_atr": sig["trail"],
            "notional": round(notional, 2), "risk_usd": round(risk_usd, 3),
            "sl_pct": round(sl_pct * 100, 2), "lev_cap": round(lev_cap, 1)}
    return True, "OK", plan
