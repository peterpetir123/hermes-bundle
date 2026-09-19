"""HERMES v2 core.consolidate — Tidur: replay & konsolidasi memori (Born/2019).

Prinsip otak: saat SWS, hippocampus replay episod 4-10x lebih cepat dan
mentransfer ke neocortex sebagai GIST/schema (bukan rekaman). REM menjaga
pengetahuan lama. Di Hermes:
  - SWS  = scan episod trade -> update skor RPE (dopamin belajar dari outcome)
  - gist = pola yang berulang (koin/arah menang-kalah) -> state/lessons.json
  - REM  = jangan sentuh lessons yang sudah mapan (proteksi pengetahuan lama)
  - prune= hippocampus yang sudah dikonsolidasi dibersihkan (kapasitas terbatas)

Dijalankan cron "tidur" (mis. 1x/hari). Stdlib murni, tanpa LLM.
REPORT-ONLY terhadap engine lama; hasil konsolidasi = bahan keputusan v2.
"""
import json, os, time
from collections import defaultdict

from hermes_bot.core import hippo, rpe

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LESSONS = os.path.join(ROOT, "state", "lessons.json")
MARK = os.path.join(ROOT, "state", "consolidated_upto.json")
CONSOLIDATED = os.path.join(ROOT, "state", "episodes_archive.jsonl")

MIN_TRADES_GIST = 5      # baru jadi lesson jika n cukup (anti overfit 1-2 sampel)
WIN_RATIO_GIST = 0.7     # dominan menang/kalah baru layak dicatat


def _load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def run():
    """Satu sesi tidur. Return ringkasan (untuk log/cron)."""
    start = time.strftime("%F %T")
    s1 = _sws_rpe()
    s2 = _gist_lessons()
    n_pruned = hippo.prune_old()
    _mark_upto()
    out = {"ts": start, "rpe_updated": s1, "lessons_total": s2,
           "hippo_pruned": n_pruned}
    try:
        json.dump(out, open(os.path.join(ROOT, "log", "last_consolidate.json"),
                            "w"), indent=1)
    except Exception:
        pass
    return out


def _sws_rpe():
    """Replay episod trade belum-konsolidasi -> RPE update -> tandai."""
    eps = hippo.recall(kind="trade", limit=hippo.RETAIN_MAX)
    upto = _load(MARK, {}).get("ts", "")
    n = 0
    for ep in eps:
        if ep.get("ts", "") <= upto:
            continue  # sudah pernah dikonsolidasi (REM: tak diulang)
        r = ep.get("r")
        if r is None:
            continue
        # outcome final diketahui; expected = expectancy 0.39R (sama dgn seed)
        rpe.update_strategy(
            "don_breakout_" + str(ep.get("ctx", {}).get("coin", "na")).lower(),
            actual_r=r, expected_r=0.39,
            meta={"via": "consolidate", "ep_ts": ep.get("ts")})
        n += 1
    return n


def _gist_lessons():
    """Distilasi episod jadi lessons (semantic): pola menang/kalah per koin,
    anomali yang berulang. Menimpa file (schema sederhana, versi naik)."""
    eps = hippo.recall(limit=hippo.RETAIN_MAX)
    per_coin = defaultdict(lambda: {"w": 0, "l": 0, "r_sum": 0.0})
    anomaly = defaultdict(int)
    for ep in eps:
        c = ep.get("ctx", {}).get("coin")
        if ep.get("kind") == "trade" and ep.get("r") is not None and c:
            if ep["r"] > 0:
                per_coin[c]["w"] += 1
            else:
                per_coin[c]["l"] += 1
            per_coin[c]["r_sum"] += ep["r"]
        elif ep.get("kind") == "anomaly" and c:
            anomaly[c] += 1
    lessons = _load(LESSONS, {"version": 1, "updated": None, "by_coin": {},
                              "anomaly_counts": {}})
    for c, d in per_coin.items():
        n = d["w"] + d["l"]
        if n < MIN_TRADES_GIST:
            continue  # sampel terlalu tipis — bukan pengetahuan
        wr = d["w"] / n
        entry = {"n": n, "win_ratio": round(wr, 2), "sum_r": round(d["r_sum"], 2)}
        old = lessons["by_coin"].get(c)
        # REM-proteksi: lesson baru hanya menimpa jika beda JAUH (bukan noise)
        if old and abs(old["win_ratio"] - wr) < 0.15 and old["n"] >= n:
            continue
        lessons["by_coin"][c] = entry
    for c, k in anomaly.items():
        lessons["anomaly_counts"][c] = max(
            lessons["anomaly_counts"].get(c, 0), k)
    lessons["updated"] = time.strftime("%F %T", time.gmtime()) + "Z"
    lessons["version"] = lessons.get("version", 1) + 1
    os.makedirs(os.path.dirname(LESSONS), exist_ok=True)
    json.dump(lessons, open(LESSONS, "w"), indent=1)
    return len(lessons["by_coin"])


def _mark_upto():
    eps = hippo.recall(limit=1)
    if eps:
        json.dump({"ts": eps[0].get("ts", "")}, open(MARK, "w"))


def lessons():
    return _load(LESSONS, {"version": 0, "by_coin": {}})


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
