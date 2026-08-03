"""Weekly look-back — §E.25 bootstrap discipline:
during first 4 weeks OR while every star bucket has n<5, the report must
show raw counts only, NOT percentage tables. Fake precision on tiny n is worse
than honest raw counts.
"""
import sqlite3
from datetime import UTC, datetime

import pytest

from src import config, db
from src.accuracy import Stats
from src.reports import weekly_lookback


def _reset_db(tmp_path, monkeypatch):
    dbpath = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", dbpath)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    db.init_db(dbpath)
    return dbpath


def _insert_pitch(cur, star: int, resolution: str, ticker: str = "AAPL"):
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur.execute(
        """INSERT INTO pitches
        (generated_at, report_date, asset_symbol, asset_class, direction, thesis,
         key_factors_json, rough_entry_hint, star_rating, rubric_breakdown_json,
         low_star_warning, earnings_within_3d, knowledge_sources_used, horizon_days,
         resolution)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            now, "2026-08-01", ticker, "equity_bluechip", "long", "test thesis",
            "[]", None, star, "{}", None, 0, "[]", 7, resolution,
        ),
    )


def test_bootstrap_star_rows_are_raw_counts_not_percentages(tmp_path, monkeypatch):
    """When bucket_max_n < 5, star rows must show 'k=v' style, not 'played=X%'."""
    _reset_db(tmp_path, monkeypatch)
    with db.connect() as conn:
        cur = conn.cursor()
        # 4 pitches at 5★ — under the n<5 threshold per bucket
        for _ in range(4):
            _insert_pitch(cur, 5, "still_open")

    from src import accuracy
    s = accuracy.stats_snapshot()
    assert s.pitches_by_star[5]["still_open"] == 4

    rows = weekly_lookback._pitch_star_rows(s, bootstrap=True)
    joined = "\n".join(rows)
    assert "still_open=4" in joined, "bootstrap should list raw resolution counts"
    assert "%" not in joined, "bootstrap mode must not show percentage columns"
    assert "played=" not in joined, "bootstrap mode must not compute played percentage"


def test_post_bootstrap_shows_percentages(tmp_path, monkeypatch):
    """When enough data lands, mode switches to percentage view."""
    _reset_db(tmp_path, monkeypatch)
    with db.connect() as conn:
        cur = conn.cursor()
        # 5 pitches at 4★, 3 played out, 1 failed, 1 still open
        for _ in range(3):
            _insert_pitch(cur, 4, "thesis_played_out")
        _insert_pitch(cur, 4, "thesis_failed")
        _insert_pitch(cur, 4, "still_open")

    from src import accuracy
    s = accuracy.stats_snapshot()
    rows = weekly_lookback._pitch_star_rows(s, bootstrap=False)
    joined = "\n".join(rows)
    assert "played=" in joined, "post-bootstrap should show played=X%"
    assert "%" in joined


def test_bootstrap_header_appears_in_report_when_low_n(tmp_path, monkeypatch):
    """The generate() path prints the 'Bootstrap week N of 4' header when applicable."""
    _reset_db(tmp_path, monkeypatch)
    with db.connect() as conn:
        cur = conn.cursor()
        _insert_pitch(cur, 3, "still_open")
    # Deep-stub the sub-collectors we don't exercise here to avoid touching
    # network/DB paths in ways this test isn't about
    monkeypatch.setattr(weekly_lookback.accuracy, "resolve_open_positions", lambda as_of=None: (0, 0))
    body, _ = weekly_lookback.generate()
    assert "Bootstrap week" in body
    # Percentages must NOT appear in the star table when we're in bootstrap
    assert "played=" not in body
