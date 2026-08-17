"""Knowledge loader — CLAUDE.md §D.7. Applies_to_reports filter, ticker facts, always-included files."""
import pytest

from src import config, knowledge
from src.market_data import BLUE_CHIP_UNIVERSE


def _find_stub_ticker() -> str | None:
    """Find the first blue-chip ticker whose facts file is still a stub. Returns
    None if every ticker has been populated (a happy problem — test skips)."""
    for t in BLUE_CHIP_UNIVERSE:
        p = config.KNOWLEDGE_DIR / "blue_chip" / f"{t}_facts.md"
        if not p.exists():
            continue
        chunk = knowledge._read_chunk(p)
        if chunk is not None and knowledge._is_stub(chunk):
            return t
    return None


def test_load_returns_house_view_active_themes_always():
    out = knowledge.load_for_report("daily_wrap", tickers=[])
    assert any("active_themes.md" in sid for sid in out), out.keys()


def test_load_returns_client_language_for_weekly_prep():
    # 2026-08-18: daily_morning drops client_language to fit Groq's 8K TPM cap.
    # weekly_prep still loads it since that flow has multi-call TPM headroom.
    out = knowledge.load_for_report("weekly_prep", tickers=[])
    assert any("client_language.md" in sid for sid in out)


def test_load_omits_client_language_for_daily_morning():
    out = knowledge.load_for_report("daily_morning", tickers=[])
    assert not any("client_language.md" in sid for sid in out)


def test_load_omits_client_language_for_wrap():
    out = knowledge.load_for_report("daily_wrap", tickers=[])
    assert not any("client_language.md" in sid for sid in out)


def test_load_skips_stub_ticker_facts():
    """Stub-scaffold ticker facts are correctly skipped by load_for_report to
    conserve LLM tokens. §E.19 presence check uses verify_blue_chip_coverage
    (file existence), not load_for_report (content quality)."""
    ticker = _find_stub_ticker()
    if ticker is None:
        pytest.skip("no stub ticker files remain — every blue-chip is populated")
    out = knowledge.load_for_report("daily_morning", tickers=[ticker])
    assert not any(f"blue_chip/{ticker}_facts.md" in sid for sid in out), (
        "stub ticker fact leaked into LLM context — over-eager to conserve tokens? "
        "Verify stub-detection heuristic in knowledge._is_stub"
    )
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
