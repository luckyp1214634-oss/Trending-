# Trading MCP Server - Standalone Package (Hindi Guide)

Yehi wo MCP server hai. Isme server ka code + real-data wala analysis code,
dono ek hi folder me hain. Alag se kuch download karne ki zaroorat nahi hai.

## Isme kya hai?

- `server.py` - MCP server (7 tools, read-only, koi order/payment nahi)
- `src/` - real data, analysis, backtest, validation, trade-plan ka code
- `requirements.txt` - install karne wali libraries
- `render.yaml` - Render par deploy karne ki setting
- `test_client.py` - local test karne ke liye

## 7 Tools

1. `get_real_quote` - taaza price + source + date
2. `analyze_stock` - chart analysis
3. `backtest_stock` - pichhla backtest
4. `validate_strategy` - 1000 bootstrap validation
5. `check_trade_risk` - risk, quantity, stop-loss
6. `pre_trade_checklist` - 25-point checklist
7. `get_trade_plan` - BUY / WAIT / NO TRADE + entry, stop, target,
   hold period (3-10 din), kab sell karna, broker payment step

## Live link kaise banega? (Ye step tumhara account chahiye)

MCP server ka live link banane ke liye server ko internet par chalana padta hai.
Ye kaam Lucky tumhare naam se nahi kar sakta, kyunki Render/GitHub account
tumhare email aur login se banta hai, aur uska password Lucky ko nahi dena hai.

Tumko sirf ye 5 minute ka kaam karna hai:

1. GitHub.com par free account banao (agar nahi hai to), aur is folder ko
   ek naye PRIVATE repo me upload karo. Repo ka naam kuch bhi rakho,
   jaise `trading-mcp-server`.
2. Render.com par free account banao, GitHub se login karo.
3. Render me **New + > Web Service** dabao, apna repo chuno.
4. Ye bharo:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`
   - Plan: Free
5. **Create Web Service** dabao. 2-5 minute me URL milega, jaise:
   `https://trading-assistant-mcp.onrender.com`
6. Tumhara MCP link ye hoga:
   `https://trading-assistant-mcp.onrender.com/mcp`

## Claude me link kaise add karo?

1. claude.ai kholo > **Customize > Connectors**
2. **+ > Add custom connector** dabao
3. Naam: `Trading Assistant`
4. URL: upar wala `/mcp` link paste karo
5. **Add** > **Connect** dabao (is server me koi login nahi hai)
6. Nayi chat me **+ > Connectors** me Trading Assistant ON karo
7. Likho: `RELIANCE.NS ka full trade plan do, capital Rs 100,000`

Free account me sirf 1 custom connector milta hai, isliye yehi ek rakho.

## Local test (computer par, bina Render ke)

```
pip install -r requirements.txt
python server.py
# alag terminal me:
python test_client.py
```

Server chalega: `http://127.0.0.1:8000/mcp`
Ye local link Claude.ai me NAHI chalega, kyunki Claude tumhare computer
se nahi, apne cloud se connect hota hai. Claude.ai ke liye Render wala
public link hi chahiye.

## Safety

- Ye server kabhi order nahi lagata, payment nahi leta.
- Broker ka password, OTP ya API key kabhi isme mat dalo.
- Free Yahoo data ~15 minute delayed hota hai. Buy se pehle broker app
  ka live price zaroor check karo.
