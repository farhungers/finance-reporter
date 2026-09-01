"""Knowledge trim guard — CLAUDE.md §D.7, §C9.

Regression coverage for the 2026-09-01 fix: Groq's 8K TPM ceiling was breached
(prompt 8681 vs 8000 cap) when the pitch prompt loaded macro playbook + ticker
facts + active themes on a day of prompt drift. The trim guard drops the
largest chunks first until under `budget_chars`. Ticker facts + small chunks
are preserved by construction (they're smaller than the macro playbook).
"""
from src.pitches import _trim_knowledge_to_budget


def test_trim_noop_when_under_budget():
    chunks = {"a": "x" * 500, "b": "y" * 500}
    out = _trim_knowledge_to_budget(chunks, budget_chars=2000)
    assert out == chunks


def test_trim_drops_largest_first():
    chunks = {
        "small": "s" * 100,
        "huge": "h" * 10000,
        "medium": "m" * 500,
    }
    out = _trim_knowledge_to_budget(chunks, budget_chars=1000)
    # huge must be dropped; small + medium fit
    assert "huge" not in out
    assert "small" in out
    assert "medium" in out


def test_trim_drops_multiple_until_fit():
    chunks = {
        "big1": "a" * 5000,
        "big2": "b" * 5000,
        "small": "c" * 200,
    }
    out = _trim_knowledge_to_budget(chunks, budget_chars=1000)
    # Both bigs dropped; only small remains
    assert "big1" not in out
    assert "big2" not in out
    assert "small" in out


def test_trim_returns_empty_when_all_too_large():
    chunks = {"huge1": "x" * 10000, "huge2": "y" * 10000}
    out = _trim_knowledge_to_budget(chunks, budget_chars=500)
    assert out == {}


def test_trim_preserves_chunk_bodies():
    """Bodies must be returned verbatim, not truncated — we drop whole chunks
    (preserving source_id provenance) rather than mid-chunk cuts."""
    chunks = {"kept": "content here", "dropped": "x" * 5000}
    out = _trim_knowledge_to_budget(chunks, budget_chars=100)
    assert out.get("kept") == "content here"
