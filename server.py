"""
Trading Assistant MCP Server v2 - REAL DATA ONLY, NO GUESS
===========================================================
Tools:
  - get_real_quote      : sabse taaza price + source + timestamp + delay warning
  - analyze_stock       : REAL data par chart analysis (source/date ke saath)
  - backtest_stock      : pichhle data par backtest
  - validate_strategy   : 1000 bootstrap resample validation (asli setups se)
  - check_trade_risk    : 1% risk, stop-loss, position size, Risk:Reward
  - pre_trade_checklist : 25-point checklist
  - get_trade_plan      : END-TO-END plan - BUY / WAIT / NO TRADE,
                          entry, stop, target, quantity, hold period,
                          kab sell karna, aur broker me payment step

NO-GUESS RULE (sakht):
  Agar REAL data nahi milta to tool ERROR dega, kabhi andaze se
  price, target ya decision NAHI banayega. Claude ko bhi yehi rule
  CLAUDE.md me diya gaya hai.

Isme KOI live order / buy / sell / payment tool NAHI hai.
Server kabhi broker me order nahi lagata, koi password/OTP/API key
nahi maangta, koi paisa move nahi karta. Payment tum broker app me
khud karte ho, plan dekh kar.

Claude.ai me endpoint:
  https://TUMHARA-SERVER-URL/mcp
Local test:
  python server.py   ->  http://127.0.0.1:8000/mcp
  python test_client.py  (alag terminal me, server chal raha ho tab)
"""
import os
import sys

_here = os.path.dirname(__file__)
# Standalone package me src/ isi folder me hai, purane kit me ../src me tha.
# Dono jagah try karo, jo mile use karo.
for _p in (os.path.join(_here, "src"), os.path.join(_here, "..", "src")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)
        break

from mcp.server.fastmcp import FastMCP

from data import fetch_data_with_meta, fetch_quote
from analysis import analyse
from backtest import backtest
from decision import make_trade_plan
from risk import check_trade
from validation import validate_strategy

mcp = FastMCP("trading-assistant")
mcp.settings.host = "0.0.0.0"
mcp.settings.port = int(os.environ.get("PORT", "8000"))
try:
    mcp.settings.transport_security.enable_dns_rebinding_protection = False
    mcp.settings.transport_security.allowed_hosts = ["*"]
    mcp.settings.transport_security.allowed_origins = ["*"]
except Exception:
    pass


def _err(symbol, e):
    return {
        "symbol": symbol,
        "decision": "NO DATA",
        "error": (
            f"REAL data nahi mila: {e}. "
            "Andaza mat lagao. 2 minute baad dobara try karo, "
            "ya broker app ka price/date batao."
        ),
        "do_not_guess": True,
    }


@mcp.tool()
def get_real_quote(symbol: str) -> dict:
    """Sabse taaza REAL price do, source + timestamp + delay warning ke saath.
    symbol: RELIANCE.NS, TCS.NS, AAPL, MSFT. Data na mile to error, guess nahi."""
    try:
        return fetch_quote(symbol)
    except Exception as e:
        return _err(symbol, e)


@mcp.tool()
def analyze_stock(symbol: str, period: str = "1y") -> dict:
    """REAL data par chart analysis: trend, RSI, EMA, MACD, ATR,
    support/resistance, score. Har jawab me source aur last_date hoga.
    Data stale (7 din se purana) ho to bhi ye bata dega."""
    try:
        df, meta = fetch_data_with_meta(symbol, period=period)
        result = analyse(df)
        result["symbol"] = symbol
        result["data_meta"] = meta
        result["warning"] = (
            "Ye analysis hai, guarantee nahi. Free data ~15 min delayed ho sakta hai."
        )
        return result
    except Exception as e:
        return _err(symbol, e)


@mcp.tool()
def backtest_stock(symbol: str, period: str = "2y") -> dict:
    """Pichhle REAL data par backtest: trades, win rate, profit factor, drawdown.
    Pichhla result future guarantee nahi hai."""
    try:
        df, meta = fetch_data_with_meta(symbol, period=period)
        result = backtest(df)
        result["symbol"] = symbol
        result["data_meta"] = meta
        return result
    except Exception as e:
        return _err(symbol, e)


@mcp.tool()
def validate_strategy(symbol: str, period: str = "5y") -> dict:
    """Strategy ko 1000 baar bootstrap check karo.
    Asli setups pichhle REAL data se nikalte hain, phir un outcomes ko
    1000 baar resample karke win-rate ki range nikalte hain.
    Ye 1000 naye trades nahi hain, ye baat jawab me saaf likhi hogi."""
    try:
        df, meta = fetch_data_with_meta(symbol, period=period)
        result = validate_strategy(df)
        result["symbol"] = symbol
        result["data_meta"] = meta
        return result
    except Exception as e:
        return _err(symbol, e)


@mcp.tool()
def check_trade_risk(entry: float, stop_loss: float, target: float,
                     capital: float = 100000) -> dict:
    """Risk check: 1% rule, Risk:Reward >= 1.5, quantity, max loss/profit."""
    try:
        ok, msg, details = check_trade(entry, stop_loss, target, capital)
        return {"ok": ok, "message": msg, "entry": entry,
                "stop_loss": stop_loss, "target": target,
                "capital": capital, **details}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def pre_trade_checklist() -> dict:
    """25-point pre-trade checklist. Mandatory (1-10) me ek bhi FAIL = NO TRADE."""
    return {
        "mandatory_1_to_10": [
            "1. Trend daily chart par clear hai",
            "2. Stop-loss level clear hai",
            "3. Risk:Reward kam se kam 1:1.5 hai",
            "4. Ek trade ka risk capital ka 1% se zyada nahi",
            "5. Aaj ka total loss 2% se kam hai",
            "6. Volume normal se kam nahi hai",
            "7. Aaj koi bada news/earnings/result nahi hai",
            "8. Market trend ke against nahi ja rahe",
            "9. Entry level clear hai",
            "10. Exit plan clear hai",
        ],
        "confirmation_11_to_18": [
            "Price 50 EMA ke upar hai (long ke liye), RSI 50-70 me hai, "
            "MACD positive hai, volume badh raha hai, support paas hai",
        ],
        "discipline_19_to_25": [
            "FOMO se trade nahi le raha, loss bardasht kar sakta hoon, "
            "trade journal me likhunga, leverage nahi, din me 3 se zyada trades nahi",
        ],
        "rule": "Mandatory me se ek bhi FAIL = NO TRADE. Total PASS 16 se kam = NO TRADE.",
    }


@mcp.tool()
def get_trade_plan(symbol: str, capital: float = 100000, period: str = "5y") -> dict:
    """END-TO-END plan, ek hi call me sab kuch:
    REAL data fetch -> analysis -> 1000 bootstrap validation -> risk check
    -> gates -> final BUY / WAIT / NO TRADE, entry, stop, target, quantity,
    hold period (3-10 din), kab sell karna (6 rules), aur broker payment step.
    Data na mile to decision NO DATA hoga, guess nahi.
    capital: tumhari total capital, default Rs 100,000 example hai."""
    try:
        df, meta = fetch_data_with_meta(symbol, period=period)
        return make_trade_plan(df, meta, capital=capital)
    except Exception as e:
        return _err(symbol, e)


if __name__ == "__main__":
    # Claude.ai remote connector ke liye Streamable HTTP.
    # Endpoint: http://HOST:PORT/mcp
    mcp.run(transport="streamable-http")
