"""HERMES v2 core.rpe — Dopamin: Reward Prediction Error (Schultz).

Prinsip otak: neuron dopamin tidak mengkode reward, ia mengkode
    RPE = actual - expected
RPE+ menguatkan strategi (teaching signal), RPE- melemahkan.
Asimetris: RPE+ lebih besar dari RPE- (optimisme struktural, Bayer & Glimcher).
Skor strategi = EMA dari RPE -> dipakai untuk bobot keputusan v2.

REPORT-ONLY terhadap engine lama: modul ini hanya MENYIMPAN dan MENGHITUNG.
Sumber RPE tahap 1: hasil backtest per-trade (offline, deterministik).
Tahap 2 (nanti): live trades expected-vs-actual.

Desain ponytail: stdlib murni, satu file, JSON flat, tanpa LLM.
"""
import json, math, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCORES = os.path.join(ROOT, "state", "rpe_scores.json")
# dopamin: positif dihitun penuh, negatif diredam (Bayer & Glimcher 2005)
ALPHA_NEG = 0.5
EMA_ALPHA = 0.3   # kecepatan update skor strategi
FLOOR = -1.0      # strategi tak pernah dibuang total; skor minimum


def load_scores():
    try:
        return json.load(open(SCORES))
    except Exception:
        return {}


def save_scores(s):
    os.makedirs(os.path.dirname(SCORES), exist_ok=True)
    json.dump(s, open(SCORES, "w"), indent=1)


def rpe(actual_r, expected_r):
    """Satu unit dopamin: RPE = actual - expected (dalam R).
    Negatif diredam ALPHA_NEG (asimetri biologis)."""
    d = (actual_r - expected_r)
    return d if d >= 0 else d * ALPHA_NEG


def update_strategy(name, actual_r, expected_r, meta=None):
    """Catat satu trade/keputusan + update EMA skor strategi."""
    s = load_scores()
    st = s.setdefault(name, {"score": 0.0, "n": 0, "sum_rpe": 0.0,
                             "wins": 0, "losses": 0, "last_ts": None})
    e = rpe(actual_r, expected_r)
    st["score"] = round(st["score"] * (1 - EMA_ALPHA) + e * EMA_ALPHA, 4)
    st["n"] += 1
    st["sum_rpe"] = round(st["sum_rpe"] + e, 3)
    st["wins" if actual_r > 0 else "losses"] += 1
    st["last_ts"] = time.strftime("%F %T", time.gmtime())
    if meta:
        st.setdefault("recent", []).append(
            {"ts": st["last_ts"], "actual_r": actual_r,
             "expected_r": expected_r, "rpe": round(e, 3), **meta})
        st["recent"] = st["recent"][-20:]
    save_scores(s)
    return e


def apply_baseline(trades, coin="NA"):
    """Tahap 1: RPE dari backtest. Expected = expectancy historis strategi
    (di sini konstan 0.39R dari SUMMARY BTC/ETH/SOL/DOGE pooled) —
    strategi yang konsisten lebih baik dari ekspektasi hidup, sebaliknya matang."""
    for t in trades:
        if t.get("r") is None:
            continue
        update_strategy("don_breakout_" + t.get("coin", coin).lower(),
                        actual_r=t["r"], expected_r=0.39,
                        meta={"ts_in": t.get("ts_in")})


def rank():
    """Strategi terurut skor — nanti dipakai voting 'thousand brains'."""
    s = load_scores()
    rows = sorted(s.items(), key=lambda kv: -kv[1]["score"])
    return [(k, v["score"], v["n"]) for k, v in rows]


if __name__ == "__main__":
    # smoke: asimetri dopamin + EMA stabil
    assert rpe(2.0, 1.0) == 1.0
    assert math.isclose(rpe(-2.0, 0.0), -1.0)          # diredam 0.5
    assert math.isclose(rpe(0.5, 2.0), -0.75)
    if len(sys_import := __import__("sys").argv) > 1 and sys_import[1] == "--seed":
        # seed dari backtest riil
        for coin in ("BTC", "ETH", "SOL", "DOGE", "XRP"):
            p = os.path.join(ROOT, "backtest_results", coin + ".json")
            try:
                d = json.load(open(p))
                apply_baseline(d.get("trades_tail", []), coin=coin)
            except Exception:
                pass
        print("seeded:", json.dumps(rank(), indent=1))
    else:
        print("rpe smoke PASS", rank())
