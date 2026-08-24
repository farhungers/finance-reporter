"""End-to-end wireup tests for the Phase 2 US-macro plumbing.

Covers:
  - knowledge.load_for_report pulls the matching macro playbook when a US 3-star
    event is on today's calendar (daily_morning only)
  - pitches._thesis_mentions_macro accepts common aliases correctly
  - daily_morning._us_3star_event_names extracts USD/US/USA-flagged events
  - daily_morning._calendar_block renders the 3-line format for US 3-star and
    respects the length-budget cap for high-event days
"""
from __future__ import annotations

from src import calendar_source, knowledge, pitches
from src.reports.daily_morning import (
    _US_DETAILED_EVENT_CAP,
    _calendar_block,
    _us_3star_event_names,
)


def _evt(name: str, country: str = "USD", imp: int = 3, date: str = "2026-08-25", time: str = "15:30"):
    return calendar_source.CalendarEvent(
        date_ist=date, time_ist=time, country=country, event_name=name,
        importance=imp, forecast=None, previous=None, actual=None, source="test",
    )


def test_load_for_report_pulls_matching_macro_playbook_for_cpi():
    out = knowledge.load_for_report(
        "daily_morning", tickers=[], todays_event_names=["CPI m/m"],
    )
    assert any("cpi_playbook.md" in sid for sid in out), (
        f"expected cpi_playbook loaded, got: {list(out)}"
    )


def test_load_for_report_pulls_fomc_playbook_for_fomc_statement():
    out = knowledge.load_for_report(
        "daily_morning", tickers=[], todays_event_names=["FOMC Statement"],
    )
    assert any("fomc_playbook.md" in sid for sid in out)


def test_load_for_report_skips_playbook_without_matching_event():
    out = knowledge.load_for_report(
        "daily_morning", tickers=[], todays_event_names=["German ZEW Economic Sentiment"],
    )
    assert not any("cpi_playbook.md" in sid for sid in out)
    assert not any("fomc_playbook.md" in sid for sid in out)


def test_load_for_report_daily_wrap_does_not_load_macro_playbook():
    """Only daily_morning gets the macro-playbook injection — wrap has a
    different LLM prompt (pre-open outlook) that doesn't need the playbook."""
    out = knowledge.load_for_report(
        "daily_wrap", tickers=[], todays_event_names=["CPI m/m"],
    )
    assert not any("cpi_playbook.md" in sid for sid in out)


def test_thesis_mentions_macro_matches_cpi_aliases():
    from src.pitches import _thesis_mentions_macro
    assert _thesis_mentions_macro("Watch for the CPI print today.", ["CPI m/m"])
    assert _thesis_mentions_macro("Inflation prints Wednesday.", ["CPI m/m"])
    assert _thesis_mentions_macro("With consumer price data on tap...", ["CPI m/m"])
    assert not _thesis_mentions_macro("Apple reports earnings.", ["CPI m/m"])


def test_thesis_mentions_macro_matches_fomc_aliases():
    from src.pitches import _thesis_mentions_macro
    assert _thesis_mentions_macro("Powell speaks at 2pm.", ["Federal Funds Rate"])
    assert _thesis_mentions_macro("Fed decision today.", ["FOMC Statement"])
    assert _thesis_mentions_macro("Rate decision incoming.", ["FOMC Statement"])


def test_thesis_mentions_macro_vacuously_true_when_no_events():
    from src.pitches import _thesis_mentions_macro
    assert _thesis_mentions_macro("Any thesis text.", [])


def test_us_3star_event_names_extracts_usd_flagged():
    events = [
        _evt("CPI m/m", country="USD"),
        _evt("German ZEW Economic Sentiment", country="EUR"),
        _evt("Retail Sales m/m", country="US"),
        _evt("NFP", country="USD", imp=2),  # not 3-star
    ]
    names = _us_3star_event_names(events, "2026-08-25")
    assert "CPI m/m" in names
    assert "Retail Sales m/m" in names
    assert "German ZEW Economic Sentiment" not in names
    assert "NFP" not in names  # importance filter


def test_calendar_block_renders_3_line_format_for_us_events():
    events = [_evt("CPI m/m", country="USD")]
    block = _calendar_block(events, "2026-08-25")
    # 3-line format uses the 📘 What and 📈 Effect markers
    assert "📘" in block
    assert "📈" in block


def test_calendar_block_respects_us_detailed_cap():
    """Only _US_DETAILED_EVENT_CAP events get the 3-line format; overflow falls
    back to 1-line. This is the Phase 4.4 length-budget guardrail."""
    events = [
        _evt(f"CPI m/m", country="USD", time=f"{10+i:02d}:00")
        for i in range(_US_DETAILED_EVENT_CAP + 2)  # exceed cap
    ]
    block = _calendar_block(events, "2026-08-25")
    # 📘 count == number of full-format cards, bounded by cap
    assert block.count("📘") == _US_DETAILED_EVENT_CAP


def test_calendar_block_non_us_uses_compact_format():
    events = [_evt("German CPI m/m", country="EUR")]
    block = _calendar_block(events, "2026-08-25")
    # Non-US events keep the 1-line effect format (no 📘 marker)
    assert "📘" not in block
