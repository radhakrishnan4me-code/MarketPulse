"""
MarketPulse — Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Central configuration panel for all scraper instances.
Mirrors NseKit's NseConfig pattern.
"""

import threading


class MarketPulseConfig:
    """
    Central configuration for all ``Moneycontrol`` and ``NdtvProfit`` instances.

    Every field is a **class attribute** — there are no instances.
    Changes take effect immediately for all subsequent HTTP calls.

    Attributes
    ----------
    max_rps : float
        Maximum requests per second (shared via token-bucket).  Default ``2.0``.
    retries : int
        Extra retry attempts after first failure.  Default ``3``.
    retry_delay : float
        Base sleep between retries (doubles each attempt).  Default ``2.0``.
    cookie_cache : bool
        Enable on-disk cookie caching.  Default ``True``.
    """

    max_rps:      float = 2.0
    retries:      int   = 3
    retry_delay:  float = 2.0
    cookie_cache: bool  = True

    # ── Internal rate-limit state ─────────────────────────────────────
    _lock:        threading.Lock = threading.Lock()
    _tokens:      float          = 2.0
    _last_refill: float          = 0.0

    def __init_subclass__(cls, **kw):
        raise TypeError("MarketPulseConfig is not meant to be subclassed")

    def __new__(cls):
        raise TypeError("MarketPulseConfig is a namespace — do not instantiate it")
