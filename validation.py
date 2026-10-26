"""1000-baar validation - imaandari ke saath.
Ye 1000 alag future trades NAHI banata. Ye karta hai:
  1. Pichhle 5 saal ke REAL data me har setup dhoondhta hai
     (Price > EMA50 aur RSI 50-70).
  2. Har setup ka asli outcome nikalta hai (10 din ke andar
     target pehle hit hua, stop pehle hit hua, ya kuch nahi hua).
  3. Phir un asli outcomes ko 1000 baar bootstrap resample karta hai
     (matlab purane results ko 1000 baar dobara sample karke
     win-rate ki range nikalta hai).
Agar asli setups 20 se kam hain to sample bahut chhota hai,
us par BUY ka faisla mat lo - ye tool khud bata dega.
"""
import random

from indicators import add_indicators


def validate_strategy(df, hold_days=10, seed=42):
    df = add_indicators(df).reset_index(drop=True)
    outcomes = []  # 1 = win, 0 = loss, 0.5 = neutral (time exit)
    details = []
    for i in range(50, len(df) - 1):
        row = df.iloc[i]
        if not (row["Close"] > row["EMA50"] and 50 <= row["RSI"] <= 70):
            continue
        entry = float(row["Close"])
        atr_v = float(row["ATR"])
        if atr_v == 0:
            continue
        stop = entry - 1.5 * atr_v
        target = entry + 2.5 * atr_v
        outcome = 0.5
        for j in range(i + 1, min(len(df), i + 1 + hold_days)):
            low, high = float(df.iloc[j]["Low"]), float(df.iloc[j]["High"])
            if low <= stop:
                outcome = 0
                break
            if high >= target:
                outcome = 1
                break
        outcomes.append(outcome)
        details.append({"entry": round(entry, 2), "outcome": outcome})

    total = len(outcomes)
    if total == 0:
        return {"total_real_setups": 0, "message": "Is data me koi setup nahi mila."}
    wins = sum(1 for o in outcomes if o == 1)
    losses = sum(1 for o in outcomes if o == 0)
    win_rate = round(100 * wins / total, 1)

    # 1000 bootstrap resamples - asli outcomes se range nikalna
    rng = random.Random(seed)
    boot_rates = []
    for _ in range(1000):
        sample = [rng.choice(outcomes) for _ in range(total)]
        boot_rates.append(100 * sum(1 for o in sample if o == 1) / total)
    boot_rates.sort()
    return {
        "total_real_setups": total,
        "wins": wins,
        "losses": losses,
        "neutral_time_exit": total - wins - losses,
        "win_rate_pct": win_rate,
        "bootstrap_1000_runs": 1000,
        "bootstrap_win_rate_5th_pct": round(boot_rates[50], 1),
        "bootstrap_win_rate_95th_pct": round(boot_rates[950], 1),
        "sample_enough": bool(total >= 20),
        "explanation": (
            "1000 bootstrap = purane asli setups ko 1000 baar dobara sample kiya, "
            "ye 1000 naye trades nahi hain. Win-rate range dekhna, ek number par bharosa mat karna."
        ),
        "warning": "Pichhla win-rate future profit ki guarantee nahi hai.",
    }
