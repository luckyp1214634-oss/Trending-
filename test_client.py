"""Local test: server ko alag terminal me chalao (python server.py),
phir ye script chalao. Tools list + checklist + risk + trade plan (1y) check karega.
Trade plan wala test REAL Yahoo data mangta hai, isliye 60-120 sec lag sakta hai.
Server band hone par ye fail hoga, wo normal hai - pehle server start karo.
"""
import asyncio
import os

for _k in list(os.environ):
    if _k.lower() in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
        del os.environ[_k]

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _client_factory(**kwargs):
    kwargs.pop("timeout", None)
    return httpx.AsyncClient(proxy=None, timeout=180, **kwargs)


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp", httpx_client_factory=_client_factory
    ) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            res = await s.call_tool("check_trade_risk", {
                "entry": 2950, "stop_loss": 2900, "target": 3025, "capital": 100000})
            print("RISK:", res.content[0].text[:500])
            print("TRADE PLAN test chal raha hai (REAL data, thoda time lagega)...")
            res2 = await s.call_tool("get_trade_plan", {
                "symbol": "RELIANCE.NS", "capital": 100000, "period": "1y"})
            txt = res2.content[0].text
            print("TRADE PLAN (pehle 2000 chars):")
            print(txt[:2000])


if __name__ == "__main__":
    asyncio.run(main())
