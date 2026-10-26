"""Real price data - NO GUESS rule.
Data sirf Yahoo Finance (free) se aata hai. Agar data nahi milta to
function ERROR deta hai, kabhi andaze se price NAHI banata.
Free Yahoo data ~15 minute delayed hota hai, ye exchange ka
tick-by-tick real-time nahi hai. Final buy se pehle broker app ka
live price zaroor cross-check karo, kyunki price tab tak badal sakta hai.
"""
import time
from datetime import datetime, timezone

import pandas as pd


def _flatten(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()


def fetch_data(symbol, period="1y", interval="1d"):
    """Purana function - compatibility ke liye. Data na mile to ValueError."""
    df, _meta = fetch_data_with_meta(symbol, period=period, interval=interval)
    return df


def fetch_data_with_meta(symbol, period="1y", interval="1d"):
    """Returns (df, meta). meta me source, last_date, rows, fetched_at aur stale flag hota hai.
    3 baar retry karta hai. Teenon fail hon to ValueError - guess nahi karta."""
    try:
        import yfinance as yf
    except ImportError as e:
        raise SystemExit(
            "yfinance install nahi hai. Chalao: pip install -r requirements.txt"
        ) from e

    last_error = None
    for attempt in range(3):
        try:
            df = yf.download(symbol, period=period, interval=interval,
                             auto_adjust=True, progress=False, timeout=20)
            if df is not None and len(df) > 0:
                df = _flatten(df)
                if len(df) > 0:
                    last_date = df.index[-1]
                    # last_date timezone-aware ho sakta hai, date nikaalo
                    last_day = last_date.date() if hasattr(last_date, "date") else last_date
                    today = datetime.now(timezone.utc).date()
                    age_days = (today - last_day).days if hasattr(last_day, "year") else 999
                    meta = {
                        "source": "Yahoo Finance (free, ~15 min delayed)",
                        "symbol": symbol,
                        "period": period,
                        "interval": interval,
                        "rows": int(len(df)),
                        "last_date": str(last_day),
                        "age_days": int(age_days),
                        # 7 din se zyada purana data = stale, us par BUY mat do
                        "is_stale": bool(age_days > 7),
                        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                        "attempt": attempt + 1,
                    }
                    return df, meta
        except Exception as e:  # noqa: BLE001 - retry ke liye sab pakdo
            last_error = e
            time.sleep(2)
    raise ValueError(
        f"{symbol} ke liye REAL data nahi mila ({last_error}). "
        "Price ka andaza mat lagao. 2 minute baad dobara try karo, "
        "ya broker app ka price/date user se lekar aage badho."
    )


def fetch_quote(symbol):
    """Sabse taaza quote: pehle 1-minute intraday, na mile to daily last close.
    Returns dict with source, timestamp aur delay warning. Kabhi guess nahi."""
    try:
        import yfinance as yf
    except ImportError as e:
        raise SystemExit("yfinance install nahi hai.") from e
    # Intraday try
    for period, interval in [("1d", "1m"), ("5d", "1d")]:
        try:
            df = yf.download(symbol, period=period, interval=interval,
                             auto_adjust=True, progress=False, timeout=20)
            if df is not None and len(df) > 0:
                df = _flatten(df)
                price = float(df["Close"].iloc[-1])
                return {
                    "symbol": symbol,
                    "price": round(price, 2),
                    "timestamp": str(df.index[-1]),
                    "source": "Yahoo Finance",
                    "delay_warning": (
                        "Free data ~15 minute delayed ho sakta hai. "
                        "Buy karne se pehle broker app ka live price check karo."
                    ),
                }
        except Exception:
            continue
    raise ValueError(f"{symbol} ka live quote nahi mila. Andaza mat lagao.")


def last_price(df):
    return float(df["Close"].iloc[-1])
