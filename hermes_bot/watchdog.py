"""HERMES watchdog — kesehatan tiap 30 menit."""
import json, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from hermes_bot.notify import telegram_bot as tg


def main():
    msgs = []
    if os.path.exists("KILL"):
        msgs.append("KILL-switch aktif — eksekusi berhenti (rm KILL untuk resume)")
    if os.path.exists("state/state.json"):
        s = json.load(open("state/state.json"))
        if s.get("halted"):
            msgs.append(f"HALTED (circuit breaker) pada {s.get('day')}")
    if os.path.exists("log/last_scan.json"):
        age = time.time() - os.path.getmtime("log/last_scan.json")
        if age > 26 * 3600:
            msgs.append(f"scan terakhir {age/3600:.0f} jam lalu — cek cron/endpoint")
    du = shutil.disk_usage("/")
    if du.free / du.total < 0.15:
        msgs.append(f"disk sisa {du.free/1e9:.1f}GB (<15%)")
    with open("/proc/meminfo") as f:
        ram = int(next(l for l in f if "MemAvailable" in l).split()[1])
    if ram < 200_000:
        msgs.append(f"RAM tersedia {ram//1024}MB — rendah")
    if msgs:
        tg.alert_system("\n".join(msgs))
    print("\n".join(msgs) or "watchdog OK")


if __name__ == "__main__":
    main()
