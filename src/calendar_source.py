"""Economic calendar fetch — ForexFactory weekly XML (100% free, no key, no rate limit).

CLAUDE.md §B.3 primary source. Fallback: TradingEconomics guest (guest:guest).
Prohibited: Investing.com scraping (§G.1).
"""
from __future__ import annotations

import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

from src import config

log = logging.getLogger(__name__)

_FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
_FF_URL_FALLBACK = "https://www.forexfactory.com/ffcal_week_this.xml"
_CACHE_TTL_SEC = 6 * 3600  # 6 hours — calendar is essentially static within a day

# In-process cache — dedupes fetches within a single report generation
_MEM_CACHE: dict[str, tuple[float, list]] = {}


@dataclass(frozen=True)
class CalendarEvent:
    date_ist: str          # YYYY-MM-DD in Europe/Istanbul
    time_ist: Optional[str]  # HH:MM or None (All Day / Tentative)
    country: str
    event_name: str
    importance: int        # 1/2/3
    forecast: Optional[str]
    previous: Optional[str]
    actual: Optional[str]
    source: str = "forexfactory"


_IMPACT_MAP = {"High": 3, "Medium": 2, "Low": 1, "Holiday": 0, "None": 0}


def _parse_ff_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """ForexFactory XML: date=MM-DD-YYYY, time=H:MMam/pm or 'All Day' / 'Tentative'."""
    try:
        d = datetime.strptime(date_str.strip(), "%m-%d-%Y")
    except ValueError:
        return None
    t = (time_str or "").strip().lower()
    if not t or t in {"all day", "tentative"}:
        return d.replace(tzinfo=config.TZ_ET)
    try:
        parsed_t = datetime.strptime(t.replace(" ", ""), "%I:%M%p").time()
    except ValueError:
        return None
    return datetime.combine(d.date(), parsed_t).replace(tzinfo=config.TZ_ET)


def _cache_path() -> Path:
    cache_dir = config.DATA_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"ff_calendar_{datetime.now(UTC).strftime('%Y%m%d')}.xml"


def fetch_week(force: bool = False) -> list[CalendarEvent]:
    """Fetch current week calendar from ForexFactory with two-tier cache.

    Tier 1: in-process memory cache (dedupes within a report run).
    Tier 2: file cache in data/cache/ with 6-hour TTL (dedupes across reports).
    """
    key = "week"
    now = time.time()
    if not force:
        # in-memory
        hit = _MEM_CACHE.get(key)
        if hit and now - hit[0] < _CACHE_TTL_SEC:
            return hit[1]
        # file cache
        p = _cache_path()
        if p.exists() and now - p.stat().st_mtime < _CACHE_TTL_SEC:
            try:
                events = _parse_xml(p.read_text(encoding="utf-8"))
                _MEM_CACHE[key] = (now, events)
                return events
            except Exception as e:
                log.warning("cache parse failed, refetching: %s", e)

    for url in (_FF_URL, _FF_URL_FALLBACK):
        try:
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            _cache_path().write_text(r.text, encoding="utf-8")
            events = _parse_xml(r.text)
            _MEM_CACHE[key] = (now, events)
            return events
        except Exception as e:
            log.warning("ForexFactory fetch failed at %s: %s", url, e)
    # If both endpoints fail but we have any file cache (even stale), return it.
    p = _cache_path()
    if p.exists():
        log.warning("using stale file cache after fetch failures")
        try:
            events = _parse_xml(p.read_text(encoding="utf-8"))
            _MEM_CACHE[key] = (now, events)
            return events
        except Exception:
            pass
    log.error("ForexFactory unreachable via both URLs and no cache")
    return []


def _parse_xml(xml_text: str) -> list[CalendarEvent]:
    root = ET.fromstring(xml_text)
    out: list[CalendarEvent] = []
    for event in root.findall("event"):
        title = (event.findtext("title") or "").strip()
        country = (event.findtext("country") or "").strip()
        date_s = (event.findtext("date") or "").strip()
        time_s = (event.findtext("time") or "").strip()
        impact = (event.findtext("impact") or "").strip()
        forecast = (event.findtext("forecast") or "").strip() or None
        previous = (event.findtext("previous") or "").strip() or None
        actual = (event.findtext("actual") or "").strip() or None

        dt_et = _parse_ff_datetime(date_s, time_s)
        if dt_et is None:
            continue
        dt_ist = dt_et.astimezone(config.TZ_IST)
        has_time = bool(time_s) and time_s.lower() not in {"all day", "tentative"}
        out.append(
            CalendarEvent(
                date_ist=dt_ist.strftime("%Y-%m-%d"),
                time_ist=dt_ist.strftime("%H:%M") if has_time else None,
                country=country,
                event_name=title,
                importance=_IMPACT_MAP.get(impact, 0),
                forecast=forecast,
                previous=previous,
                actual=actual,
            )
        )
    return out


def three_star_events_for_day(events: list[CalendarEvent], target_date_ist: str) -> list[CalendarEvent]:
    return [e for e in events if e.date_ist == target_date_ist and e.importance >= 3]


def events_for_day(events: list[CalendarEvent], target_date_ist: str, min_importance: int = 1) -> list[CalendarEvent]:
    return [e for e in events if e.date_ist == target_date_ist and e.importance >= min_importance]


def events_next_n_days(events: list[CalendarEvent], start_date_ist: str, n: int, min_importance: int = 3) -> list[CalendarEvent]:
    start = datetime.strptime(start_date_ist, "%Y-%m-%d").date()
    dates = {(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)}
    return [e for e in events if e.date_ist in dates and e.importance >= min_importance]
