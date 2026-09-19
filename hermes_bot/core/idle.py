"""HERMES v2 core.idle — Default Mode Network: pikiran saat menganggur.

Prinsip otak (Raichle 2001; Buckner; Christoff): ketika tidak ada tugas eksternal,
jaringan mode-default aktif — MEMUTAR ULANG pengalaman dan MENSIMULASIKAN masa
depan (mental time travel). Bukan pemborosan: otak menghabiskan ~20% energi total
tubuh justru untuk aktivitas intrinsik ini (Raichle, "restless brain").

Dua fungsi DMN yang ditiru:
  1. Replay kontrafaktual (Buzsáki): "bagaimana kalau ekspektasinya berbeda?"
  2. Prospeksi: "kalau pola ini berulang, apa yang mungkin terjadi?"

Dua bahaya yang dicegah (pelajaran insiden GPT-6 Astra × creeper):
  1. RUMINASI — memutar skenario buruk yang sama berulang-ulang. Di sini: key
     pikiran yang berulang >= RUMINATION_REPEAT kali / 24 jam ditandai ruminasi
     dan DIHENTIKAN (bukan terus diputar).
  2. Terlalu banyak berpikir saat terancam. Di otak, ancaman MENSUPRESI DMN.
     Di sini: safe-mode (core.feel) -> DMN mati otomatis.

REPORT-ONLY: modul ini tidak menyentuh config/engine/sizing/entry. Keluarannya
adalah HIPOTESIS untuk BACKLOG (butuh backtest + persetujuan Nahkoda), bukan aksi.

Stdlib murni, 0 LLM, mikrodetik.
"""
import json, os, time

from hermes_bot.core import feel, hippo, rpe

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORE = os.path.join(ROOT, "state", "idle.json")
MAX_THOUGHTS = 5          # DMN tetap berbatas: tak semua pikiran dilaporkan
RUMINATION_REPEAT = 3     # key sama >=3x/24 jam -> ruminasi, hentikan
WINDOW_H = 24
EXPECT_BASE = 0.39        # ekspektasi statis tahap 1 (samakan dgn core.rpe)
MIN_N = 3                 # simulasi butuh minimal 3 kejadian


def _now():
    return time.time()


def _ts(t=None):
    return time.strftime("%F %T", time.gmtime(t or _now())) + "Z"


def _load():
    try:
        return json.load(open(STORE))
    except Exception:
        return {"version": 1, "n_runs": 0, "thoughts": [], "flags": [],
                "keys": {}}


def _save(s):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    json.dump(s, open(STORE, "w"), indent=1, ensure_ascii=False)


def _trades():
    return [e for e in hippo.recall(kind="trade", limit=500)
            if e.get("r") is not None]


def _think_counterfactual(trades):
    """Replay kontrafaktual: apa yang berubah bila ekspektasi per-koin (bukan
    konstan 0.39R)? Sinyal dopamin jadi lebih tajam atau cuma berisik?"""
    by = {}
    for t in trades:
        by.setdefault((t.get("ctx") or {}).get("coin", "?"), []).append(t["r"])
    fixed = adapt = 0.0
    n = 0
    for coin, rs in by.items():
        if len(rs) < MIN_N:
            continue
        mean = sum(rs) / len(rs)
        for r in rs:
            fixed += rpe.rpe(r, EXPECT_BASE)
            adapt += rpe.rpe(r, mean)
            n += 1
    if not n:
        return None
    delta = adapt - fixed
    arah = "menajam" if delta > 0.05 else ("meredam" if delta < -0.05 else "netral")
    return {"kind": "kontrafaktual", "key": "kontrafaktual:expectancy-adaptif",
            "subject": "expectancy-adaptif", "salience": round(min(3.0, abs(delta) + 0.5), 2),
            "text": (f"kalau ekspektasi per-koin dipakai (bukan {EXPECT_BASE}R konstan), "
                     f"total sinyal dopamin {fixed:+.2f} -> {adapt:+.2f} ({arah} {delta:+.2f}) "
                     f"atas {n} trade"),
            "usul": "kandidat BACKLOG: uji expectancy adaptif per koin (butuh backtest)"}


def _think_prospective(ls):
    """Prospeksi: kalau pola koin ini berulang, apa yang mungkin terjadi?"""
    out = []
    for coin, d in (ls.get("by_coin") or {}).items():
        if d.get("n", 0) < MIN_N + 2:
            continue
        ev = d["sum_r"] / d["n"]
        if abs(ev) < 0.05:
            continue
        arah = "positif" if ev > 0 else "negatif"
        out.append({"kind": "prospeksi", "key": f"prospeksi:{coin}", "subject": coin,
                    "salience": round(min(2.5, abs(ev)), 2),
                    "text": (f"kalau pola {coin} berulang: EV ~{ev:+.2f}R/trade "
                             f"(win_ratio {d['win_ratio']}, n={d['n']}) — kecenderungan {arah}"),
                    "usul": "pantau; bukan aksi"})
    return out


def _think_calibration(ls):
    """Kalibrasi intuisi: apakah somatic marker sejalan dgn hasil nyata?"""
    from hermes_bot.core import somatic
    out = []
    for coin, d in (ls.get("by_coin") or {}).items():
        if d.get("n", 0) < MIN_N + 2:
            continue
        v, action, _ = somatic.mark(coin)
        real = (d["win_ratio"] - 0.5) * 2
        selaras = (v >= 0) == (real >= 0)
        if not selaras:
            out.append({"kind": "kalibrasi", "key": f"kalibrasi:{coin}", "subject": coin,
                        "salience": 1.5,
                        "text": (f"intuisi vs realitas TIDAK selaras utk {coin}: "
                                 f"marker {v:+.2f} ({action}) tapi win_ratio {d['win_ratio']}"),
                        "usul": "periksa bobot marker saat tuning (jangan ubah sekarang)"})
    return out


def _think_anomaly(ls):
    out = []
    for coin, n in (ls.get("anomaly_counts") or {}).items():
        if n >= 2:
            out.append({"kind": "pola", "key": f"pola:anomali:{coin}", "subject": coin,
                        "salience": 1.0,
                        "text": f"{n} anomali {coin} tercatat — pola berulang, bukan kejutan tunggal",
                        "usul": "tunggu data; lapor bila berlanjut"})
    return out


def think(force=False):
    """Satu sesi menganggur. Return dict ringkas (juga ditulis ke state/idle.json)."""
    s = _load()
    ok, why = feel.applies_now()
    if not ok and not force:
        s["last_run"] = _ts()
        s["mode"] = "suppressed"
        s["suppressed_reason"] = why
        _save(s)
        return {"mode": "suppressed", "reason": why, "n": 0, "thoughts": []}

    ls = __import__("hermes_bot.core.consolidate", fromlist=["lessons"]).lessons()
    trades = _trades()
    cands = [c for c in (_think_counterfactual(trades),) if c]
    cands += _think_prospective(ls) + _think_calibration(ls) + _think_anomaly(ls)

    # --- gerbang ruminasi (pelajaran Astra) ---
    now = _now()
    keys = {k: [t for t in v if now - t < WINDOW_H * 3600]
            for k, v in (s.get("keys") or {}).items()}
    fresh, ruminated = [], []
    for c in cands:
        hist = keys.setdefault(c["key"], [])
        if len(hist) >= RUMINATION_REPEAT:
            ruminated.append(c["key"])
            continue
        fresh.append(c)
    fresh.sort(key=lambda c: -c["salience"])
    fresh = fresh[:MAX_THOUGHTS]
    for c in fresh:
        keys[c["key"]].append(now)

    flags = []
    if ruminated:
        flags.append({"ts": _ts(), "flag": "ruminasi",
                      "keys": ruminated,
                      "note": "pikiran sama diputar >=3x/24j -> dihentikan (bukan diputar terus)"})

    s.update({"version": 1, "last_run": _ts(), "mode": "idle",
              "n_runs": s.get("n_runs", 0) + 1,
              "thoughts": fresh, "flags": (s.get("flags") or [])[-20:] + flags,
              "keys": keys})
    _save(s)
    return {"mode": "idle", "n": len(fresh), "ruminasi": ruminated,
            "thoughts": fresh, "flags": flags}


if __name__ == "__main__":
    import tempfile
    orig, STORE = STORE, os.path.join(tempfile.mkdtemp(), "idle.json")
    try:
        r1 = think()
        assert r1["mode"] in ("idle", "suppressed"), r1["mode"]
        if r1["mode"] == "idle":
            assert isinstance(r1["thoughts"], list) and len(r1["thoughts"]) <= MAX_THOUGHTS
            # putar pikiran yang sama berulang -> harus muncul flag ruminasi
            seen_rum = []
            for _ in range(RUMINATION_REPEAT + 2):
                seen_rum += think()["ruminasi"]
            assert seen_rum, "gerbang ruminasi tidak memicu"
            print("idle smoke PASS: DMN berpikir, ruminasi dihentikan otomatis")
        else:
            print(f"idle smoke PASS: DMN tersupresi oleh ancaman ({r1['reason']})")
    finally:
        STORE = orig
