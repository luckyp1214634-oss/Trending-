"""Full Trade Plan Engine - ek hi jagah se saaf faisla.
Output sirf 3 me se ek hoga: BUY / WAIT / NO TRADE.
BUY tabhi jab saare mandatory gates PASS hon, warna WAIT ya NO TRADE.
80-90% accuracy ka daava ye engine NAHI karta, kyunki wo jhooth hota.
Achha system 40-55% win-rate par bhi profit de sakta hai, jab
Risk:Reward 1:1.5 se upar ho aur loss chhota rakha jaye.
"""
from analysis import analyse
from risk import check_trade
from validation import validate_strategy


def make_trade_plan(df, meta, capital=100000):
    a = analyse(df)
    v = validate_strategy(df)
    price = a["price"]
    stop = a["suggested_stop"]
    # Stop = entry - 1.5*ATR, isliye Target 1 kam se kam 1.5x risk hona chahiye:
    # Target 1 = entry + 2.25*ATR (RR = 1.5), Target 2 = entry + 3.75*ATR (RR = 2.5)
    target1 = round(price + 2.25 * a["atr"], 2)
    target2 = round(price + 3.75 * a["atr"], 2)
    ok_risk, risk_msg, risk_det = check_trade(price, stop, target1, capital)

    gates = {}
    gates["data_fresh"] = (not meta.get("is_stale", True)) and meta.get("rows", 0) >= 60
    gates["trend_up"] = price > a["ema50"]
    gates["momentum_ok"] = (50 <= a["rsi"] <= 70) and a["macd_hist"] > 0
    gates["volume_ok"] = True  # volume detail analysis me reasons me hai, yahan soft gate
    gates["risk_ok"] = bool(ok_risk)
    gates["validation_ok"] = bool(v.get("sample_enough")) and v.get("win_rate_pct", 0) >= 40
    # Resistance ke bahut paas ho to chase mat karo
    gates["not_near_resistance"] = (a["resistance"] - price) >= 0.5 * a["atr"]

    failed = [k for k, val in gates.items() if not val]
    passed = len(gates) - len(failed)

    if not gates["data_fresh"]:
        decision = "NO TRADE"
        reason = "Data stale ya bahut kam hai, andaze par trade nahi."
    elif not failed:
        decision = "BUY"
        reason = "Saare mandatory gates PASS hain. Phir bhi loss possible hai."
    elif gates["trend_up"] and len(failed) <= 2:
        decision = "WAIT"
        reason = f"Wait karo, ye gates fail hain: {', '.join(failed)}. Unke theek hone par dobara check karo."
    else:
        decision = "NO TRADE"
        reason = f"Setup kamzor hai, fail gates: {', '.join(failed)}."

    plan = {
        "decision": decision,
        "reason": reason,
        "gates_passed": f"{passed}/{len(gates)}",
        "failed_gates": failed,
        "symbol": meta.get("symbol"),
        "data_source": meta.get("source"),
        "data_last_date": meta.get("last_date"),
        "data_rows": meta.get("rows"),
        "price": price,
        "entry_zone": f"{round(price * 0.995, 2)} - {round(price * 1.005, 2)}",
        "entry": price,
        "stop_loss": stop,
        "target_1": target1,
        "target_2": target2,
        "quantity_for_capital": risk_det.get("quantity", 0) if ok_risk else 0,
        "max_loss": risk_det.get("max_loss", 0) if ok_risk else 0,
        "max_profit_target_1": risk_det.get("max_profit_target", 0) if ok_risk else 0,
        "risk_reward": risk_det.get("risk_reward", 0) if ok_risk else 0,
        "capital_used_for_calc": capital,
        "analysis": a,
        "validation": v,
        "hold_period": "Swing trade: 3-10 trading days. Har din market band hone ke baad review karo.",
        "kab_sell_karna": [
            "1. Target 1 hit ho to aadhi quantity becho, stop-loss ko entry par le aao (free trade).",
            "2. Target 2 hit ho to baaki becho.",
            "3. Stop-loss hit ho to poora becho, wait mat karo, hope par trade mat rakho.",
            "4. Price daily close me EMA50 ke neeche band ho to becho, chahe stop na laga ho.",
            "5. 10 trading din me na target na stop lage to review karo, aur kamzor lage to exit karo (time stop).",
            "6. Company ka bada negative news aaye to turant review karo.",
        ],
        "payment_step": (
            "Broker app me ja kar, entry zone me LIMIT order lagao, "
            "quantity upar wali lo. Agar broker price entry se 1% se zyada upar "
            "nikal gaya ho to chase mat karo, WAIT karo. MCP server kabhi "
            "payment nahi leta aur order nahi lagata - payment tum broker me karte ho."
        ),
        "final_check_before_paying": (
            "Buy dabane se pehle broker app ka live price, quantity aur "
            "stop-loss dobara match karo. Free data ~15 min delayed ho sakta hai."
        ),
        "disclaimer": (
            "Ye plan pichhle REAL data par based hai, future guarantee nahi hai. "
            "80-90% accuracy ka daava galat hota. Loss possible hai, isliye "
            "stop-loss aur 1% risk rule kabhi mat todo."
        ),
    }
    return plan
