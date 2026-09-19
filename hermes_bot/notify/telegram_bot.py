"""HERMES notify.telegram_bot — alert template string (0 token)."""
import json, os, urllib.request


def _send(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        return False
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json.dumps({"chat_id": chat, "text": text, "parse_mode": "Markdown"}).encode(),
            {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def alert_open(pos, coin):
    return _send(f"*HERMES* OPEN {coin}\nentry `{pos['entry']:.6g}` SL `{pos['sl']:.6g}`\n"
                 f"trail {pos['trail_atr']}xATR | notional ${pos['notional']}\n"
                 f"regime {pos['regime']} (erp {pos['erp']})")


def alert_close(c):
    e = "✅" if c["r"] > 0 else "❌"
    return _send(f"*HERMES* CLOSE {c['coin']} {e}\nexit `{c['exit']:.6g}` | *{c['r']:+.2f}R*\nalasan {c['reason']}")


def alert_trail(pos, sl):
    """Trigger saat SL naik (trail) = de-facto TP mesin ini. 0 token."""
    entry = pos["entry"]
    lock = (sl - entry) / entry * 100
    tag = (f"profit terkunci +{lock:.2f}%" if lock > 0
           else f"belum profit (SL {lock:.2f}%)")
    return _send(f"*HERMES* TRAIL-UP {pos['coin']}\n"
                 f"SL naik -> `{sl:.6g}` (entry {entry:.6g})\n"
                 f"{tag} | mesin ini tanpa TP tetap: TP-nya = trail ini")


def alert_system(msg):
    return _send(f"⚠️ *HERMES SYSTEM*\n{msg}")


def digest(state, report):
    op = "\n".join(f"  {p['coin']} @{p['entry']:.4g} SL {p['sl']:.4g}" for p in state["positions"]) or "  -"
    return _send(f"*HERMES DIGEST*\n{report[:3800]}")


def digest_raw(state, summary_text):
    return _send(f"*HERMES DIGEST*\nequity ${state.get('equity', 0):.2f} "
                 f"| day {state.get('day_pnl', 0):+.2f}\n{summary_text[:3800]}")
