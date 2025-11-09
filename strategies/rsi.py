# strategies/rsi.py
import pandas as pd

def get_rsi_signal(closes, period=14):
    series = pd.Series(closes)
    delta = series.diff().dropna()
    up = delta.clip(lower=0).ewm(alpha=1/period).mean()
    down = -delta.clip(upper=0).ewm(alpha=1/period).mean()
    rs = up / down
    rsi = 100 - (100 / (1 + rs))
    last = rsi.iloc[-1]
    if last > 70:
        return -1
    elif last < 30:
        return 1
    else:
        return 0
