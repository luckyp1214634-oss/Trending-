"""Risk management - loss ko chhota rakhne ke pakke rules."""


def position_size(capital, risk_pct, entry, stop_loss):
    """Kitne shares khareed sakte ho, taaki loss risk_pct se zyada na ho."""
    risk_per_share = abs(entry - stop_loss)
    if risk_per_share == 0:
        return 0
    risk_amount = capital * (risk_pct / 100.0)
    return int(risk_amount // risk_per_share)


def risk_reward(entry, stop_loss, target):
    risk = abs(entry - stop_loss)
    reward = abs(target - entry)
    if risk == 0:
        return 0
    return round(reward / risk, 2)


def check_trade(entry, stop_loss, target, capital, risk_pct=1.0, min_rr=1.5):
    """Trade lene layak hai ya nahi? Returns (ok, reason, details)."""
    rr = risk_reward(entry, stop_loss, target)
    qty = position_size(capital, risk_pct, entry, stop_loss)
    if qty <= 0:
        return False, "Stop-loss entry ke bahut paas hai, position size 0 aaya.", {}
    if rr < min_rr:
        return False, f"Risk:Reward {rr} hai, kam se kam {min_rr} chahiye.", {}
    details = {
        "risk_reward": rr,
        "quantity": qty,
        "max_loss": round(qty * abs(entry - stop_loss), 2),
        "max_profit_target": round(qty * abs(target - entry), 2),
    }
    return True, "PASS: Risk rules ke andar hai.", details
