"""SQLite schema v1 — LOCKED per CLAUDE.md §B.5.

Schema is additive-only after v1. New columns must be nullable. Historical rows
are immutable except for resolver writes to the resolution/realized_* fields
(these are the append-once fields; a resolved row is never re-resolved).
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from src import config

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pitches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  generated_at TEXT NOT NULL,               -- ISO UTC
  report_date TEXT NOT NULL,                -- YYYY-MM-DD (IST)
  asset_symbol TEXT NOT NULL,
  asset_class TEXT NOT NULL,                -- 'equity_bluechip'
  direction TEXT NOT NULL,                  -- 'long' / 'short' / 'neutral'
  thesis TEXT NOT NULL,
  key_factors_json TEXT NOT NULL,
  rough_entry_hint TEXT,
  star_rating INTEGER NOT NULL CHECK(star_rating BETWEEN 0 AND 5),
  rubric_breakdown_json TEXT NOT NULL,
  low_star_warning TEXT,
  earnings_within_3d INTEGER DEFAULT 0,
  knowledge_sources_used TEXT,
  horizon_days INTEGER,
  resolved_at TEXT,
  resolution TEXT,
  realized_pct REAL
);

CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  generated_at TEXT NOT NULL,
  report_date TEXT NOT NULL,
  asset_symbol TEXT NOT NULL,
  asset_class TEXT NOT NULL,                -- 'commodity' / 'equity' / 'crypto'
  direction TEXT NOT NULL,
  entry REAL NOT NULL,
  tp REAL NOT NULL,
  sl REAL NOT NULL,
  one_line_reasoning TEXT NOT NULL,
  star_rating INTEGER NOT NULL CHECK(star_rating BETWEEN 0 AND 5),
  rubric_breakdown_json TEXT NOT NULL,
  low_star_warning TEXT,
  knowledge_sources_used TEXT,
  resolved_at TEXT,
  resolution TEXT,
  realized_r REAL
);

CREATE TABLE IF NOT EXISTS calendar_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fetched_at TEXT NOT NULL,
  event_date TEXT NOT NULL,                 -- YYYY-MM-DD (IST)
  event_time_ist TEXT,                      -- HH:MM
  country TEXT NOT NULL,
  event_name TEXT NOT NULL,
  importance INTEGER NOT NULL,              -- 1/2/3 stars
  forecast TEXT,
  previous TEXT,
  actual TEXT,
  source TEXT NOT NULL                      -- 'forexfactory' / 'tradingeconomics'
);

CREATE TABLE IF NOT EXISTS report_sends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  report_type TEXT NOT NULL,
  sent_at TEXT NOT NULL,
  telegram_message_id INTEGER,              -- NULL if send failed OR dry-run
  char_count INTEGER,
  read_minutes_estimate REAL,
  kill_switch_state TEXT NOT NULL,
  dry_run INTEGER NOT NULL,
  llm_provider TEXT,
  llm_tokens_in INTEGER,
  llm_tokens_out INTEGER
);

CREATE TABLE IF NOT EXISTS knowledge_hits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  used_at TEXT NOT NULL,
  report_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  pitch_id INTEGER,
  trade_id INTEGER
);

-- Session 3 hook (schema exists v1; consumers NOT built until Session 3 unlock)
CREATE TABLE IF NOT EXISTS feedback_reactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  received_at TEXT NOT NULL,
  telegram_message_id INTEGER NOT NULL,
  pitch_id INTEGER,
  trade_id INTEGER,
  emoji TEXT NOT NULL,
  note TEXT
);

CREATE INDEX IF NOT EXISTS idx_pitches_resolved ON pitches(resolution);
CREATE INDEX IF NOT EXISTS idx_trades_resolved ON trades(resolution);
CREATE INDEX IF NOT EXISTS idx_calendar_date ON calendar_events(event_date);
CREATE INDEX IF NOT EXISTS idx_report_sends_type_date ON report_sends(report_type, sent_at);
"""


def init_db(path=None) -> None:
    """Create tables + indices if missing. Idempotent."""
    p = str(path or config.DB_PATH)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


@contextmanager
def connect(path=None) -> Iterator[sqlite3.Connection]:
    """Context manager for a read/write connection. Row factory = sqlite3.Row."""
    p = str(path or config.DB_PATH)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
