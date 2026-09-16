"""HERMES run_scan — orkestrator denyut (entry-point cron).
Pipeline: config -> data -> regime -> signal -> risk -> exec -> trailing
-> log -> digest (opsional). Polymarket = overlay laporan, bukan gate.
"""
import argparse, json, os, shutil, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import yaml
from hermes_bot.core.data import fetch
from hermes_bot.core.signals_don import scan_don
from hermes_bot.exec.risk import check_trade, load_state
from hermes_bot.exec.hl_exec import open_position
from hermes_bot.exec.trailing import manage
from hermes_bot.notify import telegram_bot as tg
from hermes_bot.report.daily_reporter import generate

# load .env sederhana (tanpa dependensi)
ENV = os.path.join(ROOT, ".env")
if os.path.exists(ENV):
    for line in open(ENV):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def monitor(cfg):
    """Cek posisi terbuka TANPA LLM (0 token): fetch hanya koin berposisi,
    jalankan manage() (trailing + close saat SL tersapu), alert event.
    SEKALIGUS kirim ringkasan analisa ke Telegram (TELEGRAM_PERIODIC=1,
    keputusan Nahkoda 2026-09-15) — hanya saat tidak PAUSED."""
    state = load_state()
    if os.environ.get("TELEGRAM_PERIODIC") == "1":
        _periodic_report(state, cfg)
    if not state["positions"]:
        print("monitor: no open positions")
        return
    coins = sorted({p["coin"] for p in state["positions"]})
    rows_map = {c: fetch(c, "1d", "1D", cfg["data"]["min_bars"] + 100)
                for c in coins}
    n_ev = 0
    for ev in manage(cfg, rows_map):
        n_ev += 1
        if ev.get("event") == "CLOSED_TRAIL":
            tg.alert_close(ev)
        elif ev.get("event") == "CLOSE_FAIL":
            tg.alert_system(f"close gagal {ev.get('coin')}: {ev.get('r')}")
    print(f"monitor: {len(coins)} posisi dicek ({', '.join(coins)}), {n_ev} event")


def _periodic_report(state, cfg):
    """Ringkasan analisa tiap denyut monitor (:10/:40) -> Telegram.
    0 token: template string murni. Fallback = alert_system jika gagal kirim."""
    try:
        ls = json.load(open("log/last_scan.json")) if os.path.exists(
            "log/last_scan.json") else {"scans": []}
        rows = []
        for s in ls.get("scans", []):
            rows.append(f"{s['coin']}: {s['status']} ({s.get('regime')}, "
                        f"{s.get('px'):g}, trig {s.get('trigger'):g}, "
                        f"dist {s.get('dist_atr')} ATR)")
        pos = state.get("positions", [])
        pos_txt = (" | ".join(f"{p['coin']} @{p['entry']:g} SL {p['sl']:g}"
                              for p in pos)) if pos else "tidak ada"
        pnl = state.get("day_pnl", 0.0)
        txt = (f"📡 HERMES {time.strftime('%H:%M UTC')}\n"
               f"equity ${state.get('equity', 0):.2f} · day {pnl:+.2f}\n"
               f"posisi: {pos_txt}\n"
               + "\n".join(rows))
        tg.digest_raw(state, txt)
    except Exception as e:
        tg.alert_system(f"periodic report gagal: {str(e)[:120]}")


def narrative_buf(cfg):
    """buf_atr efektif dari mode narasi (KEPUTUSAN 2026-09-16, report-only
    modulasi trigger; BUKAN buka entry). off / F&G gagal -> 0.15 = BASE."""
    mode = cfg.get("narrative_trigger", {}).get("mode", "off")
    mode = str(mode if mode is not None else "off").lower()  # yaml: off=False
    if mode != "buf":
        return 0.15, None, mode
    try:
        from hermes_bot.core.sentiment import fear_greed
        v = fear_greed().get("value")
        if v is None:
            return 0.15, None, mode
        return (0.5 if v < 25 else 0.3 if v < 45 else 0.15), v, mode
    except Exception:
        return 0.15, None, mode


def main(digest=False):
    # PAUSE = Hermes dihentikan via /off: tidak ada analisa/fetch/LLM/entry/
    # monitor/digest sama sekali. Infrastruktur (Telegram, watchdog) tetap hidup.
    if os.path.exists("PAUSE"):
        print(f"hermes: PAUSED sejak {open('PAUSE').read().strip()} — /on untuk aktifkan")
        return
    cfg = yaml.safe_load(open("config.yaml"))
    if "--monitor" in sys.argv:
        monitor(cfg)
        return
    assets = cfg["assets"]["d1_watchlist"]
    # backup memori posisi — gratis tiap denyut, murah saat bencana
    if os.path.exists("state/state.json"):
        shutil.copy("state/state.json", "state/state.json.bak")
    state = load_state()
    rows_map, scans, lines = {}, [], []
    buf, fngv, mode = narrative_buf(cfg)

    for coin in assets:
        rows = fetch(coin, "1d", "1D", cfg["data"]["min_bars"] + 100)
        if len(rows) < cfg["data"]["min_bars"]:
            lines.append(f"{coin}: NO_DATA")
            continue
        rows_map[coin] = rows
        sig = scan_don(rows, buf_atr=buf)
        sig["coin"] = coin
        scans.append(sig)
        lines.append(f"{coin}: {sig['status']} ({sig.get('regime')}, "
                     f"vol {sig.get('vol_ratio')}x, dist {sig.get('dist_atr')} ATR)")
    lines.append(f"narasi_trigger: mode={mode} fng={fngv} buf={buf} ATR "
                 f"(report-only modulasi; KEPUTUSAN 2026-09-16)")

    # Polymarket overlay (report-only)
    pm_lines = ["polymarket: disabled"]
    if cfg.get("polymarket", {}).get("enabled"):
        try:
            from hermes_bot.core.polymarket import snapshot, summary_lines
            pm_lines = summary_lines(snapshot())
        except Exception as e:
            pm_lines = [f"polymarket: n/a ({str(e)[:60]})"]

    # risk + eksekusi
    equity = state.get("equity") or float(os.environ.get("INIT_EQUITY", "20"))
    opened = []
    for sig in scans:
        if sig.get("status") != "TRIGGER":
            continue
        ok, reason, plan = check_trade(sig, cfg, equity)
        if ok:
            pos, msg = open_position(sig["coin"], plan, sig, cfg)
            if pos:
                opened.append(pos)
                tg.alert_open(pos, sig["coin"])
        elif reason in ("CIRCUIT_BREAKER", "KILL_SWITCH", "MAX_POSITIONS", "HALTED"):
            tg.alert_system(f"entry {sig['coin']} ditolak: {reason}")

    # trailing
    for ev in manage(cfg, rows_map):
        if ev.get("event") == "CLOSED_TRAIL":
            tg.alert_close(ev)
        elif ev.get("event") == "CLOSE_FAIL":
            tg.alert_system(f"close gagal {ev['coin']}: {ev.get('r')}")

    # watch-queue (report-only, MIND/KEPUTUSAN.md): ETA adaptif ke TRIGGER
    try:
        from hermes_bot.core.watchqueue import update as wq_update, line as wq_line
        wq = wq_update(scans)
        wq_lines = [wq_line(wq)]
    except Exception as e:
        wq, wq_lines = [], [f"watchqueue: n/a ({str(e)[:60]})"]

    # log + print + digest
    os.makedirs("log", exist_ok=True)
    json.dump({"scans": scans, "watchqueue": wq},
              open("log/last_scan.json", "w"), indent=1)
    print("\n".join(lines))
    print("\n".join(pm_lines))
    print("\n".join(wq_lines))
    if opened:
        print(f"OPENED: {[p['coin'] for p in opened]}")

    if digest:
        st = load_state()
        if os.environ.get("LLM_API_KEY"):
            report = generate(st, scans, pm_lines)
        else:
            report = "\n".join(lines + pm_lines)
        tg.digest(st, report)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--digest", action="store_true")
    ap.add_argument("--monitor", action="store_true")
    main(digest=ap.parse_args().digest)
