"""Main program: analyze / backtest / paper
Example:
  python src/main.py --symbol RELIANCE.NS --mode analyze
  python src/main.py --symbol RELIANCE.NS --mode backtest --period 2y
  python src/main.py --mode paper
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data import fetch_data
from analysis import analyse
from backtest import backtest
from risk import check_trade


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="RELIANCE.NS")
    p.add_argument("--mode", choices=["analyze", "backtest", "paper"], default="analyze")
    p.add_argument("--period", default="1y")
    p.add_argument("--capital", type=float, default=100000)
    args = p.parse_args()

    if args.mode == "paper":
        from paper_trading import log_trade
        from datetime import date
        log_trade(str(date.today()), args.symbol, "BUY-PAPER", 0, 0, 0, 0,
                  "Paper mode - price khud bharo, ye sirf journal test hai")
        return

    df = fetch_data(args.symbol, period=args.period)

    if args.mode == "analyze":
        a = analyse(df)
        print(f"\n=== {args.symbol} ANALYSIS ===")
        for k, v in a.items():
            if k != "reasons":
                print(f"{k}: {v}")
        print("Reasons:")
        for r in a["reasons"]:
            print(f" - {r}")
        ok, msg, det = check_trade(a["price"], a["suggested_stop"],
                                   a["suggested_target"], args.capital)
        print(f"\nRisk check: {msg}")
        print(det)
        print("\nNote: Ye analysis hai, guarantee nahi. Pehle paper trading karo.")
    else:
        b = backtest(df)
        print(f"\n=== {args.symbol} BACKTEST ({args.period}) ===")
        for k, v in b.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
