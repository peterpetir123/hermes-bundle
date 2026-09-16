"""HERMES report.glm_client — GLM/DeepSeek via juan router (OpenAI-compatible)."""
import json, os, time, urllib.request

# Model terverifikasi dari /v1/models router (2026-09-16), tanpa akses ekstra
MODELS = {
    "glm-5.3-flash": "glm-5.3-flash",
    "deepseek-v4.1-flash": "deepseek-v4.1-flash",
}
RETRY_DELAY = 6  # detik: router mengembalikan "drained/rate-limited"


def chat(messages, model=None, temperature=0.3, max_tokens=1200, retries=2):
    base = os.environ.get("LLM_BASE_URL", "")
    key = os.environ.get("LLM_API_KEY", "")
    model = model or os.environ.get("LLM_MODEL", "glm-5.3-flash")
    if model not in MODELS.values():
        model = MODELS.get(model, model)  # izinkan alias/nama mentah
    if not base or not key:
        return None
    payload = {"model": model, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens,
               "stream": False}
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(
                f"{base.rstrip('/')}/chat/completions",
                json.dumps(payload).encode(),
                {"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0",
                 "Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                msg = json.loads(r.read().decode())["choices"][0]["message"]
                return msg.get("content") or msg.get("reasoning_content", "")
        except Exception as e:
            last = e
            if "rate-limited" in str(e).lower() or "drained" in str(e).lower():
                time.sleep(RETRY_DELAY)  # provider penuh sesaat — coba lagi
                continue
            return f"GLM_ERROR: {str(e)[:120]}"
    return f"GLM_ERROR: habis retry ({str(last)[:120]})"
