"""HERMES core.data — fetcher Hyperliquid publik + fallback OKX + cache.
Bar format: (ts_ms, o, h, l, c, vol) menaik. Tanpa pustaka luar.
"""
import json, os, time, urllib.request

CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
UA = {"User-Agent": "hermes/0.1", "Content-Type": "application/json"}


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _post(url, body, timeout=15):
    req = urllib.request.Request(url, json.dumps(body).encode(), UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def hl_candles(coin, interval="1d", n=400, base="https://api.hyperliquid.xyz"):
    """HL candleSnapshot + startTime paging (API kini wajib/membatasi form
    tanpa startTime). Live tetap dapat n bar terakhir; backtest minta lebih."""
    try:
        rows, start = [], int(time.time() * 1000) - max(n, 400) * 86_400_000 * 2
        for _ in range(40):
            r = _post(f"{base}/info",
                      {"type": "candleSnapshot",
                       "req": {"coin": coin, "interval": interval, "startTime": start}})
            if not r:
                break
            new = [(int(c["t"]), float(c["o"]), float(c["h"]), float(c["l"]),
                    float(c["c"]), float(c["v"])) for c in r]
            rows += new
            last_t = max(x[0] for x in new)
            if last_t <= start:      # API diam / tidak maju -> selesai
                break
            start = last_t + 1
        return sorted(set(rows))[-n:]
    except Exception:
        return []


def okx_candles(inst, bar="1D", n=400):
    """OKX history-candles dengan pagination via 'after' (cursor ts_ms).
    3 halaman x 100 bar = 300 bar >= min_bars gate."""
    for base in ["https://www.okx.com", "https://aws.okx.com"]:
        try:
            rows, after = [], None
            for _ in range(3):
                url = f"{base}/api/v5/market/history-candles?instId={inst}&bar={bar}&limit=100"
                if after:
                    url += f"&after={after}"
                r = _get(url)
                if not r.get("data"):
                    break
                rows += [(int(x[0]), float(x[1]), float(x[2]), float(x[3]),
                          float(x[4]), float(x[5])) for x in r["data"]]
                after = min(int(x[0]) for x in r["data"])
                if len(r["data"]) < 100:
                    break
                time.sleep(0.2)
            return sorted(set(rows))[-n:]
        except Exception:
            time.sleep(0.3)
    return []


def fetch(coin, interval="1d", bar="1D", n=400):
    """HL utama -> OKX fallback -> cache terakhir."""
    rows = hl_candles(coin, interval, n)
    if len(rows) < 120:
        rows = okx_candles(f"{coin}-USDT", bar, n)
    if rows:
        os.makedirs(CACHE, exist_ok=True)
        json.dump(rows, open(os.path.join(CACHE, f"{coin}-{interval}.json"), "w"))
    else:
        p = os.path.join(CACHE, f"{coin}-{interval}.json")
        if os.path.exists(p):
            rows = [tuple(r) for r in json.load(open(p))]
    return rows
