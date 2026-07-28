"""Knowledge coverage — CLAUDE.md §E.19. Every blue-chip ticker MUST have a facts file."""
from src import knowledge
from src.market_data import BLUE_CHIP_UNIVERSE


def test_every_bluechip_ticker_has_facts_file():
    present, missing = knowledge.verify_blue_chip_coverage(BLUE_CHIP_UNIVERSE)
    assert missing == [], f"missing facts files for tickers: {missing}"
    assert len(present) == len(BLUE_CHIP_UNIVERSE)
