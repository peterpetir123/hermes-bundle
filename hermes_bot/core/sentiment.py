"""HERMES core.sentiment — Fear&Greed + RSS headline (stdlib murni, 0 LLM token).
Semua fetch try/except -> fallback kosong; kegagalan TIDAK PERNAH bikin denyut gagal.
NARASI = REPORT-ONLY (MIND/KEPUTUSAN.md) — tidak pernah menyentuh eksekusi.
Cache 1 jam di cache/ agar denyut sering tak boros call.
"""
import json, os, time, urllib.request, xml.etree.ElementTree as ET

CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
UA = {"User-Agent": "Mozilla/5.0"}  # CF 1010-blocker: UA python-urllib diblok
TTL = 3600


def _cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < TTL:
        try:
            return json.load(open(p))
        except Exception:
            pass
    try:
        data = fn()
        json.dump(data, open(p, "w"))
        return data
    except Exception:
        return {}


def fear_greed():
    """Fear & Greed Index (alternative.me). {'value':int,'label':str} atau {}."""
    def _f():
        req = urllib.request.Request("https://api.alternative.me/fng/?limit=1", headers=UA)
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())
        x = d["data"][0]
        return {"value": int(x["value"]), "label": x["value_classification"]}
    return _cached("fng.json", _f)


def headlines(n=8, feed="https://cointelegraph.com/rss"):
    """n headline terbaru dari RSS crypto. [{'title','date'}] atau []."""
    def _f():
        req = urllib.request.Request(feed, headers=UA)
        xml = urllib.request.urlopen(req, timeout=15).read()
        root = ET.fromstring(xml)
        out = []
        for item in root.iter("item"):
            t = item.findtext("title", "").strip()
            d = item.findtext("pubDate", "").strip()
            if t:
                out.append({"title": t[:160], "date": d[:22]})
            if len(out) >= n:
                break
        return out
    return _cached("news.json", _f)


def summary_lines():
    """Ringkas utk digest/dashboard — selalu aman dipanggil."""
    lines = []
    fg = fear_greed()
    if fg:
        lines.append(f"fear_greed: {fg['value']} ({fg['label']})")
    hl = headlines()
    if hl:
        lines.append("berita24j: " + " | ".join(h["title"] for h in hl[:5]))
    return lines or ["narasi: n/a (sumber gagal)"]


if __name__ == "__main__":
    fg = fear_greed()
    hl = headlines()
    assert "value" in fg and 0 <= fg["value"] <= 100, f"F&G rusak: {fg}"
    assert isinstance(hl, list), "headlines harus list"
    print("sentiment smoke PASS:", fg, f"| {len(hl)} headline")
