#!/usr/bin/env bash
# Fase 0: akses + latensi. Gerbang: HTTP 200 semua, median <400ms
FAIL=0
for url in https://api.hyperliquid.xyz https://api.hyperliquid-testnet.xyz https://gamma-api.polymarket.com https://www.okx.com https://aws.okx.com; do
  code=$(curl -o /dev/null -s -w "%{http_code}" --max-time 10 "$url")
  med=$(for i in $(seq 1 10); do curl -o /dev/null -s -w "%{time_total}\n" --max-time 10 "$url"; done | sort -n | awk 'NR==5{printf "%.0f",$1*1000}')
  echo "$url -> HTTP $code | median ${med}ms"
  [ "$code" != "200" ] && FAIL=1
  [ "${med:-999}" -gt 400 ] && FAIL=1
done
curl -s ipinfo.io | head -5
[ "$FAIL" = "0" ] && echo "LULUS" || echo "GAGAL - cek provider/region"
