"""Tests for src/market_wire.py — schema, escaping, render safety."""
from __future__ import annotations

from unittest.mock import patch

from src import calendar_source, market_wire, news
from src.reports.daily_morning import _wire_block


def _sample_item(**overrides) -> market_wire.WireItem:
    defaults = dict(
        country_code="US",
        lead_emoji="🔴",
        headline="The 30-year US Treasury yield hit 5.35%, its highest since June 2007.",
        significance=(
            "Higher real yields raise the discount rate on future cash flows, "
            "compressing growth multiples. With DXY firm and VIX calm, the "
            "flow is orderly rotation from duration equities into banks."
        ),
        impact_usd="+",
        impact_gold="-",
        impact_stocks="-",
        impact_crypto="-",
        key_sector="Real Estate −−",
        knowledge_sources_used=["knowledge/macro/impact_matrix.md"],
    )
    defaults.update(overrides)
    return market_wire.WireItem(**defaults)


def test_country_flag_maps_known_codes():
    assert market_wire.country_flag("US") == "🇺🇸"
    assert market_wire.country_flag("EU") == "🇪🇺"
    assert market_wire.country_flag("GLOBAL") == "🌐"
    # Unknown code falls back to globe (never blocks the render)
    assert market_wire.country_flag("ZZ") == "🌐"


def test_wire_block_renders_three_items():
    items = [_sample_item(), _sample_item(country_code="EU", lead_emoji="🟡"),
             _sample_item(country_code="GLOBAL", lead_emoji="🟢")]
    out = _wire_block(items)
    # All three flags render
    assert "🇺🇸" in out
    assert "🇪🇺" in out
    assert "🌐" in out
    # Numbering present
    assert "*1\\.*" in out
    assert "*2\\.*" in out
    assert "*3\\.*" in out
    # Impact glyphs present (+ → green, - → red)
    assert "🟢" in out  # USD +
    assert "🔴" in out  # gold/stocks/crypto -


def test_wire_block_escapes_mdv2_reserved_chars():
    """§C7, §E.1 — every dynamic string must pass through esc()."""
    item = _sample_item(
        headline="Yields hit 5.35% (highest since 2007)! Fed's next move?",
        significance="Rate-move mechanics: 10Y > 5% breaks the 20-year range.",
        key_sector="REITs (very negative)",
    )
    out = _wire_block([item])
    # Escaped tokens for MDv2 reserved chars — dots, parens, exclamation
    assert "5\\.35" in out or "5\\.35%" in out
    assert "\\(" in out
    assert "\\)" in out
    assert "\\!" in out
    # Unescaped raw '.' should NOT appear next to numeric text in the headline
    # (the '.' between digits must be escaped). Sanity-check on the injected content.
    assert " 5.35% " not in out  # unescaped form must not survive


def test_wire_block_empty_items_shows_sentinel():
    out = _wire_block([])
    assert "No wire items" in out


def test_wire_block_handles_missing_key_sector():
    item = _sample_item(key_sector="")
    out = _wire_block([item])
    # Impact line should still render with only the 4 assets, no trailing sector
    assert "USD" in out and "Gold" in out and "Stocks" in out and "Crypto" in out
    # A well-formed impact line ending; no dangling separator
    assert "  ·  \n" not in out


def test_filtered_headlines_drops_non_macro_titles():
    """Macro keyword filter must drop pure single-name/opinion headlines."""
    fake = [
        news.Headline("Reuters", "Fed hints at pause as CPI cools", None, ""),
        news.Headline("WSJ", "Celebrity chef opens new restaurant", None, ""),
        news.Headline("MW", "10-year Treasury yield spikes on hawkish Powell speech", None, ""),
        news.Headline("CNBC", "Local sports team wins championship", None, ""),
    ]
    with patch.object(news, "fetch_headlines", return_value=fake):
        out = market_wire._filtered_headlines(cap=10)
    titles = [h.title for h in out]
    assert any("Fed" in t for t in titles)
    assert any("Treasury" in t for t in titles)
    assert not any("restaurant" in t.lower() for t in titles)
    assert not any("sports" in t.lower() for t in titles)


def test_filtered_headlines_dedupes():
    """RSS feeds often cross-post the same wire story — dedupe on normalized title."""
    fake = [
        news.Headline("Reuters", "Fed hints at pause as CPI cools", None, ""),
        news.Headline("Yahoo", "Fed  hints at pause as CPI cools", None, ""),  # extra space
        news.Headline("WSJ", "FED HINTS AT PAUSE AS CPI COOLS", None, ""),      # case diff
    ]
    with patch.object(news, "fetch_headlines", return_value=fake):
        out = market_wire._filtered_headlines(cap=10)
    assert len(out) == 1


def test_calendar_lines_empty_day():
    empty = market_wire._calendar_lines_for_llm([], "2026-09-16")
    assert "no 3-star events" in empty.lower()


def test_calendar_lines_only_3star():
    """Only 3-star events pass through to the LLM prompt (matches display)."""
    events = [
        calendar_source.CalendarEvent(
            date_ist="2026-09-16", time_ist="15:30", country="US",
            event_name="CPI m/m", importance=3, forecast="0.3%",
            previous="0.2%", actual=None, source="test",
        ),
        calendar_source.CalendarEvent(
            date_ist="2026-09-16", time_ist="10:00", country="EU",
            event_name="Trade Balance", importance=2, forecast="20B",
            previous="18B", actual=None, source="test",
        ),
    ]
    out = market_wire._calendar_lines_for_llm(events, "2026-09-16")
    assert "CPI" in out
    assert "Trade Balance" not in out


def test_wire_schema_has_named_slots():
    """Groq strict decoder requires named top-level slots, not arrays."""
    assert set(market_wire._WIRE_SCHEMA["required"]) == {"item_1", "item_2", "item_3"}
    item_schema = market_wire._WIRE_ITEM_SCHEMA
    # Cross-asset direction enums are locked to {+, -, ~}
    for k in ("impact_usd", "impact_gold", "impact_stocks", "impact_crypto"):
        assert set(item_schema["properties"][k]["enum"]) == {"+", "-", "~"}
    assert set(item_schema["properties"]["country_code"]["enum"]) == {
        "US", "EU", "UK", "JP", "CN", "GLOBAL",
    }


def test_impact_glyph_covers_all_enum_values():
    """The renderer must have a glyph for every schema-valid impact value —
    KeyError here would blow the report at generation time."""
    from src.reports.daily_morning import _IMPACT_GLYPH
    for v in ("+", "-", "~"):
        assert v in _IMPACT_GLYPH


def test_impact_matrix_knowledge_file_exists_and_populated():
    """§C15 discipline: the impact_matrix must exist and not be a stub."""
    from src import config, knowledge
    p = config.KNOWLEDGE_DIR / "macro" / "impact_matrix.md"
    assert p.exists(), "knowledge/macro/impact_matrix.md missing — market_wire cannot ground impact directions"
    chunk = knowledge._read_chunk(p)
    assert chunk is not None
    assert not knowledge._is_stub(chunk), "impact_matrix.md is a stub — LLM has no impact rules to apply"
