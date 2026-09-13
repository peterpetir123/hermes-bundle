#!/bin/bash
# Wrapper quick tunnel: ekstrak URL trycloudflare -> simpan ke log/tunnel.url
# Dipakai oleh systemd user unit hermes-tunnel.service.
exec /usr/bin/cloudflared tunnel --url http://127.0.0.1:8080 --no-autoupdate 2>&1 | \
  while IFS= read -r line; do
    url=$(printf '%s' "$line" | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | head -1)
    if [ -n "$url" ]; then printf '%s' "$url" > /root/hermes-bundle/log/tunnel.url; fi
    printf '%s\n' "$line"
  done
