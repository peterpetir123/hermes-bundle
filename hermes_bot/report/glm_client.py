"""HERMES report.glm_client — GLM 5.3 via juan router (OpenAI-compatible)."""
import json, os, urllib.request


def chat(messages, model="glm-5.3-flash", temperature=0.3, max_tokens=1200):
    base = os.environ.get("LLM_BASE_URL", "")
    key = os.environ.get("LLM_API_KEY", "")
    if not base or not key:
        return None
    try:
        req = urllib.request.Request(
            f"{base.rstrip('/')}/chat/completions",
            json.dumps({"model": os.environ.get("LLM_MODEL", model),
                        "messages": messages, "temperature": temperature,
                        "max_tokens": max_tokens, "stream": False}).encode(),
            {"Content-Type": "application/json",
             "User-Agent": "Mozilla/5.0",
             "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            msg = json.loads(r.read().decode())["choices"][0]["message"]
            return msg.get("content") or msg.get("reasoning_content", "")
    except Exception as e:
        return f"GLM_ERROR: {str(e)[:120]}"
