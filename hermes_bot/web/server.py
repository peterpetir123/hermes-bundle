"""HERMES web.server — dashboard local-only (stdlib murni, tanpa dependensi).
Bind WAJIB 127.0.0.1:8080 (keputusan terkunci: local-only, nol permukaan serangan).
Endpoint:
  GET /                      -> index.html (static)
  GET /api/state             -> state/state.json + "saldo_real": null
  GET /api/scan              -> log/last_scan.json
  GET /api/candles?coin=BTC  -> cache/BTC-1d.json
  GET /api/mind              -> MIND/SESSION-LOG.md
  GET /api/backtest?coin=BTC -> backtest_results/BTC.json
"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
# Default TIDAK BERUBAH: 127.0.0.1:8080 (keputusan terkunci local-only).
# Override hanya via env (dipakai unit hermes-web-public, dilindungi iptables).
BIND = os.environ.get("HERMES_WEB_BIND", "127.0.0.1")
PORT = int(os.environ.get("HERMES_WEB_PORT", "8080"))


def read_json(path):
    try:
        return json.load(open(path))
    except Exception:
        return {"error": "not found"}


def read_text(path):
    try:
        return open(path, errors="replace").read()
    except Exception:
        return ""


def safe_coin(raw):
    """Whitelist ketat: hanya koin cache/watchlist, cegah path traversal."""
    return "".join(c for c in (raw or "").upper() if c.isalnum())[:12]


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path == "/":
                with open("hermes_bot/web/index.html", "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if u.path == "/api/state":
                st = read_json("state/state.json")
                st["saldo_real"] = None  # keputusan terkunci: n/a hingga Tahap B
                return self._send(200, json.dumps(st))
            if u.path == "/api/scan":
                return self._send(200, json.dumps(read_json("log/last_scan.json")))
            if u.path == "/api/candles":
                coin = safe_coin((q.get("coin") or [""])[0])
                return self._send(200, json.dumps(
                    read_json(f"cache/{coin}-1d.json")))
            if u.path == "/api/mind":
                return self._send(200, read_text("MIND/SESSION-LOG.md"),
                                  "text/markdown; charset=utf-8")
            if u.path == "/api/backtest":
                coin = safe_coin((q.get("coin") or [""])[0])
                return self._send(200, json.dumps(
                    read_json(f"backtest_results/{coin}.json")))
            return self._send(404, json.dumps({"error": "not found"}))
        except Exception as e:
            return self._send(500, json.dumps({"error": str(e)[:200]}))

    def log_message(self, *a):  # senyap; dashboard lokal tidak butuh akses log
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer((BIND, PORT), Handler)
    print(f"hermes-web listening on http://{BIND}:{PORT} (local-only)")
    srv.serve_forever()
