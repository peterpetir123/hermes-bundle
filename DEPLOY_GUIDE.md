# DEPLOY — operasional & kenaikan tahap
TAHAP A (default: mode testnet di config.yaml) — order dicatat, tidak dikirim.
  Gerbang naik: >=30 sinyal, error rate <5%, latensi stabil.
TAHAP B (live kecil) — dompet BURNER khusus trading; HL_PRIVATE_KEY di .env;
  atau lebih baik AGENT KEY Hyperliquid (trade-only, tanpa hak withdraw).
  Gerbang: >=50 sinyal sehat + funding dimodelkan.
TAHAP C (agent key penuh + skala) — master key TIDAK PERNAH di VPS.
  Gerbang: >=100 sinyal + PF live >=0.9.

HARIAN: cat log/last_scan.json | log/trades.jsonl | touch KILL = stop darurat.
UBAH PARAMETER: tulis riset -> validate.py LULUS (n>=100, PF>=1.1, totR>0)
  -> baru edit config.yaml. Gagal = bubarkan, catat di journal.
KN (Konsultasi Nahkoda): pakai skills_and_prompts/STAFF_ANALYST_PROMPT.md
  sebagai system-prompt GLM; keputusan = milik Nahkoda, tercatat.
KEAMANAN: .env tidak pernah di-commit; master key tidak pernah di VPS.
