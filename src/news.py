"""RSS headline aggregation (CLAUDE.md §B.3). Free, no key. NewsAPI is PROHIBITED.

Primary sources: Reuters biz, Yahoo Finance markets, WSJ market pulse, Bloomberg headlines.
Fallback: Google Finance news RSS.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import feedparser

log = logging.getLogger(__name__)

FEEDS: tuple[tuple[str, str], ...] = (
    ("Reuters Business", "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    ("WSJ Markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
    ("MarketWatch Top", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
    ("CNBC Markets", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
    ("SeekingAlpha Market Currents", "https://seekingalpha.com/market_currents.xml"),
)


@dataclass(frozen=True)
class Headline:
    source: str
    title: str
    published_utc: Optional[str]
    link: str


def fetch_headlines(max_per_feed: int = 8) -> list[Headline]:
    out: list[Headline] = []
    for source, url in FEEDS:
        try:
            f = feedparser.parse(url)
            for entry in f.entries[:max_per_feed]:
                pub = None
                if getattr(entry, "published_parsed", None):
                    pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                out.append(
                    Headline(
                        source=source,
                        title=getattr(entry, "title", "").strip(),
                        published_utc=pub,
                        link=getattr(entry, "link", ""),
                    )
                )
        except Exception as e:
            log.warning("RSS fetch failed for %s: %s", source, e)
    return out
