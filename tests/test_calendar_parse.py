"""ForexFactory XML parse — CLAUDE.md §B.3."""
from src.calendar_source import _parse_xml

_SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<weeklyevents>
  <event>
    <title>Core CPI m/m</title>
    <country>USD</country>
    <date><![CDATA[07-30-2026]]></date>
    <time><![CDATA[8:30am]]></time>
    <impact><![CDATA[High]]></impact>
    <forecast><![CDATA[0.3%]]></forecast>
    <previous><![CDATA[0.4%]]></previous>
  </event>
  <event>
    <title>Bank Holiday</title>
    <country>GBP</country>
    <date><![CDATA[07-28-2026]]></date>
    <time><![CDATA[All Day]]></time>
    <impact><![CDATA[Holiday]]></impact>
  </event>
  <event>
    <title>Fed Chair Powell Speaks</title>
    <country>USD</country>
    <date><![CDATA[07-29-2026]]></date>
    <time><![CDATA[2:00pm]]></time>
    <impact><![CDATA[High]]></impact>
  </event>
</weeklyevents>
"""


def test_parse_basic():
    events = _parse_xml(_SAMPLE_XML)
    assert len(events) == 3


def test_impact_mapped():
    events = _parse_xml(_SAMPLE_XML)
    cpi = next(e for e in events if "CPI" in e.event_name)
    assert cpi.importance == 3
    holiday = next(e for e in events if "Holiday" in e.event_name)
    assert holiday.importance == 0


def test_time_converted_to_ist():
    """8:30am ET = 15:30 IST (EDT UTC-4, IST UTC+3, in DST months)."""
    events = _parse_xml(_SAMPLE_XML)
    cpi = next(e for e in events if "CPI" in e.event_name)
    # In July 2026, ET is EDT (UTC-4), IST is UTC+3 → +7h from ET
    # 08:30 ET → 15:30 IST
    assert cpi.time_ist == "15:30"


def test_all_day_no_time():
    events = _parse_xml(_SAMPLE_XML)
    holiday = next(e for e in events if "Holiday" in e.event_name)
    assert holiday.time_ist is None


def test_forecast_previous_captured():
    events = _parse_xml(_SAMPLE_XML)
    cpi = next(e for e in events if "CPI" in e.event_name)
    assert cpi.forecast == "0.3%"
    assert cpi.previous == "0.4%"
