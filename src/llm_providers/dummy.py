"""Dummy LLM provider — canned schema-conforming outputs.

Used ONLY for pilot dry-runs and tests when API keys are not yet set. Never for
production. Selected via LLM_PROVIDER=dummy.

Outputs are structural placeholders. They exercise the render + escape + persist
paths so the pilot can prove the pipeline works before a real LLM call is made.
"""
from __future__ import annotations

from typing import Any

from src.llm_providers.base import GenerateResult, Provider


class DummyProvider(Provider):
    name = "dummy"

    def __init__(self, api_key: str = ""):
        pass

    def generate(
        self,
        system: str,
        user: str,
        response_schema: dict[str, Any],
    ) -> GenerateResult:
        # Route by schema shape — we key off top-level required keys.
        req = set(response_schema.get("required", []))
        parsed: dict[str, Any] = {}

        if "pitches" in req:
            parsed = _dummy_pitches()
        elif {"commodity", "equity", "crypto"} <= req:
            parsed = _dummy_trades()
        elif "one_line_summary" in req:
            parsed = _dummy_wrap()
        elif "macro_setup_bullets" in req:
            parsed = _dummy_prep()
        else:
            parsed = {}

        return GenerateResult(
            parsed=parsed,
            tokens_in=0,
            tokens_out=0,
            raw_text=str(parsed),
            provider=self.name,
        )


def _dummy_pitches() -> dict:
    """2 blue-chip pitches (updated 2026-07-28: was 3, reduced to 2 per operator).
    Client-ready thesis prose — plain English, named catalyst, named risk.
    Key factors are short jargon-free bullets."""
    return {
        "pitches": [
            {
                "asset_symbol": "AAPL",
                "direction": "long",
                "thesis": (
                    "Apple reports earnings on July 30, and the setup is unusually clean. "
                    "The Street already reset expectations lower after the May guidance cut, "
                    "so the bar going in is easy to clear. Positioning data shows funds have "
                    "trimmed exposure, meaning any modest beat brings buyers back in size. "
                    "We're playing an asymmetric risk-reward — limited downside on a miss "
                    "because expectations are already low, meaningful upside on any positive surprise."
                ),
                "key_factors": [
                    "Earnings July 30 — Street already reset expectations lower",
                    "Fund positioning is light, leaving room for buyers to return",
                    "Trading 12% cheaper than its 5-year average P/E",
                    "iPhone 17 product cycle mix favors the second half",
                ],
                "rough_entry_hint": "near $335 prior-swing support",
                "rubric": {
                    "macro_alignment": True,
                    "technical_setup": True,
                    "catalyst_proximity": True,
                    "base_rate_support": True,
                    "risk_reward": True,
                },
                "knowledge_sources_used": [
                    "knowledge/blue_chip/AAPL_facts.md",
                    "knowledge/house_view/client_language.md",
                ],
                "horizon_days": 7,
                "earnings_direction_expectation": "bullish",
            },
            {
                "asset_symbol": "XOM",
                "direction": "short",
                "thesis": (
                    "Oil has broken a key technical level at $80, and OPEC+ came out of "
                    "their July meeting with looser production discipline than the market "
                    "expected. Exxon's refining margins have already peaked, but Street "
                    "estimates for 2026 still assume those margins hold — that gap will close "
                    "as analysts revise lower. This is a positioning trade around a real "
                    "estimate cut, not a call on the oil price itself."
                ),
                "key_factors": [
                    "Oil broke below $80 — key technical support gone",
                    "OPEC+ loosened production discipline in July",
                    "Refining margins have peaked; Street hasn't caught up yet",
                    "Consensus 2026 numbers still assume elevated margins",
                ],
                "rough_entry_hint": "on bounce to 20-day moving average, around $118",
                "rubric": {
                    "macro_alignment": True,
                    "technical_setup": True,
                    "catalyst_proximity": False,
                    "base_rate_support": True,
                    "risk_reward": True,
                },
                "knowledge_sources_used": [
                    "knowledge/blue_chip/XOM_facts.md",
                    "knowledge/sectors/energy.md",
                ],
                "horizon_days": 10,
            },
        ]
    }


def _dummy_trades() -> dict:
    return {
        "commodity": {
            "asset_symbol": "GOLD",
            "direction": "long",
            "entry": 4045.0,
            "tp": 4120.0,
            "sl": 4008.0,
            "one_line_reasoning": "Retest of prior breakout level with DXY rolling off recent highs supports bounce-off-support entry.",
            "rubric": {
                "macro_alignment": True,
                "technical_setup": True,
                "catalyst_proximity": False,
                "base_rate_support": True,
                "risk_reward": True,
            },
            "knowledge_sources_used": ["knowledge/correlations/dxy_gold.md"],
        },
        "equity": {
            "asset_symbol": "SPY",
            "direction": "long",
            "entry": 742.0,
            "tp": 754.5,
            "sl": 736.0,
            "one_line_reasoning": "VIX rolled off 20; bid returning after 3-day pullback tests 20-EMA support.",
            "rubric": {
                "macro_alignment": True,
                "technical_setup": True,
                "catalyst_proximity": False,
                "base_rate_support": True,
                "risk_reward": True,
            },
            "knowledge_sources_used": ["knowledge/correlations/vix_spx.md"],
        },
        "crypto": {
            "asset_symbol": "BTC",
            "direction": "long",
            "entry": 63700.0,
            "tp": 66200.0,
            "sl": 62900.0,
            "one_line_reasoning": "Consolidation at prior breakout retest — no macro catalyst, purely tape/structure.",
            "rubric": {
                "macro_alignment": False,
                "technical_setup": True,
                "catalyst_proximity": False,
                "base_rate_support": False,
                "risk_reward": False,
            },
            "low_star_warning": "Chart-only setup with weak R/R and no macro tailwind; shipping to keep class slot filled — trader may skip.",
            "knowledge_sources_used": [],
        },
    }


def _dummy_wrap() -> dict:
    return {
        "one_line_summary": "US indices flat with mega-cap tech underperformance offset by defensives; oil down 3% on OPEC+ commentary.",
        "notable_items": [
            "AAPL down 1.2% ahead of earnings tomorrow despite index green tape",
            "Copper unchanged despite CNY strength — decoupling worth watching",
            "VIX slipped below 18 for first time in three sessions",
        ],
    }


def _dummy_prep() -> dict:
    return {
        "macro_setup_bullets": [
            "Week's dominant read: FOMC decision midweek — expect wider intraday range around statement + presser.",
            "Rates: 10Y at 4.59% mid-range of 6-week band; further move contingent on FOMC guidance.",
            "USD: DXY consolidating; two-way risk into decision.",
            "Earnings megacap week — AAPL, MSFT, META all report; index sensitivity elevated.",
        ],
        "sector_theme_bullets": [
            "Energy: OPEC+ compliance loosening + crack spreads rolling over — headwind persists through week.",
            "Tech: earnings-driven dispersion likely; mega-cap AI capex commentary the key tell.",
            "Financials: NIM commentary sensitive to any Fed guidance shift toward faster cuts.",
        ],
        "knowledge_sources_used": [
            "knowledge/macro/fomc_playbook.md",
            "knowledge/sectors/energy.md",
            "knowledge/sectors/tech.md",
            "knowledge/sectors/financials.md",
        ],
    }
