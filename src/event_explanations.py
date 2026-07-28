"""1-line explanations for common 3-star economic events (CLAUDE.md §D.1.a Part 1).

Each entry: "brief what the event is + why it moves markets", drawn from macro
playbook conventions. Match is case-insensitive substring / longest-match.

Missing an event? Add here first, then optionally deepen in knowledge/macro/*
when a full playbook is warranted. Not LLM-generated — this is stable reference
data, editable by operator.
"""
from __future__ import annotations

# Ordered by specificity — longer more-specific keys FIRST so they match before
# shorter generic ones. The matcher iterates this list in insertion order.
EVENT_MEANINGS: dict[str, str] = {
    # ---- US inflation ----
    "Core CPI m/m": "Fed's preferred stickiness gauge; MoM surprise is the primary rate + USD vector.",
    "Core CPI y/y": "Trend core inflation; second-order vs the MoM print.",
    "CPI m/m": "Headline inflation MoM — direct Fed input, moves rates + USD.",
    "CPI y/y": "Headline inflation YoY — trend measure; less MoM-sensitive.",
    "Trimmed Mean CPI m/m": "Fed's alternative sticky-price cut; smoothed vs core.",
    "Core PPI m/m": "Producer prices ex food/energy — CPI leading indicator ~1-2mo out.",
    "PPI m/m": "Producer prices — CPI leading indicator; supply-side inflation gauge.",
    "Core PCE Price Index m/m": "Fed's actual inflation target measure; monthly PCE surprise dominates its cousin CPI in FOMC decisions.",
    "PCE Price Index m/m": "Broader PCE inflation; less market-moving than core but same policy weight.",

    # ---- US labor ----
    "Non-Farm Employment Change": "US NFP jobs — headline + revisions + wage subcomponents drive rates and USD.",
    "Unemployment Rate": "US jobless rate; Sahm-rule proximity closely watched.",
    "Average Hourly Earnings m/m": "US wage growth — sticky-inflation signal for the Fed.",
    "ADP Non-Farm Employment Change": "Private-sector jobs proxy 2 days before NFP; weak leading signal, not a hedge.",
    "JOLTS Job Openings": "Fed watches for labor tightness; big moves affect terminal-rate pricing.",
    "Unemployment Claims": "Weekly initial claims; only large deltas move markets.",

    # ---- US Fed ----
    "Federal Funds Rate": "FOMC rate decision itself; statement + dots + presser is the day-long sequence.",
    "FOMC Statement": "Fed policy statement; forward-guidance edits move duration + risk assets.",
    "FOMC Press Conference": "Powell Q&A; often re-writes the message the statement began.",
    "FOMC Meeting Minutes": "3-week-old detail; occasionally recalibrates rate expectations at the margin.",
    "FOMC Economic Projections": "SEP + dot plot at Mar/Jun/Sep/Dec; the dot median revision is the read.",
    "Fed Chair Powell Speaks": "Any Powell speech is potentially market-moving; hawkish vs dovish lean is the read.",
    "Fed Chair Powell Testifies": "Congress testimony; Q&A can surface policy nuance beyond prepared remarks.",
    "Chair Powell Speaks": "Any Powell speech is potentially market-moving; hawkish vs dovish lean is the read.",

    # ---- US activity ----
    "Core Retail Sales m/m": "Retail sales ex autos — cleaner consumer-demand signal.",
    "Retail Sales m/m": "US consumer spending pulse — control group is the read.",
    "Advance GDP q/q": "First quarterly growth estimate; largest surprise vs later revisions.",
    "Prelim GDP q/q": "First quarterly growth estimate; largest surprise vs later revisions.",
    "GDP q/q": "Quarterly growth print vs consensus moves duration.",
    "ISM Manufacturing PMI": "US manufacturing pulse; 50 is the expansion/contraction line.",
    "ISM Services PMI": "US services pulse — larger economic share than manufacturing.",
    "S&P Global US Manufacturing PMI": "Alternative US mfg PMI; secondary to ISM.",
    "S&P Global US Services PMI": "Alternative US services PMI; secondary to ISM.",
    "CB Consumer Confidence": "Conference Board sentiment; big misses can move rates.",
    "Consumer Confidence": "Conference Board sentiment; big misses can move rates.",
    "Prelim UoM Consumer Sentiment": "Univ of Michigan preliminary sentiment + inflation expectations.",
    "Revised UoM Consumer Sentiment": "Final UoM sentiment; less market-moving than preliminary.",
    "Existing Home Sales": "Housing turnover — rate-sensitive indicator.",
    "New Home Sales": "New-build activity — housing cycle signal.",
    "Building Permits": "Forward-looking housing starts indicator.",
    "Durable Goods Orders m/m": "Big-ticket capex; ex-transport is the cleaner signal.",
    "Core Durable Goods Orders m/m": "Capex demand ex volatile aircraft — business investment pulse.",

    # ---- ECB / Europe ----
    "Main Refinancing Rate": "ECB policy rate decision.",
    "ECB Press Conference": "Lagarde Q&A after ECB decision; often more important than the rate itself.",
    "ECB Monetary Policy Statement": "ECB rate + guidance statement.",
    "German Ifo Business Climate": "Germany business sentiment; leads EUR + Bund moves.",
    "German ZEW Economic Sentiment": "Analyst sentiment on Germany; second-tier vs Ifo.",
    "German Prelim CPI m/m": "Largest Eurozone component; leads Eurozone flash CPI by ~1 day.",
    "German Flash Manufacturing PMI": "Germany mfg pulse — reads across as EU industrial temperature.",
    "Flash Manufacturing PMI": "Eurozone mfg PMI first estimate; drives EUR when significantly off consensus.",
    "Flash Services PMI": "Eurozone services PMI first estimate; larger sector share.",

    # ---- BOE / UK ----
    "Official Bank Rate": "Bank of England policy rate decision.",
    "MPC Official Bank Rate Votes": "BoE MPC vote split; changes in dissent count re-price cut odds.",
    "BOE Gov Bailey Speaks": "BoE chief; rate-path guidance moves GBP + gilts.",
    "MPC Meeting Minutes": "BoE minutes; dovish/hawkish edits at the margin.",
    "CPI y/y": "UK inflation YoY — feeds directly to BoE rate expectations.",

    # ---- BOJ / Japan ----
    "BOJ Policy Rate": "BOJ policy decision; JPY carry-trade sensitivity + global-duration knock-on.",
    "BOJ Outlook Report": "Quarterly BOJ forecasts; sets narrative for the next 3 months.",
    "Monetary Policy Statement": "Central bank policy statement (context-dependent by country).",
    "BOJ Press Conference": "Governor Q&A after policy decision; often decisive vs statement.",
    "BOJ Core CPI y/y": "BOJ's preferred inflation cut; policy input for JPY yield-curve control.",

    # ---- Australia ----
    "Cash Rate": "RBA policy rate decision.",
    "RBA Cash Rate": "RBA policy rate decision.",
    "RBA Rate Statement": "RBA guidance text alongside rate decision.",
    "RBA Gov Bullock Speaks": "RBA chief; rate-path signals move AUD + regional risk.",
    "RBA Press Conference": "RBA governor Q&A; secondary to statement.",

    # ---- Canada / Switzerland / NZ (lighter coverage) ----
    "Overnight Rate": "BoC policy rate decision.",
    "BOC Rate Statement": "Bank of Canada rate guidance.",
    "BOC Press Conference": "BoC governor Q&A after decision.",
    "SNB Policy Rate": "Swiss National Bank policy rate.",
    "SNB Press Conference": "SNB chair Q&A; often flags CHF intervention stance.",
    "Official Cash Rate": "RBNZ policy rate decision.",
    "RBNZ Rate Statement": "RBNZ guidance text.",

    # ---- China ----
    "Manufacturing PMI": "China official PMI — global growth read for commodities + EM.",
    "Caixin Manufacturing PMI": "Alternate private China PMI (biases smaller firms).",
    "GDP y/y": "China GDP; growth-forecast anchor for EM + commodities.",

    # ---- Political / geopolitical ----
    "President Trump Speaks": "US presidential remarks; potentially market-moving on trade / tariffs / Fed pressure.",
    "President Biden Speaks": "US presidential remarks; typically less market-moving than Fed but can matter on tariffs / policy.",
    "Bank Holiday": "Major exchange or bank closure — thinner liquidity in affected region.",
}


# Acronym expansions — displayed in parentheses next to the event name.
# Pattern: match if the acronym appears as a whole word in the event name.
ACRONYM_EXPANSIONS: dict[str, str] = {
    "CPI": "Consumer Price Index",
    "PPI": "Producer Price Index",
    "PCE": "Personal Consumption Expenditures",
    "GDP": "Gross Domestic Product",
    "NFP": "Non-Farm Payrolls",
    "PMI": "Purchasing Managers' Index",
    "ISM": "Institute for Supply Management",
    "FOMC": "Federal Open Market Committee",
    "ECB": "European Central Bank",
    "BOE": "Bank of England",
    "BOJ": "Bank of Japan",
    "BOC": "Bank of Canada",
    "SNB": "Swiss National Bank",
    "RBA": "Reserve Bank of Australia",
    "RBNZ": "Reserve Bank of New Zealand",
    "MPC": "Monetary Policy Committee",
    "JOLTS": "Job Openings and Labor Turnover Survey",
    "ADP": "Automatic Data Processing (private-sector jobs proxy)",
    "AHE": "Average Hourly Earnings",
    "SEP": "Summary of Economic Projections",
    "HPI": "House Price Index",
    "IPO": "Initial Public Offering",
    "UoM": "University of Michigan",
    "CB": "Conference Board",
    "Ifo": "Ifo Institute (German economic research)",
    "ZEW": "Centre for European Economic Research",
    "SPPI": "Services Producer Price Index",
    "BRC": "British Retail Consortium",
    "OPEC": "Organization of the Petroleum Exporting Countries",
    "DXY": "US Dollar Index",
    "VIX": "CBOE Volatility Index",
}


# Frequency shorthand → human phrase
FREQUENCY_EXPANSIONS: dict[str, str] = {
    "m/m": "monthly",
    "y/y": "yearly",
    "q/q": "quarterly",
    "w/w": "weekly",
    "d/d": "daily",
}


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


_ORDERED: list[tuple[str, str, str]] = sorted(
    ((k, _norm(k), v) for k, v in EVENT_MEANINGS.items()),
    key=lambda x: -len(x[1]),
)


def explain(event_name: str) -> str | None:
    """Return the best 1-line explanation for this event name, or None.
    Longest normalized-substring match wins. Case-insensitive."""
    if not event_name:
        return None
    n = _norm(event_name)
    for _original_key, normed_key, meaning in _ORDERED:
        if normed_key in n or n in normed_key:
            return meaning
    return None


def friendly_name(event_name: str) -> str:
    """Elevate the event name for human readability:
    - Expand recognized acronyms in parentheses on first occurrence
    - Replace m/m, y/y, q/q with the word (monthly, yearly, quarterly)

    Idempotent-ish: safe to run once. Example:
      "Core CPI m/m" → "Core CPI (Consumer Price Index) — monthly"
    """
    if not event_name:
        return event_name
    out = event_name
    # Replace frequency shorthand (whole-word case-insensitive)
    for shorthand, phrase in FREQUENCY_EXPANSIONS.items():
        # Handle m/m, y/y, q/q, w/w with the slash intact
        if shorthand in out:
            out = out.replace(shorthand, f"— {phrase}")
    # Expand FIRST-matching acronym found in the original name.
    # Only one expansion per event to avoid clutter.
    for acronym, full in ACRONYM_EXPANSIONS.items():
        # Whole-word match on the acronym (case-sensitive since these are all caps)
        if _has_whole_word(event_name, acronym):
            # Insert the expansion after the first occurrence of the acronym token
            out = _insert_expansion_once(out, acronym, full)
            break
    return out


def _has_whole_word(text: str, word: str) -> bool:
    """Check whether `word` appears in `text` bounded by non-alphanumeric on both sides."""
    import re
    return re.search(rf"(?<![A-Za-z0-9]){re.escape(word)}(?![A-Za-z0-9])", text) is not None


def _insert_expansion_once(text: str, acronym: str, full: str) -> str:
    """Insert ' (full)' after the first whole-word occurrence of `acronym` in `text`."""
    import re
    pattern = re.compile(rf"(?<![A-Za-z0-9]){re.escape(acronym)}(?![A-Za-z0-9])")
    m = pattern.search(text)
    if not m:
        return text
    end = m.end()
    return text[:end] + f" ({full})" + text[end:]
