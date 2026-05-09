"""
MarketPulse
~~~~~~~~~~~
Indian Financial News Aggregator — scrapes and structures news, articles,
updates, and summaries from Moneycontrol.com and NDTVProfit.com.

Usage::

    from MarketPulse import Moneycontrol, NdtvProfit

    mc   = Moneycontrol()
    ndtv = NdtvProfit()

    print(mc.latest_news())
    print(ndtv.market_news())
"""

from .config import MarketPulseConfig
from .models import NewsArticle
from .moneycontrol import Moneycontrol
from .ndtvprofit import NdtvProfit

__all__ = [
    "MarketPulseConfig",
    "NewsArticle",
    "Moneycontrol",
    "NdtvProfit",
]

__version__ = "1.0.0"
