"""MarkdownV2 escape regression — CLAUDE.md §C7 / §E.1.

Every dynamic string interpolated into a Telegram body MUST pass through esc().
This test enforces the character set.
"""
from src.telegram_send import esc


ALL_RESERVED = "_*[]()~`>#+-=|{}.!\\"


def test_all_reserved_chars_escaped():
    for c in ALL_RESERVED:
        result = esc(c)
        assert result == "\\" + c, f"char {c!r} escaped as {result!r}"


def test_mixed_string():
    src = "Hello *world*! [link](url) 3.14 = pi"
    out = esc(src)
    # Every reserved must be backslash-prefixed
    for c in ALL_RESERVED:
        # brute check: count of literal c should equal count of backslash+c
        if c in src:
            assert f"\\{c}" in out, f"{c!r} not escaped in output {out!r}"


def test_none_returns_empty():
    assert esc(None) == ""


def test_plain_ascii_unchanged():
    assert esc("HelloWorld123") == "HelloWorld123"


def test_double_escape_is_safe_to_detect():
    # We do NOT re-escape backslashes we already added, but escaping a raw
    # backslash char in user data adds one. Ensure a bare backslash in input escapes:
    assert "\\\\" in esc("a\\b")


def test_ticker_symbols_survive():
    # BRK-B has a hyphen (reserved). Ensure it escapes properly.
    out = esc("BRK-B")
    assert out == "BRK\\-B"


# --- token-in-error defense (2026-09-16) --------------------------------

def test_redact_strips_bot_token_from_url():
    """The requests library dumps the sendMessage URL — including the token —
    into HTTPError messages. _redact() must strip it before we log."""
    from src.telegram_send import _redact
    leaky = (
        "400 Client Error: Bad Request for url: "
        "https://api.telegram.org/bot8912663833:AAFeSka_c3NayDsU1XP597-fhezvxJty3dc/sendMessage"
    )
    out = _redact(leaky)
    assert "8912663833:AAFeSka_c3NayDsU1XP597-fhezvxJty3dc" not in out
    assert "<REDACTED_TOKEN>" in out
    # Rest of the diagnostic string survives so operator can still triage
    assert "400" in out
    assert "Bad Request" in out


def test_redact_handles_standalone_token():
    from src.telegram_send import _redact
    out = _redact("token=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk")
    assert "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk" not in out
    assert "<REDACTED_TOKEN>" in out


def test_redact_leaves_normal_text_alone():
    from src.telegram_send import _redact
    assert _redact("nothing to redact here") == "nothing to redact here"
    assert _redact("") == ""
    assert _redact(None) is None


def test_redact_does_not_match_plain_numbers():
    """Regression guard: 6-digit chat IDs and other numeric IDs must NOT
    match the token pattern (they lack the ':<url-safe-string>' tail)."""
    from src.telegram_send import _redact
    out = _redact("chat_id=123456789 posted at 2026-09-16T19:24:27Z")
    assert "chat_id=123456789" in out
    assert "REDACTED" not in out
