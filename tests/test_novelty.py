"""Novelty check — CLAUDE.md §C11 (no gap), §D.7 (transform not paste).

2026-08-31: LLM reasoning templates repeated verbatim across days. Jaccard on
≥3-char token bags detects the mechanism-level duplication that verbatim-hits
(from knowledge module) misses when the LLM paraphrases lightly."""
from src.novelty import most_similar, similarity, snippets


def test_identical_strings_are_1_0():
    s = "Long BTC on breakout retest of 200-day MA, riding Fed rate-cut path"
    assert similarity(s, s) == 1.0


def test_disjoint_strings_are_0():
    a = "Long gold on real yields falling into CPI"
    b = "Short crude on OPEC cheating and dollar strength"
    assert similarity(a, b) < 0.15  # nearly disjoint after stopword removal


def test_near_duplicate_flagged_at_60_pct():
    """The exact pathology: two BTC reasonings with different tickers but same mechanism."""
    r1 = "Long BTC on breakout retest of 200-day MA, riding Fed rate-cut path"
    r2 = "Long AMD on breakout retest of 200-day MA, riding Fed rate-cut path"
    j = similarity(r1, r2)
    assert j >= 0.6, f"expected near-duplicate flagged, got Jaccard={j:.2f}"


def test_stopwords_dont_inflate():
    """Two disjoint theses padded with common words should still score low."""
    a = "Long trade near support level with entry over target"
    b = "Short trade near resistance level with entry over target"
    j = similarity(a, b)
    # Almost all shared tokens are stopwords; the only real difference is
    # long/short and support/resistance — both filtered or unique.
    assert j < 0.5


def test_most_similar_returns_best_match():
    new = "Long BTC on breakout retest of 200-day MA, riding Fed rate-cut"
    baselines = [
        "Short crude on OPEC cheating",
        "Long AMD on breakout retest of 200-day MA, riding Fed rate-cut",  # near-dup
        "Gold mean reversion into CPI",
    ]
    sim, match = most_similar(new, baselines)
    assert sim >= 0.6
    assert "AMD" in match


def test_most_similar_empty_baselines():
    assert most_similar("anything", []) == (0.0, "")


def test_similarity_empty_strings():
    assert similarity("", "") == 0.0
    assert similarity("", "hello world") == 0.0


def test_snippets_trims_to_word_cap():
    rows = ["one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"]
    out = snippets(rows, max_words=5, cap=3)
    assert len(out) == 1
    # 5 words + ellipsis
    assert out[0].endswith("…")
    assert out[0].split("…")[0].split() == ["one", "two", "three", "four", "five"]


def test_snippets_caps_row_count():
    rows = ["a", "b", "c", "d", "e"]
    out = snippets(rows, max_words=15, cap=3)
    assert out == ["a", "b", "c"]


def test_snippets_handles_short_rows_unchanged():
    rows = ["short line"]
    out = snippets(rows, max_words=15, cap=3)
    assert out == ["short line"]
