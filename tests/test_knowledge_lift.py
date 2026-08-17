"""knowledge_source_lift scaffold — §D.7 promised correlation query.

Enables weekly_lookback KNOWLEDGE LIBRARY REPORT block when n≥20 pitches with
knowledge_sources_used exist (per §D.1.c bootstrap gate). This test proves the
aggregation math; the render integration will land when the data threshold hits.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src import accuracy, db


@pytest.fixture
def seeded_db(tmp_path, monkeypatch):
    p = tmp_path / "lift.db"
    monkeypatch.setattr("src.config.DB_PATH", p)
    db.init_db(p)
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with db.connect(p) as conn:
        # 6 pitches citing knowledge/x.md: 4 played out, 1 failed, 1 open
        # 4 pitches citing knowledge/y.md: 1 played out, 3 failed  → weak source
        # 3 pitches citing knowledge/rare.md → below min_n=5, excluded
        specs = [
            ("knowledge/x.md", "thesis_played_out"),
            ("knowledge/x.md", "thesis_played_out"),
            ("knowledge/x.md", "thesis_played_out"),
            ("knowledge/x.md", "thesis_played_out"),
            ("knowledge/x.md", "thesis_failed"),
            ("knowledge/x.md", None),
            ("knowledge/y.md", "thesis_played_out"),
            ("knowledge/y.md", "thesis_failed"),
            ("knowledge/y.md", "thesis_failed"),
            ("knowledge/y.md", "thesis_failed"),
            ("knowledge/y.md", "thesis_failed"),
            ("knowledge/rare.md", "thesis_played_out"),
            ("knowledge/rare.md", None),
            ("knowledge/rare.md", None),
        ]
        for src_id, res in specs:
            conn.execute(
                """INSERT INTO pitches (generated_at, report_date, asset_symbol, asset_class,
                   direction, thesis, key_factors_json, star_rating, rubric_breakdown_json,
                   knowledge_sources_used, resolution)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (now, "2026-08-18", "AAPL", "equity_bluechip", "long", "t",
                 "[]", 3, "{}", "[]", res),
            )
            pid = conn.execute("SELECT last_insert_rowid() AS i").fetchone()["i"]
            conn.execute(
                "INSERT INTO knowledge_hits (used_at, report_type, source_id, pitch_id) VALUES (?,?,?,?)",
                (now, "daily_morning", src_id, pid),
            )
    return p


def test_lift_excludes_small_samples(seeded_db):
    rows = accuracy.knowledge_source_lift(min_n=5)
    ids = {r["source_id"] for r in rows}
    assert "knowledge/x.md" in ids
    assert "knowledge/y.md" in ids
    assert "knowledge/rare.md" not in ids


def test_lift_computes_played_out_pct(seeded_db):
    rows = {r["source_id"]: r for r in accuracy.knowledge_source_lift(min_n=5)}
    # x: 4 played_out + 1 failed = 5 resolved, 4/5 = 0.8
    assert rows["knowledge/x.md"]["played_out_pct"] == pytest.approx(0.8)
    # y: 1 played + 4 failed = 5 resolved, 1/5 = 0.2 → prune candidate
    assert rows["knowledge/y.md"]["played_out_pct"] == pytest.approx(0.2)


def test_lift_orders_by_n_desc(seeded_db):
    rows = accuracy.knowledge_source_lift(min_n=1)
    counts = [(r["source_id"], r["n_pitches"] + r["n_trades"]) for r in rows]
    assert counts == sorted(counts, key=lambda x: x[1], reverse=True)
