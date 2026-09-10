"""HERMES core.probability — formula peluang dari Referensi-Probabilitas.md.
Semua fungsi punya gerbang sampel: n < MIN -> return None (noise, bukan sinyal).
Jalankan sendiri sebagai smoke test: python -m hermes_bot.core.probability
"""
MIN_TRADES = 30  # dari dokumen: minimal 30 (ideal 100+) sebelum dipakai


def expectancy(win_rate, avg_win, avg_loss):
    """E = W*AvgWin - (1-W)*AvgLoss. Negatif = berhenti, bukan naikkan size."""
    return win_rate * avg_win - (1 - win_rate) * avg_loss


def kelly(win_rate, payoff_ratio):
    """f* = W - (1-W)/R. Return None jika sampel tidak layak."""
    if payoff_ratio <= 0:
        return None
    f = win_rate - (1 - win_rate) / payoff_ratio
    return max(f, 0.0)


def risk_of_ruin(win_rate, payoff_ratio, threshold_units, risk_per_trade):
    """RoR = (L/(W*R))^(Threshold/Risk). Return None jika sampel tidak layak."""
    if win_rate <= 0 or payoff_ratio <= 0 or risk_per_trade <= 0:
        return None
    base = (1 - win_rate) / (win_rate * payoff_ratio)
    if base >= 1:
        return 1.0
    return base ** (threshold_units / risk_per_trade)


def live_stats(closed, quarter=0.25):
    """Stats live dari daftar trade R. Return None jika n < MIN_TRADES.
    closed: list dict dengan kunci 'r' (hasil dalam R)."""
    rs = [t["r"] for t in closed]
    if len(rs) < MIN_TRADES:
        return None
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    w = len(wins) / len(rs)
    aw = sum(wins) / len(wins) if wins else 0.0
    al = abs(sum(losses) / len(losses)) if losses else 1e-9
    R = aw / al
    k = kelly(w, R)
    ror = risk_of_ruin(w, R, threshold_units=50, risk_per_trade=0.067)
    return {"n": len(rs), "wr": round(w, 3), "payoff": round(R, 2),
            "expectancy_R": round(w * aw - (1 - w) * al, 3),
            "kelly_full": round(k, 3) if k is not None else None,
            "kelly_quarter": round(k * quarter, 3) if k is not None else None,
            "ror_50u": round(ror, 4) if ror is not None else None}


def summary_lines(state):
    """Untuk daily_reporter: laporan probabilitas atau peringatan sampel."""
    st = live_stats(state["closed"])
    if st is None:
        n = len(state["closed"])
        return [f"probability: n={n} <{MIN_TRADES} -> Kelly/RoR = NOISE (belum dihitung)"]
    kq = st["kelly_quarter"]
    kq_txt = f"{kq*100:.1f}%" if kq is not None else "n/a"
    ror = st["ror_50u"]
    ror_txt = f"{ror*100:.2f}%" if ror is not None else "n/a"
    return [f"probability: n={st['n']} WR={st['wr']*100:.0f}% payoff={st['payoff']} "
            f"E={st['expectancy_R']:+.3f}R "
            f"Kelly(quarter)={kq_txt} RoR(50u)={ror_txt}"]


if __name__ == "__main__":
    # Smoke test dengan contoh dokumen: WR55% avgWin312 avgLoss208 -> Kelly 25%
    e = expectancy(0.55, 312, 208)
    k = kelly(0.55, 312 / 208)
    assert k is not None, "kelly tidak boleh None untuk payoff>0"
    assert abs(k - 0.25) < 1e-9, f"kelly salah: {k}"
    assert abs(e - 78.0) < 1e-9, f"expectancy salah: {e}"
    # negatif = berhenti
    assert kelly(0.20, 1.0) == 0.0
    # gerbang sampel
    assert live_stats([{"r": 1.0}] * 10) is None
    ok = live_stats([{"r": 1.5}] * 55 + [{"r": -1.0}] * 45)
    assert ok and ok["n"] == 100
    print("probability smoke test PASS:", ok)
