"""HERMES core.learn — sesi belajar mandiri (digerakkan flag LEARN).
REPORT-ONLY SELAMANYA: hasil belajar = insight + proposal di MIND/,
TIDAK PERNAH mengubah config.yaml / engine / sizing / eksekusi.
Inovasi hanya boleh masuk via jalur bukti: backtest (n>=100, PF>=1.1,
totR>0, MC p95) + persetujuan Nahkoda (MIND/KEPUTUSAN.md).

Sumber: HNRSS (topik berputar) — stdlib murni, konten di-strip jadi teks,
dibatasi 15KB, TIDAK PERNAH dieksekusi (hanya dibaca + dirangkum GLM).
1 sesi/hari saat LEARN aktif -> hemat token (1 panggilan GLM/sesi).
"""
import html as htmlmod
import urllib.parse
import json, os, re, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# load .env sederhana (cron standalone tidak lewat run_scan) — bug temuan Hermes
_env = os.path.join(os.getcwd(), ".env")
if os.path.exists(_env):
    for _line in open(_env):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

UA = {"User-Agent": "Mozilla/5.0"}  # CF 1010-blocker: UA python-urllib diblok
CACHE = "cache"
JOURNAL = "MIND/PEMBELAJARAN.md"
BACKLOG = "MIND/BACKLOG.md"
MAX_TEXT = 15000
TOPICS = ["breakout trading", "trend following", "backtesting pitfalls",
          "position sizing", "market regime filter", "trailing stop",
          "quantitative trading research", "crypto volatility patterns",
          "trading strategy overfitting", "ATR based risk"]

SYSTEM = (
    "Kamu Hermes Learner. Tugasmu merangkum materi untuk bot trading DON-D1 "
    "breakout (trigger rolling 40d-high + 0.15 ATR, SL 3 ATR, trail 3.5 ATR, "
    "regime UP-only, long-only, quarter-Kelly 6.7%, max 3 posisi). POLA PIKIR "
    "WAJIB: (1) report-only — tidak ada saran eksekusi langsung; (2) parameter "
    "beku — usulan ubah parameter WAJIB lewat backtest dulu (gerbang: n>=100, "
    "PF>=1.1, totR>0, MC p95 positif); (3) skeptis pada overfitting; (4) "
    "sederhana > pintar (stdlib > dependency). Format jawaban Bahasa Indonesia:\n"
    "INSIGHT: <maks 5 poin inti dari materi>\n"
    "RELEVANSI: <bagaimana ini menyentuh Hermes, atau 'tidak relevan'>\n"
    "PROPOSAL: <jika layak: satu ide konkret + SYARAT BUKTINYA; jika tidak: '-'>"
)


def _fetch(url, timeout=20, cap=MAX_TEXT * 3):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(cap).decode("utf-8", "replace")


def _to_text(raw):
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", raw)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t)
    return re.sub(r"\s+", " ", t).strip()[:MAX_TEXT]


def _pick_source():
    """Ambil 1 artikel belum dipelajari dari topik berputar. None jika habis."""
    seen = set()
    try:
        seen = set(json.load(open(f"{CACHE}/learn_seen.json")))
    except Exception:
        pass
    idx = int(time.time() // 86400) % len(TOPICS)
    for i in range(len(TOPICS)):
        q = urllib.parse.quote(TOPICS[(idx + i) % len(TOPICS)])
        try:
            xml = _fetch(f"https://hnrss.org/newest?q={q}&limit=5")
        except Exception:
            continue
        links = re.findall(r"<link>(https?://[^<]+)</link>", xml)[1:]  # [0]=channel
        titles = re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", xml)[1:]
        for url, title in zip(links, titles):
            if url.lower().split("?")[0].endswith((".pdf", ".png", ".jpg", ".mp4")):
                continue  # bukan artikel — jangan buang panggilan GLM
            if url not in seen:
                return {"url": url, "title": htmlmod.unescape(title)}
    return None


def run_session():
    """1 sesi belajar. Return ringkasan utk Telegram / cron log."""
    if not os.path.exists("LEARN"):
        return "learn: flag LEARN tidak ada — /learn untuk mengaktifkan"
    try:
        path = f"{CACHE}/learn_last.json"
        last = json.load(open(path))
        age = time.time() - os.path.getmtime(path)
        # sukses blokir 24 jam; gagal hanya 1 jam (cron hourly boleh ulang)
        ttl, ket = (3600, "gagal sebelumnya — ulang jam berikutnya") \
            if last.get("gagal") else (86400, f"sudah jalan {last.get('ts', '')} — besok lagi")
        if age < ttl:
            return f"learn: {ket}"
    except Exception:
        pass
    src = _pick_source()
    if not src:
        return "learn: tidak ada artikel baru di 10 topik — coba lagi besok"
    try:
        body = _to_text(_fetch(src["url"]))[:8000]  # ponytail: 8KB cukup utk insight
        if len(body) < 400:
            raise ValueError("konten terlalu pendek (mungkin halaman JS)")
        from hermes_bot.report.glm_client import chat
        msgs = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                 f"Judul: {src['title']}\nURL: {src['url']}\n\nIsi:\n{body}"}]
        out = chat(msgs, max_tokens=2000) or chat(msgs, max_tokens=2000)
        # router sesekali kembalikan kosong -> 1 retry cukup
        # PENTING: chat() gagal mengembalikan "GLM_ERROR: ..." (bukan None)
        if not out or out.startswith("GLM_ERROR"):
            raise ValueError((out or "GLM kosong setelah retry")[:150])
    except Exception as e:
        json.dump({"ts": time.strftime("%F %T UTC"), "url": src["url"],
                   "gagal": str(e)[:150]},
                  open(f"{CACHE}/learn_last.json", "w"))  # gagal pun dicatat agar tak menembak GLM
        return f"learn: gagal ({str(e)[:120]}) — dicatat, tidak fatal"

    ts = time.strftime("%F %T UTC", time.gmtime())
    entry = (f"\n## {ts}\n**Sumber:** [{src['title']}]({src['url']})\n\n"
             f"{out.strip()}\n")
    os.makedirs("MIND", exist_ok=True)
    with open(JOURNAL, "a") as f:
        f.write(entry)
    if "PROPOSAL:" in out and "PROPOSAL: -" not in out:
        with open(BACKLOG, "a") as f:
            f.write(f"\n## [LEARN {ts}] Usulan dari {src['title']}\n"
                    f"{out.split('PROPOSAL:', 1)[1].strip()[:800]}\n"
                    f"-> MENUNGGU SYARAT BUKTI + keputusan Nahkoda.\n")
    seen = []
    try:
        seen = json.load(open(f"{CACHE}/learn_seen.json"))
    except Exception:
        pass
    seen.append(src["url"])
    json.dump(seen[-200:], open(f"{CACHE}/learn_seen.json", "w"))
    json.dump({"ts": ts, "url": src["url"]},
              open(f"{CACHE}/learn_last.json", "w"))
    first = out.strip().split("RELEVANSI:")[0][:300]
    return f"🎓 sesi belajar selesai\nSumber: {src['title']}\n{first}…\nJurnal: MIND/PEMBELAJARAN.md"


if __name__ == "__main__":
    # smoke offline: strip-tag harus bersih; guard flag dicek sesuai kondisi
    t = _to_text("<script>x=1</script><p>Halo &amp; hai</p><style>y</style>")
    assert t == "Halo & hai", repr(t)
    if not os.path.exists("LEARN"):
        assert "LEARN tidak ada" in run_session()  # tanpa flag -> aman berhenti
    print("learn smoke PASS (offline)")
    if "--run" in sys.argv:  # manual: python -m hermes_bot.core.learn --run
        print(run_session())
