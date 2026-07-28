"""Knowledge library loader with provenance tagging (CLAUDE.md §D.7, §E.19, §E.20).

Every chunk enters the LLM context with a source_id. The LLM's structured output
MUST include knowledge_sources_used: [source_id, ...] which is written to
pitches/trades tables AND to knowledge_hits.

LLM MUST NOT paste knowledge text verbatim — must transform/apply. This is
enforced by prompt discipline, not code.

Mandatory file rule (§E.19): every ticker in market_data.BLUE_CHIP_UNIVERSE MUST
have a knowledge/blue_chip/{ticker}_facts.md file. Pilot fails hard if missing.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src import config

# Matches a stub marker anywhere in a line (raw or preceded by list bullets etc.)
_STUB_RE = re.compile(r"\(stub\b", re.IGNORECASE)

log = logging.getLogger(__name__)

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass(frozen=True)
class KnowledgeChunk:
    source_id: str          # 'knowledge/{path}#{section_anchor}' or 'knowledge/{path}' for whole-file
    path: Path
    frontmatter: dict[str, object]
    body: str               # section body (or full body if no anchor)


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = m.group(2)
    fm: dict[str, object] = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        # crude list parse: [a, b, c]
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1]
            fm[k.strip()] = [s.strip() for s in inner.split(",") if s.strip()]
        else:
            fm[k.strip()] = v.strip('"').strip("'")
    return fm, body


def _read_chunk(path: Path) -> Optional[KnowledgeChunk]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as e:
        log.warning("knowledge read failed %s: %s", path, e)
        return None
    fm, body = _parse_frontmatter(raw)
    rel = path.relative_to(config.KNOWLEDGE_DIR).as_posix()
    source_id = f"knowledge/{rel}"
    return KnowledgeChunk(source_id=source_id, path=path, frontmatter=fm, body=body.strip())


def _is_stub(chunk: KnowledgeChunk) -> bool:
    """Skip stub files at LLM-context assembly time — they cost tokens without
    providing signal. Detection is by frontmatter `provenance: "stub..."` OR
    by body-content ratio (if >70% of non-header lines are '(stub ...' markers).

    Presence check (§E.19 blue-chip coverage) still uses file existence, not this."""
    # Only treat scaffold-generated stubs as stubs, not any file whose provenance
    # happens to start with "stub". Real content files like client_language.md
    # can have "stub —" provenance while still being fully populated.
    prov = chunk.frontmatter.get("provenance", "")
    if isinstance(prov, str) and prov.lower().startswith("stub scaffold"):
        return True
    lines = [l.strip() for l in chunk.body.splitlines() if l.strip()]
    content_lines = [l for l in lines if not l.startswith("#")]
    if not content_lines:
        return True
    # Match "(stub" anywhere in the line (handles "- (stub) ..." bullets etc.)
    stub_lines = sum(1 for l in content_lines if _STUB_RE.search(l))
    return stub_lines / len(content_lines) > 0.6


def load_for_report(report_type: str, tickers: list[str] | None = None) -> dict[str, str]:
    """Return {source_id: chunk_body_markdown} for the given report + tickers.

    Selection rule:
      - Any file where frontmatter `applies_to_reports` includes report_type
      - Plus every knowledge/blue_chip/{TICKER}_facts.md for tickers in `tickers`
      - Plus knowledge/house_view/active_themes.md (always)
      - Plus knowledge/house_view/client_language.md (for pitch-generating reports)
    """
    tickers = tickers or []
    out: dict[str, str] = {}

    if not config.KNOWLEDGE_DIR.exists():
        log.warning("knowledge dir missing: %s", config.KNOWLEDGE_DIR)
        return out

    # Whole-tree scan for applies_to_reports match (skip stubs to conserve tokens)
    for md in config.KNOWLEDGE_DIR.rglob("*.md"):
        chunk = _read_chunk(md)
        if chunk is None or _is_stub(chunk):
            continue
        applies = chunk.frontmatter.get("applies_to_reports", [])
        if isinstance(applies, list) and report_type in applies:
            out[chunk.source_id] = chunk.body

    # Blue-chip facts for pitched tickers (skip stubs)
    for ticker in tickers:
        p = config.KNOWLEDGE_DIR / "blue_chip" / f"{ticker}_facts.md"
        chunk = _read_chunk(p) if p.exists() else None
        if chunk and chunk.body and not _is_stub(chunk):
            out[chunk.source_id] = chunk.body

    # Always: active themes (if populated)
    p = config.KNOWLEDGE_DIR / "house_view" / "active_themes.md"
    if p.exists():
        c = _read_chunk(p)
        if c and c.body and not _is_stub(c):
            out[c.source_id] = c.body

    # For pitch-generating reports: client language (real content, not stub)
    if report_type in {"daily_morning", "weekly_prep"}:
        p = config.KNOWLEDGE_DIR / "house_view" / "client_language.md"
        if p.exists():
            c = _read_chunk(p)
            if c and c.body and not _is_stub(c):
                out[c.source_id] = c.body

    return out


def verify_blue_chip_coverage(universe: tuple[str, ...]) -> tuple[list[str], list[str]]:
    """Verify §E.19: every ticker has a knowledge/blue_chip/{ticker}_facts.md file.
    Returns (present, missing)."""
    present: list[str] = []
    missing: list[str] = []
    for t in universe:
        p = config.KNOWLEDGE_DIR / "blue_chip" / f"{t}_facts.md"
        if p.exists():
            present.append(t)
        else:
            missing.append(t)
    return present, missing


def build_context_block(chunks: dict[str, str]) -> str:
    """Render loaded chunks into an LLM context string. Each chunk is preceded by
    its source_id tag so the LLM can cite it in knowledge_sources_used."""
    if not chunks:
        return "[No knowledge library chunks loaded for this report.]"
    parts: list[str] = ["=== KNOWLEDGE LIBRARY (cite by source_id in knowledge_sources_used) ==="]
    for sid, body in chunks.items():
        parts.append(f"\n--- {sid} ---\n{body}")
    parts.append("\n=== END KNOWLEDGE LIBRARY ===")
    return "\n".join(parts)
