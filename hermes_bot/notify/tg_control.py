"""HERMES tg_control — kontrol Telegram + inbox (stdlib murni, 0 token kecuali /ask).

Perintah (whitelist TELEGRAM_CHAT_ID saja — pesan lain diabaikan + dicatat):
  /off    -> touch KILL   (entry DIBEKUKAN; denyut & monitor tetap jalan)
  /on     -> rm KILL      (entry aktif kembali)
  /status -> mode, equity, posisi, alarm
  /ask <t>-> tanya GLM dengan konteks mesin SAAT INI (report-only, bukan sinyal)
  teks bebas -> dicatat ke MIND/INBOX.md (dibaca Hermes tiap sesi) + konfirmasi
"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

ENV = os.path.join(ROOT, ".env")
if os.path.exists(ENV):
    for line in open(ENV):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from hermes_bot.notify.telegram_bot import _send
from hermes_bot.exec.risk import load_state

API = "https://api.telegram.org/bot{}/{}"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOW = os.environ.get("TELEGRAM_CHAT_ID", "")
INBOX = os.path.join(ROOT, "MIND", "INBOX.md")


def _api(meth, fields, timeout=30):
    req = urllib.request.Request(
        API.format(TOKEN, meth), json.dumps(fields).encode(),
        {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _reply(chat_id, text):
    """Kirim pesan; Markdown hanya jika lolos (teks dengan _/* sering 400)."""
    for pm in ("Markdown", None):
        try:
            fields = {"chat_id": chat_id, "text": text}
            if pm:
                fields["parse_mode"] = pm
            _api("sendMessage", fields)
            return
        except Exception as e:
            last = str(e)[:120]
    print("reply gagal:", last, flush=True)


def _summary():
    st = load_state()
    ls_age = None
    p = "log/last_scan.json"
    if os.path.exists(p):
        ls_age = (time.time() - os.path.getmtime(p)) / 3600
    return st, ls_age


def cmd_status():
    st, age = _summary()
    paused = os.path.exists("PAUSE")
    lines = ["🔧 *HERMES STATUS*",
             f"mesin: {'🛑 PAUSED (dihentikan via /off)' if paused else '🟢 AKTIF — SOP penuh jalan'}",
             f"mode: TESTNET Tahap {st.get('stage', 'A')}",
             f"equity: ${st.get('equity', 0):.2f} · day_pnl: {st.get('day_pnl', 0):+.2f}",
             f"posisi terbuka: {len(st['positions'])}/3 · halted: {st.get('halted')}",
             f"KILL-switch: {'AKTIF (entry beku)' if os.path.exists('KILL') else 'tidak aktif'}",
             f"denyut sinyal terakhir: {age:.1f} jam lalu" if age is not None
             else "denyut: TIDAK ADA DATA"]
    return "\n".join(lines)


def cmd_off(confirm=False):
    st, _ = _summary()
    n_pos = len(st.get("positions", []))
    if n_pos and not confirm:
        return (f"⚠️ *PERINGATAN: {n_pos} posisi TERBUKA* akan tidak dipantau "
                "kalau mesin dihentikan (trailing/close berhenti).\n"
                "Tetap hentikan? Kirim: /off yakin")
    if not os.path.exists("PAUSE"):
        open("PAUSE", "w").write(time.strftime("%Y-%m-%d %H:%M:%S UTC",
                                               time.gmtime()))
    return ("🛑 *HERMES DIHENTIKAN* (PAUSE aktif)\n"
            "Semua analisa, entry, monitor posisi, dan digest BERHENTI.\n"
            "Bot Telegram ini & watchdog tetap hidup.\n"
            "Kirim /on untuk menyalakan kembali, /status untuk cek.")


def cmd_on():
    was = []
    for f in ("PAUSE", "KILL"):
        if os.path.exists(f):
            os.remove(f)
            was.append(f)
    if not was:
        return "🟢 Hermes memang sudah AKTIF — SOP penuh berjalan."
    return ("🟢 *HERMES MENYALA KEMBALI*\n"
            "SOP penuh jalan: sinyal :05 · monitor posisi :10/:40 · "
            "digest 00:15 · watchdog */30.")


def cmd_ask(q):
    """Tanya GLM dengan konteks mesin. Report-only — bukan sinyal, bukan eksekusi."""
    try:
        from hermes_bot.report.glm_client import chat
        st, age = _summary()
        ctx = [
            f"equity={st.get('equity')} day_pnl={st.get('day_pnl')} "
            f"halted={st.get('halted')} KILL={os.path.exists('KILL')} "
            f"posisi={json.dumps(st['positions'])[:400]} "
            f"closed_terakhir={json.dumps(st['closed'][-3:])[:400]} "
            f"scan_terakhir={open('log/last_scan.json').read()[:600]} "
            f"umur_scan_jam={age}"]
        out = chat([{"role": "system", "content":
                     "Kamu Hermes Reporter, asisten status bot trading. "
                     "Jawab RINGKAS (maks 150 kata, Bahasa Indonesia) HANYA "
                     "dari data konteks. DILARANG: saran entry baru, ubah "
                     "parameter, opini arah pasar. Data tidak ada -> n/a."},
                    {"role": "user", "content": f"Konteks: {ctx}\n\nPertanyaan: {q}"}])
        return out or "GLM tidak merespons — coba lagi nanti."
    except Exception as e:
        return f"/ask gagal: {str(e)[:150]}"


def handle_update(msg):
    chat = str(msg.get("chat", {}).get("id", ""))
    if chat != ALLOW:
        # whitelist: catat & diamkan (jangan balas)
        with open("log/tgctl.log", "a") as f:
            f.write(f"{time.strftime('%F %T')} DITOLAK chat={chat}\n")
        return
    text = (msg.get("text") or "").strip()
    low = text.lower()
    if low in ("/off", "/stop"):
        _reply(chat, cmd_off(confirm=(low == "/off yakin" or
                                      text.lower().endswith("yakin"))))
    elif low == "/on":
        _reply(chat, cmd_on())
    elif low in ("/status", "/s"):
        _reply(chat, cmd_status())
    elif low.startswith("/ask"):
        q = text[4:].strip()
        if not q:
            _reply(chat, "pakai: /ask <pertanyaan>")
        else:
            _reply(chat, cmd_ask(q))
    elif low in ("/start", "/help"):
        _reply(chat, "🤖 *HERMES CONTROL*\n"
                     "/status — kondisi mesin\n"
                     "/off — HENTIKAN Hermes total (analisa+entry+monitor+digest)\n"
                     "/off yakin — paksa hentikan meski ada posisi terbuka\n"
                     "/on — nyalakan kembali SOP penuh\n"
                     "/ask <tanya> — tanya status via GLM\n"
                     "teks bebas — masuk inbox Hermes (dibaca sesi berikut)")
    elif text:
        os.makedirs(os.path.dirname(INBOX), exist_ok=True)
        with open(INBOX, "a") as f:
            f.write(f"\n## {time.strftime('%F %T UTC')} (dari Telegram)\n{text}\n")
        _reply(chat, "📥 masuk inbox Hermes — dibaca di sesi berikutnya.\n"
                     "Butuh jawaban cepat soal status? pakai /ask <tanya>")


def main():
    if not TOKEN or not ALLOW:
        print("tg_control: kredensial belum lengkap", flush=True)
        return
    offset = 0
    backoff = 5
    print("tg_control: polling aktif", flush=True)
    while True:
        try:
            r = _api("getUpdates", {"offset": offset, "timeout": 25}, timeout=35)
            if r.get("ok"):
                backoff = 5
                for u in r.get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message") or u.get("edited_message")
                    if msg and (msg.get("text") or "").strip():
                        try:
                            handle_update(msg)
                        except Exception as e:
                            print("handle error:", str(e)[:150], flush=True)
        except Exception as e:
            print("poll error:", str(e)[:150], flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 2, 120)


if __name__ == "__main__":
    main()
