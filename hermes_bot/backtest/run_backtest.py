"""HERMES backtest.run_backtest — CLI dual-window (9y penuh + 3y terakhir).
Pemakaian:
  python -m hermes_bot.backtest.run_backtest --all --years 9
  python -m hermes_bot.backtest.run_backtest --coin BTC
Output: backtest_results/<COIN>.json + SUMMARY.md (PASS/FAIL vs validate.py)
"""
import argparse, datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import yaml
from hermes_bot.core.data import fetch
from hermes_bot.backtest.engine import run as replay
from hermes_bot.backtest.report import metrics, monte_carlo, pass_fail_table

RESULTS = "backtest_results"


def one_coin(coin, cfg, years):
    # years=0 = FULL window (maks historis HL ~6 thn); lainnya = tahun terakhir
    bars = 3400 if years == 0 else min(365 * years + 300, 3400)
    rows = fetch(coin, "1d", "1D", bars)
    if len(rows) < 300:
        return {"error": f"NO_DATA ({len(rows)} bar)"}
    s = cfg["strategy"]["don"]
    trades = replay(rows, s["sl_atr"], s["trail_atr"], s["volume_min"],
                    cfg["strategy"]["regime"]["erp_min"])
    m = metrics(trades)
    mc = monte_carlo(trades)
    if mc:
        m["mc_p95"] = mc["p95"]
    # window 3 tahun terakhir (filter ts_out)
    cut = (rows[-1][0] - 3 * 365 * 86_400_000)
    recent = [t for t in trades if t["ts_out"] >= cut]
    m3 = metrics(recent)
    mc3 = monte_carlo(recent)
    if mc3:
        m3["mc_p95"] = mc3["p95"]
    os.makedirs(RESULTS, exist_ok=True)
    json.dump({"coin": coin, "full": m, "y3": m3, "n_trades_full": m["n"],
               "trades_tail": trades[-30:]},
              open(f"{RESULTS}/{coin}.json", "w"), indent=1)
    return {"full": m, "y3": m3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coin")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    cfg = yaml.safe_load(open("config.yaml"))
    coins = cfg["assets"]["d1_watchlist"] if args.all else [args.coin]
    table = {}
    for c in coins:
        r = one_coin(c, cfg, 0)
        if "error" in r:
            print(f"{c}: {r['error']}")
            table[c] = {"9y": None, "3y": None}
            continue
        table[c] = {"full": r["full"], "3y": r["y3"]}
        g = lambda m: (m.get("n", 0), m.get("pf", "-"), m.get("tot_r", "-"))
        n9, pf9, r9 = g(r["full"])
        n3, pf3, r3 = g(r["y3"])
        print(f"{c}: full n={n9} PF={pf9} totR={r9} | 3y n={n3} PF={pf3} totR={r3}")
    md = ["# SUMMARY Backtest DON-D1 (biaya: fee 0.045% + slippage 0.05%/sisi)",
          f"Dibuat: {datetime.date.today().isoformat()} | gerbang: n>=100, PF>=1.1, totR>0",
          "Window FULL = maks historis per venue (HL ~6 thn, bukan 9 thn riset awal).",
          "", pass_fail_table(table), ""]
    os.makedirs(RESULTS, exist_ok=True)
    with open(f"{RESULTS}/SUMMARY.md", "w") as f:
        f.write("\n".join(md))
    print("SUMMARY ->", f"{RESULTS}/SUMMARY.md")


if __name__ == "__main__":
    main()
