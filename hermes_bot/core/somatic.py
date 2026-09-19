"""HERMES v2 core.somatic — Somatic Marker (Damasio/Bechara).

Prinsip otak: SEBELUM analisis lambat, penanda valensi cepat (dari pengalaman
berbadan) memangkas opsi: "ini bahaya, jangan", "ini menarik, perhatikan".
Tanpa marker, keputusan hancur (pasien vmPFC: IQ normal, keputusan kacau).

Di Hermes v2: marker = skor valensi [-1, +1] yang dihitung MURAH (mikrodetik,
0 LLM) dari tiga sumber pengalaman:
  1. rpe skor strategi (pengalaman hasil: strategi yang membawakan dopamin)
  2. lessons gist per koin (pengalaman koin: dominan menang/besar/menang kecil)
  3. anomaly (anomali mengejutkan -> marker negatif singkat: waspada)

Output: (marker, alasan) — fast-path. Kepemutusan: marker TIDAK MENENTUKAN
sendiri; ia memangkas/mengurutkan opsi untuk slow-path (analisis penuh).
marker <= -0.6  -> PRUNE (jangan bahas, kecuali paksa=True)
marker >= +0.5  -> PRIORITAS (bahas dulu)
di antara       -> netral, urut salience biasa

Stdlib murni, tanpa LLM, mikrodetik.
"""
import time

from hermes_bot.core import hippo, rpe

# gerbang ambang (statis, bukan config runtime — ponytail #3)
PRUNE = -0.6
PRIORITIZE = 0.5
W_RPE = 0.5      # bobot pengalaman strategi
W_COIN = 0.35    # bobot pengalaman koin
W_ANOM = 0.15    # bobot anomali terkini (negatif: waspada)


def _coin_valence(coin, lessons=None, window_days=30):
    """Valensi koin dari lessons gist: win_ratio dipetakan ke [-1, +1]."""
    if lessons is None:
        from hermes_bot.core.consolidate import lessons as _lessons
        lessons = _lessons()
    d = (lessons.get("by_coin") or {}).get(coin)
    if not d or d.get("n", 0) < 5:
        return 0.0, "belum-kenal"          # koin tak dikenal: netral
    wr = d["win_ratio"]
    return round((wr - 0.5) * 2, 2), f"win_ratio={wr} n={d['n']}"


def _anomaly_valence(coin, window_hours=48):
    """Anomali terkini koin ini -> waspada (negatif kecil, cepat pudar)."""
    eps = hippo.recall(kind="anomaly", coin=coin, limit=5,
                       since_hours=window_hours)
    return -0.5 if eps else 0.0, f"{len(eps)} anomali {window_hours}h"


def mark(coin, strategy="don_breakout"):
    """Somatic marker utk opsi 'trade coin via strategy'.
    Return (value, action, reasons) — action: PRUNE|PRIORITIZE|PASS."""
    reasons = []
    # 1. pengalaman strategi
    scores = {n: s for n, s, _ in rpe.rank()}
    s_val = max(-1.0, min(1.0, scores.get(strategy + "_" + coin.lower(), 0.0)))
    reasons.append(f"rpe={s_val:+.2f}")
    # 2. pengalaman koin
    c_val, c_txt = _coin_valence(coin)
    reasons.append(f"coin={c_txt}")
    # 3. anomali terkini
    a_val, a_txt = _anomaly_valence(coin)
    reasons.append(f"anom={a_txt}")
    v = round(W_RPE * s_val + W_COIN * c_val + W_ANOM * a_val, 3)
    action = "PRUNE" if v <= PRUNE else ("PRIORITIZE" if v >= PRIORITIZE else "PASS")
    return v, action, "; ".join(reasons)


def shortlist(candidates, force=False):
    """Terapkan marker ke daftar opsi (coin): buang PRUNE (kecuali force),
    urutkan PRIORITIZE dulu. Return [(coin, value, action)]."""
    marked = []
    for coin in candidates:
        v, action, _ = mark(coin)
        if action == "PRUNE" and not force:
            continue
        marked.append((coin, v, action))
    marked.sort(key=lambda x: -x[1])
    return marked


if __name__ == "__main__":
    # smoke: koin kenal-buruk vs kenal-baik vs asing
    v_good, a_good, r_good = mark("ETH")
    v_bad, a_bad, r_bad = mark("XRP")
    v_unknown, a_unknown, _ = mark("ZZZ")
    assert v_good > v_bad, (v_good, v_bad)
    assert a_unknown == "PASS", a_unknown   # tak dikenal = netral, jangan prune
    assert -1 <= v_bad <= 1 and -1 <= v_good <= 1
    print(f"somatic smoke PASS")
    print(f"  ETH (baik)   : {v_good:+.2f} {a_good}  [{r_good}]")
    print(f"  XRP (buruk)  : {v_bad:+.2f} {a_bad}  [{r_bad}]")
    print(f"  ZZZ (asing)  : {v_unknown:+.2f} {a_unknown}")
    sl = shortlist(["ETH", "XRP", "ZZZ", "BTC"])
    print("  shortlist:", sl)
