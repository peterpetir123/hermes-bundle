"""HERMES core.indicators — formula BEKU vault. Tanpa pustaka luar."""


def atr(rows, n=14):
    if len(rows) < n + 1:
        return 0.0
    trs = []
    for i in range(len(rows) - n, len(rows)):
        h, l, pc = rows[i][2], rows[i][3], rows[i - 1][4]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs) / n


def sma(closes, n=100):
    if len(closes) < n:
        return None
    return sum(closes[-n:]) / n


def er_percentile(closes, win=20, lookback=252):
    """Kaufman ER percentile vs window lookback. >=0.55 = tren efisien."""
    if len(closes) < lookback + win:
        return None
    def er(j):
        num = abs(closes[j] - closes[j - win])
        den = sum(abs(closes[k] - closes[k - 1]) for k in range(j - win + 1, j + 1))
        return num / den if den else 0.0
    hist = [er(j) for j in range(len(closes) - lookback, len(closes) - 1)]
    cur = er(len(closes) - 1)
    return sum(1 for x in hist if x <= cur) / len(hist)


def high_n(rows, n=40):
    """High n bar terakhir yang SUDAH CLOSE (exclude bar berjalan)."""
    if len(rows) < n + 1:
        return None
    return max(r[2] for r in rows[-n - 1:-1])


def vol_ratio(rows, n=20):
    if len(rows) < n + 1:
        return 0.0
    avg = sum(r[5] for r in rows[-n - 1:-1]) / n
    return rows[-1][5] / avg if avg else 0.0
