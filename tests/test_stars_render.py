"""Star visual convention — CLAUDE.md §C14 / §E.17. Byte-exact regression."""
import pytest

from src.stars import render


def test_zero_stars():
    assert render(0) == "\u2606\u2606\u2606\u2606\u2606"


def test_one_star():
    assert render(1) == "\u2b50" + "\u2606" * 4


def test_two_stars():
    assert render(2) == "\u2b50\u2b50\u2606\u2606\u2606"


def test_three_stars():
    assert render(3) == "\u2b50\u2b50\u2b50\u2606\u2606"


def test_four_stars():
    assert render(4) == "\u2b50\u2b50\u2b50\u2b50\u2606"


def test_five_stars_gold():
    # 5/5 is 🌟 gold, visually distinct — locked §C14 addendum
    assert render(5) == "\U0001f31f" * 5


def test_invalid_raises():
    with pytest.raises(ValueError):
        render(-1)
    with pytest.raises(ValueError):
        render(6)
