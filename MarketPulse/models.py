"""
MarketPulse — Data Models
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unified data models for news articles from all sources.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class NewsArticle:
    """
    Unified schema for a news article from any source.

    Attributes
    ----------
    title : str
        Headline of the article.
    url : str
        Full URL to the article.
    summary : str
        Lead paragraph or short description.
    published_at : str
        Publication timestamp as string.
    source : str
        Source identifier: ``"moneycontrol"`` or ``"ndtvprofit"``.
    category : str
        News category: ``"latest"``, ``"markets"``, ``"economy"``, etc.
    image_url : str or None
        URL of the article's thumbnail image.
    author : str or None
        Author name if available.
    tags : list[str]
        Associated tags/keywords.
    """

    title:        str
    url:          str
    summary:      str            = ""
    published_at: str            = ""
    source:       str            = ""
    category:     str            = ""
    image_url:    Optional[str]  = None
    author:       Optional[str]  = None
    tags:         list[str]      = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to plain dictionary."""
        return asdict(self)
