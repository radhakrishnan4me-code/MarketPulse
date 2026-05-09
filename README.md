# MarketPulse

Indian Financial News Aggregator — scrapes and structures news, articles, updates, and summaries from **Moneycontrol.com** and **NDTVProfit.com**.

Inspired by [NseKit](https://github.com/Prasad1612/NseKit)'s clean, production-grade architecture.

## Installation

```bash
pip install -r requirements.txt
```

Or install as editable package:
```bash
pip install -e .
```

## Quick Start

```python
from MarketPulse import Moneycontrol, NdtvProfit

mc   = Moneycontrol()
ndtv = NdtvProfit()

# Latest news from Moneycontrol
print(mc.latest_news())

# Market news from NDTV Profit
print(ndtv.market_news())

# Stock-specific news
print(mc.stock_news("reliance"))

# Full article content
detail = mc.article_detail("https://www.moneycontrol.com/news/...")
print(detail["content"])
```

Please refer to **MarketPulse_Usage.py** for full usage examples.

## Configuration

```python
from MarketPulse import MarketPulseConfig

MarketPulseConfig.max_rps      = 2.0    # Requests per second (default: 2.0)
MarketPulseConfig.retries      = 3      # Retry attempts (default: 3)
MarketPulseConfig.retry_delay  = 2.0    # Base retry delay in seconds (default: 2.0)
MarketPulseConfig.cookie_cache = True   # Enable cookie caching (default: True)
```

## API Reference

### Moneycontrol

| Method | Description |
|--------|-------------|
| `latest_news(limit=25)` | Latest news articles |
| `market_news(limit=25)` | Market-specific news |
| `economy_news(limit=25)` | Economy & macro updates |
| `ipo_news(limit=25)` | IPO-related news |
| `expert_opinions(limit=25)` | Expert views & analysis |
| `personal_finance(limit=25)` | Personal finance news |
| `mutual_funds_news(limit=25)` | Mutual fund updates |
| `stock_news(symbol, limit=15)` | Stock-specific news |
| `trending_news(limit=10)` | Trending stories |
| `article_detail(url)` | Full article content |

### NDTV Profit

| Method | Description |
|--------|-------------|
| `latest_news(limit=25)` | Latest news articles |
| `market_news(limit=25)` | Markets section news |
| `economy_news(limit=25)` | Economy & policy news |
| `opinion_news(limit=25)` | Opinion & analysis |
| `technology_news(limit=25)` | Technology news |
| `stock_news(symbol, limit=15)` | Stock/topic news |
| `trending_news(limit=10)` | Trending stories |
| `article_detail(url)` | Full article content |

### Output Formats

All methods support two output modes:
- `output="dataframe"` — Returns `pd.DataFrame` (default)
- `output="json"` — Returns `list[dict]`

## MCP Server

MarketPulse includes a FastMCP server for AI agent and automation integration.

### Local Usage (stdio)
For use with AI coding assistants like **Claude Desktop** or **Cursor**:
```bash
python mcp_server.py
```

### Server/Automation Usage (HTTP/SSE)
For use with **n8n** or other remote clients:
```bash
python mcp_server.py --transport http --port 8000
```

---

## Docker Deployment

I have included a `Dockerfile` and `docker-compose.yml` for easy deployment on VPS environments (e.g., via **Portainer**).

### Quick Start with Docker Compose
```bash
docker-compose up -d
```

### Portainer Installation
1.  Add a new **Stack**.
2.  Select **Repository** as the build method.
3.  Enter your repository URL.
4.  Specify `docker-compose.yml` as the compose path.
5.  Deploy.

The server will be available at `http://YOUR_VPS_IP:8000/sse` for n8n.

---

## Architecture

```
MarketPulse/
├── MarketPulse/
│   ├── __init__.py         # Package exports
│   ├── config.py           # Central config (rate limits, retries)
│   ├── session.py          # BaseSession (HTTP, cookies, UA rotation)
│   ├── models.py           # NewsArticle dataclass
│   ├── moneycontrol.py     # Moneycontrol scraper
│   └── ndtvprofit.py       # NDTV Profit scraper
├── mcp_server.py           # FastMCP wrapper (22 tools)
├── MarketPulse_Usage.py    # Usage examples
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Dependencies

- `requests` — HTTP client
- `beautifulsoup4` + `lxml` — HTML parsing
- `pandas` — DataFrame output
- `feedparser` — RSS feed parsing
- `mcp[cli]` — MCP server (optional)

## Requirements

- Python 3.10+

## License

MIT License
