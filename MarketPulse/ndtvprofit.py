"""
MarketPulse — NDTV Profit News Scraper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Scrapes news, articles, updates, and summaries from ndtvprofit.com.
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

_BASE_URL = "https://www.ndtvprofit.com"


class NdtvProfit:
    """
    NDTV Profit news client.

    All public methods return a ``pd.DataFrame`` (default) or ``list[dict]``
    when ``output="json"``.

    Quick start
    -----------
    ::

        from MarketPulse import NdtvProfit
        ndtv = NdtvProfit()
        df = ndtv.latest_news()
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
            site_name="ndtvprofit",
            base_referer="https://www.ndtvprofit.com/",
            warmup_urls=[
                "https://www.ndtvprofit.com",
                "https://www.ndtvprofit.com/the-latest",
            ],
            max_rps=max_rps,
            retries=retries,
            retry_delay=retry_delay,
            cookie_cache=cookie_cache,
        )

    def __repr__(self) -> str:
        return "NdtvProfit()"

    # ══════════════════════════════════════════════════════════════════
    # Internal Parsers
    # ══════════════════════════════════════════════════════════════════

    def _parse_news_listing(self, html: str, category: str = "latest") -> list[NewsArticle]:
        """Parse an NDTV Profit news listing page into NewsArticle objects."""
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, "lxml")
        seen = set()
        
        valid_segments = ["/stories/", "/markets/", "/economy/", "/india/", "/business/", "/technology/", "/opinion/"]

        for link in soup.select("a"):
            title = link.get("title", "") or link.get_text(strip=True)
            href  = link.get("href", "")
            
            if len(title) < 25 or not href:
                continue
                
            if not any(seg in href for seg in valid_segments):
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
                    img_url = img.get("data-src") or img.get("src") or img.get("data-original")

            articles.append(NewsArticle(
                title=title,
                url=href,
                source="ndtvprofit",
                category=category,
                image_url=img_url,
            ))

        return articles

    def _parse_article_page(self, html: str, url: str = "") -> dict:
        """Extract full article content from an NDTV Profit article page."""
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
        title_el = soup.select_one("h1") or soup.select_one("title")
        if title_el:
            result["title"] = title_el.get_text(strip=True)

        # Author
        author_el = (
            soup.select_one("[class*='author'] a") or
            soup.select_one("[class*='athr'] a") or
            soup.select_one("[rel='author']")
        )
        if author_el:
            result["author"] = author_el.get_text(strip=True)

        # Published time
        time_el = soup.select_one("time") or soup.select_one("[class*='publish']")
        if time_el:
            result["published_at"] = time_el.get("datetime", "") or time_el.get_text(strip=True)

        # Main content
        content_div = (
            soup.select_one("[class*='stry_bdy']") or
            soup.select_one("[class*='story-content']") or
            soup.select_one("article") or
            soup.select_one(".content")
        )
        if content_div:
            # Remove unwanted elements
            for unwanted in content_div.select("script, style, .ad, .related, .social, .share"):
                unwanted.decompose()

            paragraphs = content_div.find_all("p")
            full_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            result["content"] = full_text

            # Summary = first 2 paragraphs
            summary_parts = [p.get_text(strip=True) for p in paragraphs[:2] if p.get_text(strip=True)]
            result["summary"] = " ".join(summary_parts)

        # Tags
        tag_els = soup.select("[class*='tags'] a") or soup.select("[class*='topic'] a")
        result["tags"] = [t.get_text(strip=True) for t in tag_els if t.get_text(strip=True)]

        # OG image
        og_img = soup.select_one("meta[property='og:image']")
        if og_img:
            result["image_url"] = og_img.get("content")

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
        Fetch latest news from NDTV Profit.

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
        html = self._session.get_html(f"{_BASE_URL}/the-latest")
        articles = self._parse_news_listing(html, category="latest")[:limit]
        return self._to_output(articles, output)

    def market_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch markets section news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/markets")
        articles = self._parse_news_listing(html, category="markets")[:limit]
        return self._to_output(articles, output)

    def economy_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch economy & policy news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/economy-finance")
        articles = self._parse_news_listing(html, category="economy")[:limit]
        return self._to_output(articles, output)

    def opinion_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch opinion and analysis articles.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/opinion")
        articles = self._parse_news_listing(html, category="opinion")[:limit]
        return self._to_output(articles, output)

    def technology_news(self, limit: int = 25, output: str = "dataframe"):
        """
        Fetch technology news.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(f"{_BASE_URL}/technology")
        articles = self._parse_news_listing(html, category="technology")[:limit]
        return self._to_output(articles, output)

    def stock_news(self, symbol: str, limit: int = 15, output: str = "dataframe"):
        """
        Fetch news for a specific stock/topic.

        Parameters
        ----------
        symbol : str
            Stock symbol or topic name (e.g., ``"reliance"``, ``"tcs"``).
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        slug = symbol.lower().replace(" ", "-")
        html = self._session.get_html(f"{_BASE_URL}/topic/{slug}")
        articles = self._parse_news_listing(html, category=f"stock:{symbol.upper()}")[:limit]
        return self._to_output(articles, output)

    def trending_news(self, limit: int = 10, output: str = "dataframe"):
        """
        Fetch trending stories from the homepage.

        Parameters
        ----------
        limit : int
            Max articles to return.
        output : str
            ``"dataframe"`` or ``"json"``.
        """
        html = self._session.get_html(_BASE_URL)
        if not html:
            return pd.DataFrame() if output == "dataframe" else []

        soup = BeautifulSoup(html, "lxml")
        trending = (
            soup.select("[class*='trending'] a") or
            soup.select("[class*='topStory'] a") or
            soup.select("[class*='hero'] a")
        )

        articles = []
        seen = set()
        for link in trending:
            title = link.get("title", "") or link.get_text(strip=True)
            href  = link.get("href", "")
            if not title or len(title) < 15 or not href:
                continue
            if not href.startswith("http"):
                href = urljoin(_BASE_URL, href)
            if href in seen:
                continue
            seen.add(href)
            articles.append(NewsArticle(
                title=title,
                url=href,
                source="ndtvprofit",
                category="trending",
            ))
            if len(articles) >= limit:
                break

        return self._to_output(articles, output)

    def article_detail(self, url: str) -> dict:
        """
        Fetch full article content from an NDTV Profit article URL.

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
