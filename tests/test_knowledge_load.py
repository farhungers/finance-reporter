"""Knowledge loader — CLAUDE.md §D.7. Applies_to_reports filter, ticker facts, always-included files."""
from src import knowledge
from src.market_data import BLUE_CHIP_UNIVERSE


def test_load_returns_house_view_active_themes_always():
    out = knowledge.load_for_report("daily_wrap", tickers=[])
    assert any("active_themes.md" in sid for sid in out), out.keys()


def test_load_returns_client_language_for_pitch_reports():
    out = knowledge.load_for_report("daily_morning", tickers=[])
    assert any("client_language.md" in sid for sid in out)


def test_load_omits_client_language_for_wrap():
    out = knowledge.load_for_report("daily_wrap", tickers=[])
    assert not any("client_language.md" in sid for sid in out)


def test_load_skips_stub_ticker_facts(tmp_path):
    """Stub-scaffold ticker facts are correctly skipped by load_for_report to
    conserve LLM tokens. §E.19 presence check uses verify_blue_chip_coverage
    (file existence), not load_for_report (content quality)."""
    ticker = BLUE_CHIP_UNIVERSE[0]
    out = knowledge.load_for_report("daily_morning", tickers=[ticker])
    # As of Session 0, all blue_chip files are stubs, so none should appear here.
    assert not any(f"blue_chip/{ticker}_facts.md" in sid for sid in out), (
        "stub ticker fact leaked into LLM context — over-eager to conserve tokens? "
        "Verify stub-detection heuristic in knowledge._is_stub"
    )
    # But the file must still exist for §E.19 enforcement
    present, missing = knowledge.verify_blue_chip_coverage((ticker,))
    assert present == [ticker]
    assert missing == []


def test_source_id_format():
    out = knowledge.load_for_report("daily_morning", tickers=[BLUE_CHIP_UNIVERSE[0]])
    for sid in out:
        assert sid.startswith("knowledge/"), sid


def test_build_context_block_has_source_id_tags():
    out = knowledge.load_for_report("daily_morning", tickers=[BLUE_CHIP_UNIVERSE[0]])
    block = knowledge.build_context_block(out)
    for sid in out:
        assert sid in block
