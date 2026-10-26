"""Paper trading: nakli paisa, asli price, poora journal.
Koi asli order nahi lagta. Har trade CSV me save hoti hai.
"""
import csv
import os

JOURNAL = os.path.join(os.path.dirname(__file__), "..", "examples", "trade-journal.csv")


def log_trade(date, symbol, action, qty, price, stop_loss, target, reason):
    exists = os.path.exists(JOURNAL)
    with open(JOURNAL, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["date", "symbol", "action", "qty", "price",
                        "stop_loss", "target", "reason"])
        w.writerow([date, symbol, action, qty, price, stop_loss, target, reason])
    print(f"Paper trade likh di gayi: {action} {qty} x {symbol} @ {price}")


if __name__ == "__main__":
    from datetime import date
    log_trade(str(date.today()), "RELIANCE.NS", "BUY-PAPER", 10, 2900,
              2850, 2980, "Example paper trade - seekhne ke liye")
