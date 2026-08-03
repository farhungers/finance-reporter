"""Verbatim-copy detector — §D.7 says the LLM must transform and apply knowledge
chunks, never paste text verbatim. Enforcement was prompt-only until 2026-08-03;
now backed by src.knowledge.verbatim_hits() as a run-time drift signal."""
from src.knowledge import verbatim_hits


def test_clean_thesis_no_hits():
    chunks = {
        "knowledge/macro/regime.md": (
            "Post-CPI drift typically favors risk assets when the surprise "
            "is dovish and the DXY responds with a sharp sell-off within an hour."
        ),
    }
    thesis = (
        "Apple looks set up for a modest bid on Wednesday's tape as inflation "
        "cools and the dollar softens into the earnings print."
    )
    assert verbatim_hits(thesis, chunks) == []


def test_verbatim_paste_is_detected():
    chunks = {
        "knowledge/macro/regime.md": (
            "Post-CPI drift typically favors risk assets when the surprise is dovish "
            "and the DXY responds with a sharp sell-off within an hour."
        ),
    }
    # The pasted phrase must be at least 8 consecutive alnum tokens.
    thesis = (
        "We like this setup because post-CPI drift typically favors risk assets "
        "when the surprise is dovish and today's print matches."
    )
    hits = verbatim_hits(thesis, chunks)
    assert hits, "expected verbatim overlap to be flagged"
    assert any(sid == "knowledge/macro/regime.md" for sid, _ in hits)


def test_punctuation_and_case_do_not_hide_overlap():
    chunks = {
        "knowledge/macro/regime.md": (
            "the pendulum swings between greed and fear across long cycles"
        ),
    }
    # Same 8+ tokens, different case and punctuation
    thesis = (
        "As Marks writes, The Pendulum SWINGS between GREED and Fear ACROSS "
        "long cycles — timing this is the game."
    )
    hits = verbatim_hits(thesis, chunks)
    assert hits, "case+punctuation should not hide a verbatim paste"


def test_short_common_phrase_not_flagged():
    chunks = {
        "knowledge/macro/regime.md": "the primary risk is a hawkish surprise",
    }
    # 7 tokens — below the 8-token window, should not trip
    thesis = "the primary risk is a hawkish surprise from the Fed later this week"
    # This IS 8 tokens: "the primary risk is a hawkish surprise from" — will
    # trip. So use a genuinely short one:
    thesis_short = "the primary risk is a hawkish surprise"
    assert verbatim_hits(thesis_short, chunks) == []


def test_empty_inputs():
    assert verbatim_hits("", {"knowledge/foo.md": "some content here about markets"}) == []
    assert verbatim_hits("some text here about the markets today", {}) == []
