"""HERMES core.regime — gate UP/DN/CHOP."""
from .indicators import er_percentile, sma


def classify(rows):
    closes = [r[4] for r in rows]
    erp = er_percentile(closes)
    s100 = sma(closes, 100)
    if erp is None or s100 is None:
        return {"regime": "CHOP", "erp": None, "sma100": None, "valid": False}
    px = closes[-1]
    if erp >= 0.55 and px > s100:
        rg = "UP"
    elif erp >= 0.55 and px < s100:
        rg = "DN"
    else:
        rg = "CHOP"
    return {"regime": rg, "erp": round(erp, 3), "sma100": round(s100, 4), "valid": True}
