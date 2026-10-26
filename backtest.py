"""Backtest: purane data par strategy ko test karo.
Strategy (simple, seekhne ke liye): Price > EMA50 aur RSI 50-70 ho to BUY,
stop-loss = entry - 1.5*ATR, target = entry + 2.5*ATR.
Ye future profit ki guarantee NAHI hai, sirf pichhla record hai.
"""
from indicators import add_indicators


def backtest(df):
    df = add_indicators(df).reset_index(drop=True)
    trades = []
    i = 20
    while i < len(df) - 1:
        row = df.iloc[i]
        # Entry condition
        if row["Close"] > row["EMA50"] and 50 <= row["RSI"] <= 70:
            entry = float(row["Close"])
            atr_v = float(row["ATR"])
            stop = entry - 1.5 * atr_v
            target = entry + 2.5 * atr_v
            # Aage ke dinon me pehle kya hit hua: stop ya target?
            result = None
            for j in range(i + 1, len(df)):
                low, high = float(df.iloc[j]["Low"]), float(df.iloc[j]["High"])
                if low <= stop:
                    result = ("LOSS", stop - entry)
                    break
                if high >= target:
                    result = ("WIN", target - entry)
                    break
            if result:
                trades.append(result)
                i = j + 1 if 'j' in locals() else i + 1
                continue
        i += 1

    if not trades:
        return {"total_trades": 0, "message": "Is period me koi trade condition nahi bani."}
    wins = [p for r, p in trades if r == "WIN"]
    losses = [p for r, p in trades if r == "LOSS"]
    total_profit = sum(p for _, p in trades)
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0
    profit_factor = (sum(wins) / abs(sum(losses))) if losses else 0
    # Max drawdown (simple): running total ka sabse bada giravat
    running, peak, max_dd = 0, 0, 0
    for _, p in trades:
        running += p
        peak = max(peak, running)
        max_dd = max(max_dd, peak - running)
    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round(100 * len(wins) / len(trades), 1),
        "avg_win_per_share": round(avg_win, 2),
        "avg_loss_per_share": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 2),
        "total_profit_per_share": round(total_profit, 2),
        "max_drawdown_per_share": round(max_dd, 2),
        "warning": "Ye pichhla data hai. Future me yehi result mile, iski guarantee nahi hai.",
    }
