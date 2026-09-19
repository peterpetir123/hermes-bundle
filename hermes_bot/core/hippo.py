"""HERMES v2 core.hippo — Hippocampus: memori episodik (fast store).

Prinsip otak: hippocampus menangkap EPISOD — kejadian ber-sumbu-waktu dengan
konteks lengkap (apa, kapan, kondisi pasar, apa yang diputuskan, hasilnya).
Penyimpanan cepat & mahal; nanti dikonsolidasi (core.consolidate) jadi
semantic memory (lessons) dan di-prune.

Prinsip tulis (encoding):
- Setiap KEJADIAN signifikan ditulis SATU baris JSON (append-only, like brain
  replay-safe): kind, ts, ctx, decision, outcome(null saat belum diketahui).
- Encoding diperkuat "novelty" (Gruber 2014): kejadian mengejutkan diberi
  salience lebih tinggi -> prioritas konsolidasi.

Prinsip query (recovery):
- recency + similarity konteks (coin, kind) -> episodic recall utk keputusan.

Stdlib murni, JSONL append-only, tanpa LLM. Batas: RETAIN_MAX episodic
(hippocampus kapasitas terbatas; yang tua dikonsolidasi lalu di-prune).
"""
import json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORE = os.path.join(ROOT, "state", "episodes.jsonl")
RETAIN_MAX = 2000   # buffer episodik; konsolidator yang mem-prune arsip lama


def _ts():
    return time.strftime("%F %T", time.gmtime()) + "Z"


def encode(kind, ctx=None, decision=None, salience=1.0, **extra):
    """Tulis satu episod. kind: trade|signal|anomaly|decision|note|alarm.
    salience = kejutan/novelty (Gruber 2014): >1 = mengejutkan, layak diingat."""
    ep = {"ts": _ts(), "kind": kind, "salience": round(float(salience), 2),
          "ctx": ctx or {}, "decision": decision}
    ep.update(extra)
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    with open(STORE, "a") as f:
        f.write(json.dumps(ep, ensure_ascii=False) + "\n")
    return ep


def recall(kind=None, coin=None, limit=10, min_salience=0.0, since_hours=None):
    """Replay episod terakhir yang cocok (terbaru dulu) — awake-replay ala
    Jadhav 2012: dipakai saat mengambil keputusan."""
    try:
        lines = open(STORE).read().strip().splitlines()
    except Exception:
        return []
    cut = time.time() - since_hours * 3600 if since_hours else None
    out = []
    for line in reversed(lines):
        try:
            ep = json.loads(line)
        except Exception:
            continue
        if kind and ep.get("kind") != kind:
            continue
        if coin and ep.get("ctx", {}).get("coin") != coin:
            continue
        if ep.get("salience", 1.0) < min_salience:
            continue
        if cut and _parse_ts(ep.get("ts")) and _parse_ts(ep["ts"]) < cut:
            continue
        out.append(ep)
        if len(out) >= limit:
            break
    return out


def _parse_ts(ts):
    try:
        return time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%SZ")) - time.timezone
    except Exception:
        return None


def stats():
    try:
        lines = open(STORE).read().strip().splitlines()
    except Exception:
        return {"n": 0}
    from collections import Counter
    kinds = Counter()
    for ln in lines:
        try:
            kinds[json.loads(ln).get("kind", "?")] += 1
        except Exception:
            pass
    return {"n": len(lines), "kinds": dict(kinds), "capacity_pct":
            round(100 * len(lines) / RETAIN_MAX, 1)}


def prune_old(n_keep=RETAIN_MAX):
    """Buang tertua bila over kapasitas (konsolidasi mengarsip dulu di luar)."""
    try:
        lines = open(STORE).read().strip().splitlines()
    except Exception:
        return 0
    if len(lines) <= n_keep:
        return 0
    open(STORE, "w").write("\n".join(lines[-n_keep:]) + "\n")
    return len(lines) - n_keep


if __name__ == "__main__":
    import tempfile, os as _os
    # smoke di store terisolasi
    tmp = tempfile.mkdtemp()
    orig = STORE
    STORE = _os.path.join(tmp, "ep.jsonl")
    encode("trade", ctx={"coin": "BTC"}, decision="open", r=1.5)
    encode("anomaly", ctx={"coin": "ETH"}, decision=None, salience=2.5,
           note="vol spike 4x")
    encode("signal", ctx={"coin": "BTC"}, decision="observe")
    assert len(recall(kind="trade")) == 1
    assert len(recall(coin="BTC")) == 2
    assert recall(min_salience=2.0)[0]["kind"] == "anomaly"
    assert stats()["n"] == 3
    assert prune_old(n_keep=2) == 1
    assert stats()["n"] == 2
    STORE = orig
    print("hippo smoke PASS", stats())
