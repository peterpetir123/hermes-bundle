"""HERMES report.daily_reporter — laporan harian via GLM dari RINGKASAN angka."""
import datetime, os
from .glm_client import chat

DIGEST_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "log", "digests")

SYSTEM = (
    "Kamu Reporter Hermes, bot trading kuantitatif. Fondasi: DON-D1 breakout 40d "
    "+ regime UP (erp>=0.55, close>SMA100) + trailing 3.5xATR — tervalidasi "
    "12.465 trade 9 tahun (+78.6R, PF 1.28). Tugas: rapikan angka yang diberikan "
    "jadi laporan Telegram Markdown (Bahasa Indonesia, maks 500 kata). "
    "LARANGAN: tanpa opini arah pasar, tanpa saran entry baru, tanpa ubah "
    "parameter. Data Polymarket = konteks konsensus, BUKAN sinyal entry. "
    "Data tidak ada -> tulis n/a. Sertakan: pasar, posisi, closed, risiko, alarm."
)


def build_summary(state, scans, pm_lines):
    closed = state["closed"][-10:]
    wins = [c for c in closed if c["r"] > 0]
    losses = [c for c in closed if c["r"] <= 0]
    pf = None
    if losses and sum(c["r"] for c in losses) != 0:
        pf = sum(c["r"] for c in wins) / abs(sum(c["r"] for c in losses))
    # probability block (Referensi-Probabilitas.md): Kelly/RoR hanya jika n>=30
    try:
        from hermes_bot.core.probability import summary_lines as prob_lines
        prob = prob_lines(state)
    except Exception:
        prob = []
    # narasi (report-only, MIND/KEPUTUSAN.md): sentimen + berita
    try:
        from hermes_bot.core.sentiment import summary_lines as nar_lines
        nar = nar_lines()
    except Exception:
        nar = []
    return "\n".join([
        f"equity=${state.get('equity', 0):.2f} day_pnl={state.get('day_pnl', 0):+.2f} "
        f"halted={state.get('halted')} stage={state.get('stage')}",
        f"open={len(state['positions'])}/3 "
        + " ".join(f"{p['coin']}@{p['entry']:.4g}" for p in state["positions"]),
        f"closed10 n={len(closed)} "
        + (f"PF={pf:.2f} " if pf else "")
        + " ".join(f"{c['coin']}:{c['r']:+.1f}R" for c in closed[-6:]),
        "scan: " + "; ".join(f"{x['coin']}:{x['status']}({x.get('regime')},vol{x.get('vol_ratio')})"
                             for x in scans),
        "\n".join(pm_lines),
        *prob,
        *nar,
    ])


def save_digest(text):
    """Persistensi digest: Telegram mungkin mati, file tidak."""
    try:
        os.makedirs(DIGEST_DIR, exist_ok=True)
        path = os.path.join(DIGEST_DIR, f"{datetime.date.today().isoformat()}.md")
        with open(path, "w") as f:
            f.write(text)
        return path
    except Exception:
        return None


def generate(state, scans, pm_lines):
    summary = build_summary(state, scans, pm_lines)
    out = chat([{"role": "system", "content": SYSTEM},
                {"role": "user", "content": summary}])
    text = out or summary
    save_digest(text)
    return text
