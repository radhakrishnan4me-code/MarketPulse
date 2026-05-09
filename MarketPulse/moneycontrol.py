"""
MarketPulse — Moneycontrol News Scraper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Scrapes news, articles, updates, and summaries from moneycontrol.com.
No third-party API packages — pure requests + BeautifulSoup.
"""

import logging
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

from .models import NewsArticle
from .session import BaseSession

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.moneycontrol.com"


class Moneycontrol:
    """
    Moneycontrol news client.

    All public methods return a ``pd.DataFrame`` (default) or ``list[dict]``
    when ``output="json"``.

    Quick start
    -----------
    ::

        from MarketPulse import Moneycontrol
        mc = Moneycontrol()
        df = mc.latest_news()
        print(df)
    """

    def __init__(
        self,
        max_rps:      float | None = None,
        retries:      int   | None = None,
        retry_delay:  float | None = None,
        cookie_cache: bool  | None = None,
    ):
        self._session = BaseSession(
            site_name="moneycontrol",
            base_referer="https://www.moneycontrol.com/",
            warmup_urls=[
                "https://www.moneycontrol.com",
                "https://www.moneycontrol.com/news/",
            ],
            max_rps=max_rps,
            retries=retries,
            retry_delay=retry_delay,
            cookie_cache=cookie_cache,
        )

    def __repr__(self) -> str:
        return "Moneycontrol()"

    # ══════════════════════════════════════════════════════════════════
    # Internal Parsers
    # ══════════════════════════════════════════════════════════════════

    def _parse_news_listing(self, html: str, category: str = "latest") -> list[NewsArticle]:
        """Parse a Moneycontrol news listing page into NewsArticle objects."""
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, "lxml")
        seen = set()

        for link in soup.select("a"):
            title = link.get("title", "") or link.get_text(strip=True)
            href  = link.get("href", "")
            
            # Must have a reasonable title length and be a news link
            if len(title) < 20 or not href or "/news/" not in href:
                continue
            
            if not href.startswith("http"):
                href = urljoin(_BASE_URL, href)
                
            if href in seen:
                continue
            seen.add(href)

            # Try to find an image nearby
            img_url = None
            parent = link.parent
            if parent:
                img = parent.select_one("img")
                if img:
                    img_url = img.get("data-src") or img.get("src")

            articles.append(NewsArticle(
                title=title,
                url=href,
                source="moneycontrol",
                category=category,
                image_url=img_url,
            ))

        return articles

    def _parse_article_page(self, html: str, url: str = "") -> dict:
        """Extract full article content from a Moneycontrol article page."""
        result = {
            "title": "",
            "content": "",
            "summary": "",
            "published_at": "",
            "author": "",
            "tags": [],
            "image_url": None,
            "url": url,
        }
        if not html:
            return result

        soup = BeautifulSoup(html, "lxml")

        # Title
        title_el = soup.select_one("h1.article_title") or soup.select_one("h1") or soup.select_one("title")
        if title_el:
            result["title"] = title_el.get_text(strip=True)

        # Author
        author_el = soup.select_one(".article_author a") or soup.select_one(".artByline a") or soup.select_one("[rel='author']")
        if author_el:
            result["author"] = author_el.get_text(strip=True)

        # Published time
        time_el = soup.select_one("div.article_schedule") or soup.select_one("time") or soup.select_one(".article_publish_date")
        if time_el:
            result["published_at"] = time_el.get_text(strip=True)

        # Main content
        content_div = soup.select_one("#contentdata") or soup.select_one(".content_wrapper") or soup.select_one("article")
        if content_div:
            # Remove unwanted elements
            for unwanted in content_div.select("script, style, .ad_container, .also_read, .related_stories, .social_share"):
                unwanted.decompose()

            paragraphs = content_div.find_all("p")
            full_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            result["content"] = full_text

            # Summary = first 2 paragraphs
            summary_parts = [p.get_text(strip=True) for p in paragraphs[:2] if p.get_text(strip=True)]
            result["summary"] = " ".join(summary_parts)

        # Tags
        tag_els = soup.select(".tags_list a") or soup.select(".article_tags a")
        result["tags"] = [t.get_text(strip=True) for t in tag_els]

        # Hero image
        img = soup.select_one(".article_image img") or soup.select_one("meta[property='og:image']")
        if img:
            result["image_url"] = img.get("src") or img.get("data-src") or img.get("content")

        return result

    def _to_output(self, articles: list[NewsArticle], output: str = "dataframe"):
        """Convert list of NewsArticle to DataFrame or JSON."""
        if not articles:
            return pd.DataFrame() if output == "dataframe" else []

        records = [a.to_dict() for a in articles]

        if output == "dataframe":
            df = pd.DataFrame(records)
            col_order = ["title", "url", "summary", "published_at", "category", "source", "image_url", "author", "tags"]
            existing = [c for c in col_order if c in df.columns]
            other = [c for c in df.columns if c not in existing]
            return df[existing + other]
        return records

    # ══════════════════════════════════════════════════════════════════
    # Public API
    # ══════════════════════════════════════════════════════════════════

    def latest_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch latest news articles from Moneycontrol.

        Parameters
        ----------
        limit : int
            Max articles to return. Default 25.
        output : str
            ``"dataframe"`` or ``"json"``.

        Returns
        -------
        pd.DataFrame or list[dict]
        """
        html = self._session.get_html(f"{_BASE_URL}/news/latest-news/")
        articles = self._parse_news_listing(html, category="latest")[:limit]
        return self._to_output(articles, output)

    def market_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch market-specific news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/business/markets/")
        articles = self._parse_news_listing(html, category="markets")[:limit]
        return self._to_output(articles, output)

    def economy_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch economy & macro news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/business/economy/")
        articles = self._parse_news_listing(html, category="economy")[:limit]
        return self._to_output(articles, output)

    def ipo_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch IPO-related news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/business/ipo/")
        articles = self._parse_news_listing(html, category="ipo")[:limit]
        return self._to_output(articles, output)

    def expert_opinions(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch expert views and analysis.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/expert-opinions/")
        articles = self._parse_news_listing(html, category="expert_opinions")[:limit]
        return self._to_output(articles, output)

    def personal_finance(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch personal finance news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/business/personal-finance/")
        articles = self._parse_news_listing(html, category="personal_finance")[:limit]
        return self._to_output(articles, output)

    def mutual_funds_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch mutual fund news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/business/mutual-funds/")
        articles = self._parse_news_listing(html, category="mutual_funds")[:limit]
        return self._to_output(articles, output)

    def stock_news(self, symbol: str, limit: int = 15, output: str = "dataframe"):
        """
        Fetch news for a specific stock symbol.

        Parameters
        ----------
        symbol : str
            Stock name or tag (e.g., ``"RELIANCE"``, ``"TCS"``).
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        slug = symbol.lower().replace(" ", "-")
        html = self._session.get_html(f"{_BASE_URL}/news/tags/{slug}.html")
        articles = self._parse_news_listing(html, category=f"stock:{symbol.upper()}")[:limit]
        return self._to_output(articles, output)

    def trending_news(self, limit: int = 10, output: str = "dataframe"):
        """
        Fetch currently trending stories.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/news/")
        if not html:
            return pd.DataFrame() if output == "dataframe" else []

        soup = BeautifulSoup(html, "lxml")
        trending = soup.select(".trending_news a") or soup.select(".trendingNow a") or soup.select("#trending a")

        articles = []
        for link in trending[:limit]:
            title = link.get("title", "") or link.get_text(strip=True)
            href  = link.get("href", "")
            if not title or not href:
                continue
            if not href.startswith("http"):
                href = urljoin(_BASE_URL, href)
            articles.append(NewsArticle(
                title=title,
                url=href,
                source="moneycontrol",
                category="trending",
            ))
        return self._to_output(articles, output)

    def article_detail(self, url: str) -> dict:
        """
        Fetch full article content from a Moneycontrol article URL.

        Parameters
        ----------
        url : str
            Full URL to the article.

        Returns
        -------
        dict
            Keys: ``title``, ``content``, ``summary``, ``published_at``,
            ``author``, ``tags``, ``image_url``, ``url``.
        """
        html = self._session.get_html(url)
        return self._parse_article_page(html, url)
