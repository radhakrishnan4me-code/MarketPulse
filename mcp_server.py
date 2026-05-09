"""
MarketPulse MCP Server
~~~~~~~~~~~~~~~~~~~~~~~~
FastMCP wrapper exposing all MarketPulse scrapers as MCP tools.
AI agents can query Indian financial news via this server.

Usage::

    # stdio mode (for Claude Code, Cursor, etc.)
    python mcp_server.py

    # Or via FastMCP CLI
    mcp run mcp_server.py
"""

import json
import os
import time
from threading import Lock

import pandas as pd
from mcp.server.fastmcp import FastMCP

from MarketPulse import Moneycontrol, NdtvProfit

# ================================================================
#                   RATE LIMIT CONTROL
# ================================================================

RATE_LIMIT_SECONDS = 0.5  # ~2 requests/sec
_last_call_time = 0
_lock = Lock()


def rate_limit():
    """Ensures minimum delay between scraper calls."""
    global _last_call_time
    with _lock:
        now = time.time()
        elapsed = now - _last_call_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        _last_call_time = time.time()


# ================================================================
#                   MCP + Scraper Initialization
# ================================================================

mcp = FastMCP("MarketPulse-MCP", json_response=True)

mc   = Moneycontrol()
ndtv = NdtvProfit()


# ================================================================
#                   Helper: DF → JSON
# ================================================================

def df_to_json(data):
    """Convert DataFrame to list of dicts for JSON serialization."""
    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")
    return data


# =====================================================================
# MONEYCONTROL — NEWS TOOLS
# =====================================================================

@mcp.tool()
def mc_latest_news(limit: int = 25):
    """
    TOOL: mc_latest_news
    DESCRIPTION:
        Fetch latest news articles from Moneycontrol.com.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of news articles with title, url, summary, published_at
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.latest_news(limit=limit))


@mcp.tool()
def mc_market_news(limit: int = 25):
    """
    TOOL: mc_market_news
    DESCRIPTION:
        Fetch market-specific news from Moneycontrol.
        Covers stock market updates, trading sessions, indices.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of market news articles
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.market_news(limit=limit))


@mcp.tool()
def mc_economy_news(limit: int = 25):
    """
    TOOL: mc_economy_news
    DESCRIPTION:
        Fetch economy & macro news from Moneycontrol.
        GDP, RBI, inflation, policy updates.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of economy news
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.economy_news(limit=limit))


@mcp.tool()
def mc_ipo_news(limit: int = 25):
    """
    TOOL: mc_ipo_news
    DESCRIPTION:
        Fetch IPO-related news from Moneycontrol.
        New listings, subscription status, grey market premium.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of IPO news
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.ipo_news(limit=limit))


@mcp.tool()
def mc_expert_opinions(limit: int = 25):
    """
    TOOL: mc_expert_opinions
    DESCRIPTION:
        Fetch expert views and analysis from Moneycontrol.
        Analyst opinions, market outlook, investment strategies.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of expert opinion articles
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.expert_opinions(limit=limit))


@mcp.tool()
def mc_personal_finance(limit: int = 25):
    """
    TOOL: mc_personal_finance
    DESCRIPTION:
        Fetch personal finance news from Moneycontrol.
        Tax, savings, insurance, loans.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of personal finance news
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.personal_finance(limit=limit))


@mcp.tool()
def mc_mutual_funds_news(limit: int = 25):
    """
    TOOL: mc_mutual_funds_news
    DESCRIPTION:
        Fetch mutual fund news from Moneycontrol.
        NAV updates, SIP trends, fund performance.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of mutual fund news
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.mutual_funds_news(limit=limit))


@mcp.tool()
def mc_stock_news(symbol: str, limit: int = 15):
    """
    TOOL: mc_stock_news
    DESCRIPTION:
        Fetch news for a specific stock from Moneycontrol.
        Company-specific updates, earnings, analysis.
    PARAMETERS:
        symbol: str – Stock name/tag (e.g., "reliance", "tcs", "hdfc-bank")
        limit: int – Max articles (default 15)
    RETURNS:
        JSON list of stock-specific news
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.stock_news(symbol=symbol, limit=limit))


@mcp.tool()
def mc_trending_news(limit: int = 10):
    """
    TOOL: mc_trending_news
    DESCRIPTION:
        Fetch currently trending stories from Moneycontrol.
    PARAMETERS:
        limit: int – Max articles (default 10)
    RETURNS:
        JSON list of trending news
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return df_to_json(mc.trending_news(limit=limit))


@mcp.tool()
def mc_article_detail(url: str):
    """
    TOOL: mc_article_detail
    DESCRIPTION:
        Fetch full article content from a Moneycontrol article URL.
        Returns title, full text, summary, author, tags, image.
    PARAMETERS:
        url: str – Full Moneycontrol article URL
    RETURNS:
        JSON with full article details (title, content, summary, author, tags)
    CATEGORY:
        Moneycontrol_News
    """
    rate_limit()
    return mc.article_detail(url)


# =====================================================================
# NDTV PROFIT — NEWS TOOLS
# =====================================================================

@mcp.tool()
def ndtv_latest_news(limit: int = 25):
    """
    TOOL: ndtv_latest_news
    DESCRIPTION:
        Fetch latest news from NDTV Profit.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of news articles with title, url, summary, published_at
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.latest_news(limit=limit))


@mcp.tool()
def ndtv_market_news(limit: int = 25):
    """
    TOOL: ndtv_market_news
    DESCRIPTION:
        Fetch markets section news from NDTV Profit.
        Stock market updates, indices, FII/DII activity.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of market news
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.market_news(limit=limit))


@mcp.tool()
def ndtv_economy_news(limit: int = 25):
    """
    TOOL: ndtv_economy_news
    DESCRIPTION:
        Fetch economy & policy news from NDTV Profit.
        GDP, RBI, fiscal policy, trade data.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of economy news
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.economy_news(limit=limit))


@mcp.tool()
def ndtv_opinion_news(limit: int = 25):
    """
    TOOL: ndtv_opinion_news
    DESCRIPTION:
        Fetch opinion and analysis from NDTV Profit.
        Expert columns, editorials, market analysis.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of opinion articles
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.opinion_news(limit=limit))


@mcp.tool()
def ndtv_technology_news(limit: int = 25):
    """
    TOOL: ndtv_technology_news
    DESCRIPTION:
        Fetch technology news from NDTV Profit.
        Tech stocks, startups, digital economy.
    PARAMETERS:
        limit: int – Max articles (default 25)
    RETURNS:
        JSON list of tech news
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.technology_news(limit=limit))


@mcp.tool()
def ndtv_stock_news(symbol: str, limit: int = 15):
    """
    TOOL: ndtv_stock_news
    DESCRIPTION:
        Fetch news for a specific stock/topic from NDTV Profit.
    PARAMETERS:
        symbol: str – Stock symbol or topic (e.g., "reliance", "infosys")
        limit: int – Max articles (default 15)
    RETURNS:
        JSON list of stock-specific news
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.stock_news(symbol=symbol, limit=limit))


@mcp.tool()
def ndtv_trending_news(limit: int = 10):
    """
    TOOL: ndtv_trending_news
    DESCRIPTION:
        Fetch trending stories from NDTV Profit homepage.
    PARAMETERS:
        limit: int – Max articles (default 10)
    RETURNS:
        JSON list of trending news
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return df_to_json(ndtv.trending_news(limit=limit))


@mcp.tool()
def ndtv_article_detail(url: str):
    """
    TOOL: ndtv_article_detail
    DESCRIPTION:
        Fetch full article content from an NDTV Profit article URL.
        Returns title, full text, summary, author, tags, image.
    PARAMETERS:
        url: str – Full NDTV Profit article URL
    RETURNS:
        JSON with full article details (title, content, summary, author, tags)
    CATEGORY:
        NdtvProfit_News
    """
    rate_limit()
    return ndtv.article_detail(url)


# =====================================================================
# COMBINED / CROSS-SOURCE TOOLS
# =====================================================================

@mcp.tool()
def all_latest_news(limit: int = 15):
    """
    TOOL: all_latest_news
    DESCRIPTION:
        Fetch latest news from BOTH Moneycontrol and NDTV Profit combined.
        Returns a merged list sorted by source.
    PARAMETERS:
        limit: int – Max articles per source (default 15, total up to 30)
    RETURNS:
        JSON list of combined news from both sources
    CATEGORY:
        Combined_News
    """
    rate_limit()
    mc_news   = mc.latest_news(limit=limit, output="json")
    rate_limit()
    ndtv_news = ndtv.latest_news(limit=limit, output="json")

    combined = (mc_news or []) + (ndtv_news or [])
    return combined


@mcp.tool()
def all_market_news(limit: int = 15):
    """
    TOOL: all_market_news
    DESCRIPTION:
        Fetch market news from BOTH Moneycontrol and NDTV Profit combined.
    PARAMETERS:
        limit: int – Max articles per source (default 15, total up to 30)
    RETURNS:
        JSON list of combined market news
    CATEGORY:
        Combined_News
    """
    rate_limit()
    mc_news   = mc.market_news(limit=limit, output="json")
    rate_limit()
    ndtv_news = ndtv.market_news(limit=limit, output="json")

    combined = (mc_news or []) + (ndtv_news or [])
    return combined


@mcp.tool()
def all_stock_news(symbol: str, limit: int = 10):
    """
    TOOL: all_stock_news
    DESCRIPTION:
        Fetch news for a stock from BOTH Moneycontrol and NDTV Profit.
    PARAMETERS:
        symbol: str – Stock symbol (e.g., "reliance", "tcs")
        limit: int – Max articles per source (default 10, total up to 20)
    RETURNS:
        JSON list of combined stock news
    CATEGORY:
        Combined_News
    """
    rate_limit()
    mc_news   = mc.stock_news(symbol=symbol, limit=limit, output="json")
    rate_limit()
    ndtv_news = ndtv.stock_news(symbol=symbol, limit=limit, output="json")

    combined = (mc_news or []) + (ndtv_news or [])
    return combined


# =====================================================================
# BEARER AUTH MIDDLEWARE (for Host Rewriting)
# =====================================================================

class HostRewritingMiddleware:
    """
    ASGI middleware that rewrites the Host header to localhost 
    to pass MCP DNS rebinding checks when running in Docker/n8n.
    """
    def __init__(self, app, port):
        self.app = app
        self.port = port

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            new_headers = []
            for key, value in scope.get("headers", []):
                if key == b"host":
                    # Force host to localhost to satisfy MCP security
                    value = f"localhost:{self.port}".encode()
                new_headers.append((key, value))
            scope = dict(scope, headers=new_headers)

        await self.app(scope, receive, send)

# ================================================================
#                   ENTRY POINT
# ================================================================

if __name__ == "__main__":
    import argparse
    import uvicorn
    from starlette.responses import Response

    parser = argparse.ArgumentParser(description="MarketPulse MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio", help="Transport protocol")
    parser.add_argument("--port", type=int, default=8001, help="Port for HTTP server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for HTTP server")
    args = parser.parse_args()

    if args.transport == "http":
        print(f"Starting MarketPulse MCP Server on http://{args.host}:{args.port}")
        
        # Create the MCP Starlette app for streamable-http transport
        mcp_app = mcp.streamable_http_app()
        
        # Wrap with host rewrite middleware to fix Docker "Invalid Host header" errors
        app = HostRewritingMiddleware(mcp_app, args.port)

        uvicorn.run(app, host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")
