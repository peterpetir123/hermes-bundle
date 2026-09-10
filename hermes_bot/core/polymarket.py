"""HERMES core.polymarket — implied probability dari pasar prediksi.
PERAN: overlay konsensus untuk laporan & telaah KN. BUKAN gate entry,
BUKAN pemicu eksekusi (protokol: edge dari formula beku saja).
"""
import json, os, time, urllib.request

GAMMA = "https://gamma-api.polymarket.com"
UA = {"User-Agent": "hermes/0.1"}
CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "cache", "polymarket.json")
KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum"],
    "SOL": ["solana"],
    "XRP": ["xrp", "ripple"],
    "DOGE": ["dogecoin"],
}


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _yes_prob(m):
    try:
        outcomes = json.loads(m.get("outcomes", "[]"))
        prices = json.loads(m.get("outcomePrices", "[]"))
        i = outcomes.index("Yes") if "Yes" in outcomes else 0
        return float(prices[i])
    except Exception:
        return None


def snapshot(limit=200):
    """Return {asset: [(p_yes, question, volume, end)]} top-volume per aset."""
    try:
        markets = _get(f"{GAMMA}/markets?active=true&closed=false&limit={limit}")
    except Exception:
        return {}
    out = {}
    for asset, kws in KEYWORDS.items():
        hits = []
        for m in markets:
            if m.get("closed") or m.get("archived"):
                continue
            q = (m.get("question") or "").lower()
            if any(k in q for k in kws):
                p = _yes_prob(m)
                if p is not None:
                    hits.append((p, m.get("question", "")[:90],
                                 float(m.get("volumeNum") or 0),
                                 (m.get("endDate") or "")[:10]))
        hits.sort(key=lambda x: -x[2])
        out[asset] = hits[:3]
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump({"ts": time.time(), "data": out}, open(CACHE, "w"))
    except Exception:
        pass
    return out


def summary_lines(snap):
    lines = ["polymarket (implied prob — konteks, bukan sinyal):"]
    for asset, hits in snap.items():
        if hits:
            p, q, vol, end = hits[0]
            lines.append(f"  {asset} {p*100:.0f}% | {q} | vol ${vol:,.0f} | ends {end}")
    return lines if len(lines) > 1 else ["polymarket: n/a (API gagal — abaikan)"]
