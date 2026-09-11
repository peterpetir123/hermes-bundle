"""HERMES backtest.report — metrik + Monte Carlo (stdlib murni).
Konstitusi Referensi-Probabilitas: DD untuk sizing = p95 shuffle, bukan DD jalur tunggal.
"""
import random

GATE = {"n_min": 100, "pf_min": 1.1, "totr_min": 0.0}  # = validate.py


def metrics(trades):
    rs = [t["r"] for t in trades]
    n = len(rs)
    if not n:
        return {"n": 0, "pass": False}
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    gross_w = sum(wins)
    gross_l = abs(sum(losses))
    pf = gross_w / gross_l if gross_l else float("inf")
    tot_r = sum(rs)
    wr = len(wins) / n
    exp = tot_r / n
    curve, peak, maxdd = 0.0, 0.0, 0.0
    for r in rs:
        curve += r
        peak = max(peak, curve)
        maxdd = max(maxdd, peak - curve)
    ok = (n >= GATE["n_min"] and pf >= GATE["pf_min"] and tot_r > GATE["totr_min"])
    return {"n": n, "wr": round(wr, 3), "pf": round(pf, 3),
            "tot_r": round(tot_r, 1), "expectancy": round(exp, 3),
            "max_dd_r": round(maxdd, 1), "pass": ok}


def monte_carlo(trades, iters=1000, seed=42):
    """Shuffle urutan trade 1000x -> distribusi maxDD. Return p50/p95."""
    rs = [t["r"] for t in trades]
    if len(rs) < 10:
        return None
    rng = random.Random(seed)
    dds = []
    for _ in range(iters):
        rng.shuffle(rs)
        curve = peak = dd = 0.0
        for r in rs:
            curve += r
            peak = max(peak, curve)
            dd = max(dd, peak - curve)
        dds.append(dd)
    dds.sort()
    return {"p50": round(dds[len(dds) // 2], 1),
            "p95": round(dds[int(len(dds) * 0.95)], 1), "iters": iters}


def pass_fail_table(results_by_coin):
    """results_by_coin: {coin: {9y: metrics, 3y: metrics}} -> markdown."""
    lines = ["| Aset | Window | n | WR | PF | totR | maxDD | MC p95 | Gerbang |",
             "|---|---|---|---|---|---|---|---|---|"]
    for coin, w in sorted(results_by_coin.items()):
        for win, m in w.items():
            if not m or m.get("n", 0) == 0:
                lines.append(f"| {coin} | {win} | 0 | - | - | - | - | - | FAIL(no data) |")
                continue
            mc = m.get("mc_p95", "-")
            lines.append(
                f"| {coin} | {win} | {m['n']} | {m['wr']} | {m['pf']} | "
                f"{m['tot_r']} | {m['max_dd_r']} | {mc} | "
                f"{'PASS' if m['pass'] else 'FAIL'} |")
    return "\n".join(lines)
