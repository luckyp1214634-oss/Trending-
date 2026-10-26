"""Stock analysis: trend + momentum + volume se simple score."""
from indicators import add_indicators, support_resistance


def analyse(df):
    df = add_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    price = float(last["Close"])
    score = 0
    reasons = []

    if price > last["EMA50"]:
        score += 1
        reasons.append("Price 50 EMA ke upar hai (uptrend)")
    else:
        score -= 1
        reasons.append("Price 50 EMA ke neeche hai (downtrend)")

    rsi_v = float(last["RSI"])
    if 50 <= rsi_v <= 70:
        score += 1
        reasons.append(f"RSI {rsi_v:.1f} healthy range me hai")
    elif rsi_v > 75:
        reasons.append(f"RSI {rsi_v:.1f} bahut zyada hai - overbought, savdhan")
    elif rsi_v < 30:
        reasons.append(f"RSI {rsi_v:.1f} bahut kam hai - oversold")

    if float(last["MACD_hist"]) > 0:
        score += 1
        reasons.append("MACD positive hai (momentum up)")
    else:
        reasons.append("MACD negative hai (momentum down)")

    if float(last["Volume"]) > float(last["VolAvg20"]):
        score += 1
        reasons.append("Volume average se zyada hai (interest badh raha hai)")
    else:
        reasons.append("Volume average se kam hai")

    support, resistance = support_resistance(df)
    atr_v = float(last["ATR"])
    verdict = "SIGNAL STRONG HAI - checklist ke saath hi socho" if score >= 3 else (
        "WAIT / NO TRADE" if score < 2 else "WEAK - sirf checklist ke saath"
    )
    return {
        "price": round(price, 2),
        "ema20": round(float(last["EMA20"]), 2),
        "ema50": round(float(last["EMA50"]), 2),
        "ema200": round(float(last["EMA200"]), 2),
        "rsi": round(rsi_v, 1),
        "macd_hist": round(float(last["MACD_hist"]), 2),
        "atr": round(atr_v, 2),
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "score": score,
        "reasons": reasons,
        "verdict": verdict,
        "suggested_stop": round(price - 1.5 * atr_v, 2),
        "suggested_target": round(price + 2.5 * atr_v, 2),
    }
