"""
MarketPulse — Base Session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shared HTTP transport with cookie management, UA rotation,
rate limiting, and retry logic.  Mirrors NseKit's Nse session pattern.
"""

import json
import logging
import os
import random
import time

import requests

from .config import MarketPulseConfig

logger = logging.getLogger(__name__)

_USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) "
    "Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) "
    "Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


class BaseSession:
    """
    HTTP session wrapper with NseKit-style infrastructure.

    Features
    --------
    - Rotating User-Agent pool
    - Cookie warm-up + on-disk caching
    - Token-bucket rate limiter (shared across all instances)
    - Automatic retry with exponential backoff

    Parameters
    ----------
    site_name : str
        Identifier for cookie cache file (e.g. ``"moneycontrol"``).
    base_referer : str
        Default ``Referer`` header for all requests.
    warmup_urls : list[str]
        URLs to GET during session warm-up for cookie establishment.
    max_rps : float, optional
        Override ``MarketPulseConfig.max_rps``.
    retries : int, optional
        Override ``MarketPulseConfig.retries``.
    retry_delay : float, optional
        Override ``MarketPulseConfig.retry_delay``.
    cookie_cache : bool, optional
        Override ``MarketPulseConfig.cookie_cache``.
    """

    _COOKIE_TTL = 3600  # 1 hour

    def __init__(
        self,
        site_name:    str,
        base_referer: str,
        warmup_urls:  list[str],
        max_rps:      float | None = None,
        retries:      int   | None = None,
        retry_delay:  float | None = None,
        cookie_cache: bool  | None = None,
    ):
        self.site_name    = site_name
        self.base_referer = base_referer
        self.warmup_urls  = warmup_urls

        self.max_rps      = max_rps      if max_rps      is not None else MarketPulseConfig.max_rps
        self.retries      = retries      if retries      is not None else MarketPulseConfig.retries
        self.retry_delay  = retry_delay  if retry_delay  is not None else MarketPulseConfig.retry_delay
        self.cookie_cache = cookie_cache if cookie_cache is not None else MarketPulseConfig.cookie_cache

        self._cookie_path = os.path.join(
            os.path.expanduser("~"), f".marketpulse_{site_name}_cache.json"
        )

        self.session = requests.Session()
        ua = random.choice(_USER_AGENTS)
        self.headers = {
            "User-Agent":       ua,
            "Accept":           "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language":  "en-US,en;q=0.9",
            "Accept-Encoding":  "gzip, deflate",
            "Referer":          base_referer,
            "Connection":       "keep-alive",
            "Sec-Ch-Ua":        '"Chromium";v="125", "Not=A?Brand";v="24", "Google Chrome";v="125"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest":   "document",
            "Sec-Fetch-Mode":   "navigate",
            "Sec-Fetch-Site":   "same-origin",
            "Sec-Fetch-User":   "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control":    "max-age=0",
        }
        # Also set UA on the session itself for redirects
        self.session.headers.update({"User-Agent": ua})

        if self.cookie_cache and self._load_cookies():
            return
        self._warm_up()

    # ── Rate Limiting ─────────────────────────────────────────────────

    def _throttle(self) -> None:
        """Token-bucket rate limiter shared across all instances."""
        cap = self.max_rps
        while True:
            with MarketPulseConfig._lock:
                now     = time.monotonic()
                elapsed = now - MarketPulseConfig._last_refill
                MarketPulseConfig._tokens      = min(cap, MarketPulseConfig._tokens + elapsed * cap)
                MarketPulseConfig._last_refill = now
                if MarketPulseConfig._tokens >= 1.0:
                    MarketPulseConfig._tokens -= 1.0
                    return
                wait = (1.0 - MarketPulseConfig._tokens) / cap
            time.sleep(wait)

    # ── User-Agent Rotation ───────────────────────────────────────────

    def rotate_user_agent(self) -> None:
        """Randomly rotate the User-Agent header."""
        self.headers["User-Agent"] = random.choice(_USER_AGENTS)

    # ── Cookie Management ─────────────────────────────────────────────

    def _load_cookies(self) -> bool:
        """Load cookies from on-disk cache if fresh."""
        try:
            with open(self._cookie_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if time.time() - data.get("ts", 0.0) < self._COOKIE_TTL:
                for k, v in data.get("cookies", {}).items():
                    self.session.cookies.set(k, v)
                logger.debug("MarketPulse[%s]: cookies loaded from cache", self.site_name)
                return True
        except Exception:
            pass
        return False

    def _save_cookies(self) -> None:
        """Persist cookies to disk cache."""
        if not self.cookie_cache:
            return
        cookies = dict(self.session.cookies)
        if not cookies:
            return
        tmp = self._cookie_path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"ts": time.time(), "cookies": cookies}, fh)
            os.replace(tmp, self._cookie_path)
            logger.debug("MarketPulse[%s]: %d cookie(s) saved", self.site_name, len(cookies))
        except Exception as exc:
            logger.debug("MarketPulse[%s]: cookie save failed: %s", self.site_name, exc)
            try:
                os.remove(tmp)
            except OSError:
                pass

    def _warm_up(self) -> None:
        """Perform warm-up GETs to establish session cookies."""
        for url in self.warmup_urls:
            try:
                self._throttle()
                resp = self.session.get(url, headers=self.headers, timeout=15, allow_redirects=True)
                logger.debug("MarketPulse[%s]: warm-up %s → %d", self.site_name, url, resp.status_code)
            except Exception as exc:
                logger.debug("MarketPulse[%s]: warm-up failed (%s): %s", self.site_name, url, exc)
        time.sleep(1.0)
        self._save_cookies()

    # ── Retry Logic ───────────────────────────────────────────────────

    def _retry(self, fn, retries: int | None = None, delay: float | None = None):
        """Call fn() up to 1 + retries times with exponential backoff."""
        n = self.retries     if retries is None else retries
        d = self.retry_delay if delay   is None else delay
        last_exc = None
        for attempt in range(n + 1):
            try:
                return fn()
            except Exception as exc:
                last_exc = exc
                if attempt < n:
                    time.sleep(d * (2 ** attempt))
        raise last_exc

    # ── Core Fetch Methods ────────────────────────────────────────────

    def get_html(self, url: str, params: dict | None = None, timeout: int = 15) -> str | None:
        """
        Fetch a URL and return raw HTML text.
        Returns None on failure.
        """
        try:
            def _fetch():
                self.rotate_user_agent()
                self._throttle()
                resp = self.session.get(url, headers=self.headers, params=params, timeout=timeout)
                resp.raise_for_status()
                return resp.text
            return self._retry(_fetch)
        except Exception as exc:
            logger.warning("MarketPulse[%s]: GET failed %s: %s", self.site_name, url, exc)
            return None

    def get_json(self, url: str, params: dict | None = None, timeout: int = 15) -> dict | list | None:
        """
        Fetch a URL and return parsed JSON.
        Returns None on failure.
        """
        try:
            def _fetch():
                self.rotate_user_agent()
                self._throttle()
                resp = self.session.get(url, headers=self.headers, params=params, timeout=timeout)
                resp.raise_for_status()
                return resp.json()
            return self._retry(_fetch)
        except Exception as exc:
            logger.warning("MarketPulse[%s]: JSON GET failed %s: %s", self.site_name, url, exc)
            return None
