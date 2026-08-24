"""US event definitions + playbook-mapping tests (2026-08-24 roadmap Phase 1-2)."""
from __future__ import annotations

from src import event_explanations as ee


def test_what_is_returns_definition_for_us_core_releases():
    assert ee.what_is("CPI m/m")
    assert "consumer" in ee.what_is("CPI m/m").lower()
    assert "bls" in ee.what_is("Non-Farm Employment Change").lower() or "employer" in ee.what_is("Non-Farm Employment Change").lower()
    assert ee.what_is("Federal Funds Rate")
    assert "fed" in ee.what_is("Federal Funds Rate").lower()


def test_what_is_returns_none_for_unknown():
    assert ee.what_is("Some Made-Up Event") is None
    assert ee.what_is("") is None


def test_explain_full_returns_both_fields():
    r = ee.explain_full("CPI m/m")
    assert r["what_it_is"]
    assert r["market_effect"]
    r2 = ee.explain_full("Some Made-Up Event")
    assert r2["what_it_is"] is None
    assert r2["market_effect"] is None


def test_matching_playbook_maps_cpi_and_variants():
    assert ee.matching_playbook("CPI m/m") == "cpi_playbook.md"
    assert ee.matching_playbook("Core CPI m/m") == "cpi_playbook.md"
    # Longer key ('core pce') beats shorter ('pce')
    assert ee.matching_playbook("Core PCE Price Index m/m") == "pce_playbook.md"


def test_matching_playbook_maps_fomc_variants():
    assert ee.matching_playbook("FOMC Statement") == "fomc_playbook.md"
    assert ee.matching_playbook("FOMC Meeting Minutes") == "fomc_playbook.md"
    assert ee.matching_playbook("FOMC Economic Projections") == "dot_plot_playbook.md"


def test_matching_playbook_maps_jobs_variants():
    assert ee.matching_playbook("Non-Farm Employment Change") == "nfp_playbook.md"
    assert ee.matching_playbook("Unemployment Rate") == "nfp_playbook.md"
    assert ee.matching_playbook("Average Hourly Earnings m/m") == "nfp_playbook.md"
    assert ee.matching_playbook("JOLTS Job Openings") == "jolts_playbook.md"


def test_matching_playbook_maps_treasury_auctions():
    assert ee.matching_playbook("10-y Bond Auction") == "treasury_auctions.md"
    assert ee.matching_playbook("30-y Bond Auction") == "treasury_auctions.md"
    assert ee.matching_playbook("3-y Note Auction") == "treasury_auctions.md"


def test_matching_playbook_returns_none_for_unmapped():
    # NOTE: matching_playbook is intentionally country-agnostic — its callers
    # (knowledge.load_for_report via daily_morning._us_3star_event_names) filter
    # to US events before calling. A "German CPI" event never reaches this
    # function in the daily_morning flow. So we only assert on strings that
    # have no substring match in EVENT_TO_PLAYBOOK.
    assert ee.matching_playbook("Bank Holiday") is None
    assert ee.matching_playbook("") is None
    assert ee.matching_playbook("Some Made Up Release") is None


def test_playbook_files_actually_exist():
    """Every filename in EVENT_TO_PLAYBOOK must correspond to a real file — fail
    fast if a playbook reference dangles into a missing file."""
    from pathlib import Path
    from src import config
    referenced = set(ee.EVENT_TO_PLAYBOOK.values())
    for fname in referenced:
        p = config.KNOWLEDGE_DIR / "macro" / fname
        assert p.exists(), f"EVENT_TO_PLAYBOOK references missing file: {fname}"


def test_us_definitions_cover_all_playbook_events():
    """Any event that maps to a playbook should also have a what_is definition.
    Otherwise the daily_morning 3-line card will render only 2 lines for that
    event even though the deep playbook exists."""
    missing: list[str] = []
    for evt_substring in ee.EVENT_TO_PLAYBOOK.keys():
        if ee.what_is(evt_substring) is None:
            missing.append(evt_substring)
    assert not missing, f"missing what_is definitions for: {missing}"
