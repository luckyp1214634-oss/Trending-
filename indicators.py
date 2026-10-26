"""Chart indicators: RSI, EMA, MACD, ATR, VWAP, Support/Resistance.
Sab calculation sirf price data se hoti hai, koi future price predict nahi karta.
"""
import pandas as pd
import numpy as np


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(close, fast=12, slow=26, signal=9):
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


def atr(df, period=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def add_indicators(df):
    df = df.copy()
    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)
    df["RSI"] = rsi(df["Close"])
    macd_line, sig, hist = macd(df["Close"])
    df["MACD"], df["MACD_signal"], df["MACD_hist"] = macd_line, sig, hist
    df["ATR"] = atr(df)
    df["VolAvg20"] = df["Volume"].rolling(20).mean()
    return df


def support_resistance(df, window=20):
    """Aakhri window ke high/low se simple support/resistance."""
    recent = df.tail(window)
    return float(recent["Low"].min()), float(recent["High"].max())
