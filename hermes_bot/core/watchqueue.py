"""HERMES core.watchqueue — antrean koin terdekat ke TRIGGER (0 LLM token).
REPORT-ONLY (MIND/KEPUTUSAN.md): tidak pernah gate eksekusi.

ETA adaptif (keputusan Nahkoda): kecepatan pendekatan diukur dari perubahan
dist_atr antar denyut (cache/dist_history.json). Data <2 denyut atau koin
menjauh -> fallback 1 ATR/hari. ETA = estimasi prioritas perhatian, BUKAN
janji harga akan menyentuh level.
"""
import json, math, os, time

CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
HIST = os.path.join(CACHE, "dist_history.json")
FALLBACK_ATR_PER_DAY = 1.0   # ponytail: fallback, history membaik otomatis
MIN_VEL = 0.05               # ATR/hari — di bawah ini dianggap datar
MAX_POINTS = 60              # ~2-3 hari denyut 30-60 mnt; cukup utk kecepatan


def _load_hist():
    try:
        return json.load(open(HIST))
    except Exception:
        return []


def update(scans):
    """Catat dist_atr denyut ini + hitung ETA. scans = list sig dari scan_don.
    Return list {coin, dist_atr, eta_days, trend} terurut terdekat dulu."""
    now = time.time()
    dist = {}
    for s in scans:
        d = s.get("dist_atr")
        if isinstance(d, (int, float)) and not math.isinf(d):
            dist[s["coin"]] = round(float(d), 3)
    hist = _load_hist()
    hist.append({"t": now, "d": dist})
    hist = hist[-MAX_POINTS:]
    try:
        os.makedirs(CACHE, exist_ok=True)
        json.dump(hist, open(HIST, "w"))
    except Exception:
        pass

    out = []
    for coin, d in dist.items():
        vel = None
        for prev in reversed(hist[:-1]):
            dt_days = (now - prev["t"]) / 86400.0
            if coin in prev.get("d", {}) and dt_days > 0:
                vel = (prev["d"][coin] - d) / dt_days  # + = mendekat
                break
        if vel is None or vel <= MIN_VEL:
            eta = d / FALLBACK_ATR_PER_DAY
            trend = "datar" if vel is None or abs(vel) <= MIN_VEL else "menjauh"
        else:
            eta = d / vel
            trend = "mendekat"
        out.append({"coin": coin, "dist_atr": d, "eta_days": round(eta, 1),
                    "trend": trend})
    out.sort(key=lambda x: x["eta_days"])
    return out


def line(wq):
    """Satu baris ringkas utk output denyut."""
    if not wq:
        return "watchqueue: kosong (tidak ada koin berm data dist_atr)"
    top = ", ".join(f"{x['coin']} {x['eta_days']}h({x['trend']})"
                    for x in wq[:3])
    return f"watchqueue: {top}"


if __name__ == "__main__":
    import shutil, tempfile
    tmp = tempfile.mkdtemp()
    orig = HIST
    # uji dengan cache terisolasi agar cache asli tak tersentuh
    globals()["HIST"] = os.path.join(tmp, "dist_history.json")
    t0 = time.time() - 86400  # denyut kemarin
    json.dump([{"t": t0, "d": {"BTC": 2.0, "ETH": 1.0, "SOL": 0.5}}],
              open(globals()["HIST"], "w"))
    wq = update([{"coin": "BTC", "dist_atr": 1.0},   # -1 ATR/hari -> eta 1.0
                 {"coin": "ETH", "dist_atr": 1.5},   # menjauh -> fallback eta 1.5
                 {"coin": "SOL", "dist_atr": 0.25}])  # -0.25/hari -> eta 1.0
    by = {x["coin"]: x for x in wq}
    assert by["BTC"]["trend"] == "mendekat" and by["BTC"]["eta_days"] == 1.0, by["BTC"]
    assert by["ETH"]["trend"] == "menjauh", by["ETH"]
    assert by["SOL"]["trend"] == "mendekat", by["SOL"]
    assert wq[0]["coin"] in ("BTC", "SOL"), wq  # terdekat dulu
    # denyut pertama tanpa history -> semua fallback, tetap aman
    globals()["HIST"] = os.path.join(tmp, "h2.json")
    wq2 = update([{"coin": "XRP", "dist_atr": 3.2}])
    assert wq2[0]["eta_days"] == 3.2 and wq2[0]["trend"] == "datar", wq2
    shutil.rmtree(tmp)
    globals()["HIST"] = orig
    print("watchqueue smoke PASS:", by["BTC"], by["ETH"])
