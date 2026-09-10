"""HERMES exec.hl_exec — eksekutor: paper/testnet + live via SDK (lazy import)."""
import json, os
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
LOG = os.path.join(ROOT, "log", "trades.jsonl")


def _log(e):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(e) + "\n")


def open_position(coin, plan, sig, cfg):
    if cfg["mode"] == "live" and os.environ.get("HL_PRIVATE_KEY"):
        ok, msg = _sdk(coin, plan["notional"] / plan["px"], buy=True)
        if not ok:
            return None, f"ORDER_FAILED: {msg}"
    s = json.load(open(os.path.join(ROOT, "state", "state.json")))
    pos = {"id": f"P-{int(datetime.now(timezone.utc).timestamp())}", "coin": coin,
           "entry": plan["px"], "sl": plan["sl"], "hh": plan["px"],
           "trail_atr": plan["trail_atr"], "notional": plan["notional"],
           "risk_usd": plan["risk_usd"], "regime": sig["regime"], "erp": sig["erp"],
           "opened": datetime.now(timezone.utc).isoformat()}
    s["positions"].append(pos)
    json.dump(s, open(os.path.join(ROOT, "state", "state.json"), "w"), indent=1)
    _log(dict(pos, event="OPEN", mode=cfg["mode"]))
    return pos, "OK"


def close_position(pos, px_exit, reason, cfg):
    fee_rt = 0.0009
    gross = (px_exit - pos["entry"]) * (pos["notional"] / pos["entry"])
    r = (gross - abs(gross) * fee_rt) / pos["risk_usd"] if pos["risk_usd"] else 0.0
    if cfg["mode"] == "live" and os.environ.get("HL_PRIVATE_KEY"):
        ok, msg = _sdk(pos["coin"], None, buy=False)
        if not ok:
            return None, f"CLOSE_FAILED: {msg}"
    p = os.path.join(ROOT, "state", "state.json")
    s = json.load(open(p))
    s["positions"] = [x for x in s["positions"] if x["id"] != pos["id"]]
    c = dict(pos, exit=px_exit, r=round(r, 3), reason=reason,
             closed=datetime.now(timezone.utc).isoformat())
    s["closed"].append(c)
    s["day_pnl"] = round(s.get("day_pnl", 0.0) + gross, 4)
    s["equity"] = round(s.get("equity", 0.0) + gross, 4)
    json.dump(s, open(p, "w"), indent=1)
    _log(dict(c, event="CLOSE", mode=cfg["mode"]))
    return c, "OK"


def _sdk(coin, sz, buy):
    try:
        from hyperliquid.exchange import Exchange
        from hyperliquid.utils import constants
        base = (constants.TESTNET_API_URL
                if os.environ.get("HL_TESTNET", "1") == "1"
                else constants.MAINNET_API_URL)
        ex = Exchange(os.environ["HL_PRIVATE_KEY"], base_url=base)
        res = ex.market_open(coin, sz) if buy else ex.market_close(coin)
        ok = str(res.get("status")) == "ok"
        return ok, str(res)[:200]
    except Exception as e:
        return False, str(e)[:200]
