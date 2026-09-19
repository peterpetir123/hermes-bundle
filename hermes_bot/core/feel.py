"""HERMES v2 core.feel — Perasaan: state afektif dengan mood + regulasi.

Latar riset (lihat /root/hermes-mind/notes/brain-research/):
1. Insiden GPT-6 Astra (Vals AI, Sep 2026): creeper meledakkan chest ->
   "trauma" -> hours farming potatoes + paranoia objek hijau. PELAJARANNYA:
   emosi reaktif TANPA dekay/regulasi = perilaku dysfunctional (over-generalize,
   paralysis). Itu bug, bukan fitur — dan justru kasus belajar terbaik.
2. OCC model (Ortony/Clore/Collins): emosi = valenced appraisal of events.
   Event-based: joy/distress. Prospect-based: hope/fear/relief/disappointment.
3. Affect circumplex: emosi = (valence, arousal), bukan label tunggal.
4. Mood = rata-rata lambat dari emosi faset; mempengaruhi bias (mood-congruent).
5. Regulasi (reappraisal, Ochsner/Gross): emosi kuat meluruh; prefrontal
   menurunkan amigdala. Tanpa decay -> trauma permanen ala Astra.

Desain Hermes (jujur & aman):
- Emosi = event-driven appraisal (OCC subset 8 emosi) -> (valence, arousal).
- Mood = EMA lambat valence (half-life ~1 hari) -> bias halus, bukan blokir.
- TRAUMA GUARD: event sangat negatif boleh bikin marker tajam TAPI wajib
  decay eksponensial + cooldown "safe-mode" terbatas (max N jam, ala
  circuit-breaker) — BUKAN paralysis tanpa batas seperti Astra.
- Semua angka tertulis di sini (ponytail #3), report-only, 0 LLM.
"""
import json, math, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, "state", "feel.json")

MOOD_HALF_LIFE_H = 24.0    # mood meluruh ke 50% dalam 24 jam
SAFE_MODE_MAX_H = 3.0      # batas paralysis ala-Astra: maksimal 3 jam mundur
SAFE_MODE_TRIGGER = -2.0   # shock score yang memicu safe-mode (sekitar -3R di RPE)
SHOCK_DECAY_H = 6.0        # shock meluruh cukup cepat (6 jam half-life)


def _now():
    return time.time()


def _load():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"mood_valence": 0.0, "mood_ts": None, "shocks": [],
                "safe_until": None, "last_event": None}


def _save(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE, "w"), indent=1)


def _decay_shocks(s, now=None):
    """Shock lama meluruh eksponensial (reappraisal: emosi kuat meluruh)."""
    now = now or _now()
    alive = []
    for sh in s.get("shocks", []):
        age_h = (now - sh["t"]) / 3600.0
        v = sh["v"] * math.pow(0.5, age_h / SHOCK_DECAY_H)
        if abs(v) > 0.05:
            alive.append({"t": sh["t"], "v": round(v, 3), "why": sh.get("why")})
    s["shocks"] = alive
    return sum(x["v"] for x in alive)


def _update_mood(s, valence, now=None):
    """Mood = EMA lambat dgn half-life (bukan rata2 selamanya)."""
    now = now or _now()
    if s.get("mood_ts"):
        dt_h = (now - s["mood_ts"]) / 3600.0
        w = math.pow(0.5, dt_h / MOOD_HALF_LIFE_H)   # bobot mood lama meluruh
        s["mood_valence"] = round(s["mood_valence"] * w + valence * (1 - w), 3)
    else:
        s["mood_valence"] = round(valence, 3)
    s["mood_ts"] = now


def appraise(event, intensity=1.0, note=None, now=None):
    """OCC subset: satu kejadian -> emosi (valence, arousal, label).
    event: trade_win|trade_loss|anomaly|alarm|record|streak_up|streak_down|shutdown
    intensity: 0..1+ (besar kejatan = vol/nilai/gain)"""
    now = now or _now()
    table = {
        # event: (valence -1..+1, arousal 0..1, label OCC-ish)
        "trade_win":   (0.6,  0.5, "joy"),
        "record":      (0.8,  0.7, "joy-high"),
        "trade_loss":  (-0.5, 0.5, "distress"),
        "anomaly":     (-0.2, 0.6, "alertness"),   # bukan takut; waspada
        "alarm":       (-0.4, 0.8, "fear-tinged"),
        "streak_up":   (0.5,  0.3, "hope"),
        "streak_down": (-0.5, 0.4, "disappointment"),
        "shutdown":    (-0.7, 0.3, "distress-deep"),
    }
    if event not in table:
        raise ValueError(f"unknown event: {event}")
    v0, a0, label = table[event]
    v = round(max(-1.0, min(1.0, v0 * intensity)), 3)
    a = round(min(1.0, a0 * intensity), 3)

    s = _load()
    _update_mood(s, v, now)
    # shock: hanya kejadian SANGAT buruk yang mengunci perilaku sesaat
    # shock memakai intensitas mentah (clamped -3..3) — satu bencana besar
    # harus cukup memicu guard; valence yang ter-clamp -1 tidak pernah cukup
    if v <= -0.6:
        raw = round(max(-3.0, min(3.0, -intensity)), 2)
        s.setdefault("shocks", []).append({"t": now, "v": raw, "why": note or event})
    shock_total = _decay_shocks(s, now)
    # safe-mode: kuncinya TEPAT ala circuit breaker — ada batas waktu keras
    if shock_total <= SAFE_MODE_TRIGGER:
        until = now + SAFE_MODE_MAX_H * 3600
        if not s.get("safe_until") or s["safe_until"] < until:
            s["safe_until"] = until
    s["last_event"] = {"ts": now, "event": event, "valence": v,
                       "arousal": a, "label": label, "note": note}
    _save(s)
    return s["last_event"]


def state():
    """State afektif sekarang: mood, shock aktif, safe-mode. Mikrodetik."""
    s = _load()
    shock_total = _decay_shocks(s)
    _save(s)
    in_safe = bool(s.get("safe_until") and s["safe_until"] > _now())
    remain_h = max(0.0, (s.get("safe_until", 0) - _now()) / 3600.0) if in_safe else 0.0
    mood = s.get("mood_valence", 0.0)
    # bias mood-congruent: mood jelek -> sedikit pesimis pada semua marker
    bias = round(max(-0.2, min(0.2, mood * 0.4)), 3)
    return {"mood": mood, "shock_total": round(shock_total, 2),
            "safe_mode": in_safe, "safe_remaining_h": round(remain_h, 1),
            "bias": bias, "last_event": s.get("last_event")}


def applies_now():
    """Fast-path guard untuk keputusan: boleh lanjut atau safe-mode."""
    st = state()
    if st["safe_mode"]:
        return False, f"safe-mode {st['safe_remaining_h']}h lagi (shock {st['shock_total']})"
    return True, f"mood={st['mood']:+.2f} bias={st['bias']:+.2f}"


if __name__ == "__main__":
    import tempfile, os as _os
    # smoke di store terisolasi
    orig = STATE
    tmp = tempfile.mkdtemp()
    STATE = _os.path.join(tmp, "feel.json")
    # 1. kejadian biasa: mood bergeser halus
    appraise("trade_win", 1.0)
    st = state()
    assert 0 < st["mood"] <= 0.6, st
    # 2. TRAUMA ala Astra: shock besar -> safe-mode ON tapi TERBATAS
    appraise("trade_loss", 3.0, note="semua posisi kena SL sekaligus")
    st = state()
    assert st["safe_mode"] and st["safe_remaining_h"] <= SAFE_MODE_MAX_H
    assert st["shock_total"] <= -2.0
    ok, why = applies_now()
    assert not ok, why
    # 3. reappraisal: setelah 6.5 jam, shock meluruh di bawah trigger
    future = _now() + 6.5 * 3600
    s = _load(); _decay_shocks(s, future)
    assert sum(x["v"] for x in s["shocks"]) > SAFE_MODE_TRIGGER
    # dan safe_until lewat -> bebas
    assert not (s["safe_until"] > future)
    STATE = orig
    print("feel smoke PASS: mood bergeser, trauma memicu safe-mode TERBATAS, decay meluruh")
