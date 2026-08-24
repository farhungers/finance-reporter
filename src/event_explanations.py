"""1-line explanations for common 3-star economic events (CLAUDE.md §D.1.a Part 1).

Two-part model (2026-08-24 roadmap Phase 1):
  • EVENT_DEFINITIONS  → "what the release IS" — plain-English definition
  • EVENT_MEANINGS     → "how it moves markets" — consequence / playbook one-liner

Both dicts share the same longest-substring-match key convention. Callers get
either via what_is() / explain() or both via explain_full(). The daily_morning
calendar card renders both lines for US 3-star events; smaller events show the
market-effect line only, per length-budget guardrail.

Missing an event? Add to EVENT_MEANINGS first (always), then EVENT_DEFINITIONS
if the release is US-material. Not LLM-generated — stable reference data,
editable by operator.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# "How it moves markets" — one-line consequence.
# Ordered by specificity — longer more-specific keys FIRST so they match before
# shorter generic ones. The matcher iterates this list in insertion order.
# ---------------------------------------------------------------------------
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
    "Challenger Job Cuts": "Corporate layoff announcements; noisy but leads NFP in downturns.",

    # ---- US Fed ----
    "Federal Funds Rate": "FOMC rate decision itself; statement + dots + presser is the day-long sequence.",
    "FOMC Statement": "Fed policy statement; forward-guidance edits move duration + risk assets.",
    "FOMC Press Conference": "Powell Q&A; often re-writes the message the statement began.",
    "FOMC Meeting Minutes": "3-week-old detail; occasionally recalibrates rate expectations at the margin.",
    "FOMC Economic Projections": "SEP + dot plot at Mar/Jun/Sep/Dec; the dot median revision is the read.",
    "Fed Chair Powell Speaks": "Any Powell speech is potentially market-moving; hawkish vs dovish lean is the read.",
    "Fed Chair Powell Testifies": "Congress testimony; Q&A can surface policy nuance beyond prepared remarks.",
    "Chair Powell Speaks": "Any Powell speech is potentially market-moving; hawkish vs dovish lean is the read.",
    "Beige Book": "Regional Fed anecdotes 2 weeks pre-FOMC; qualitative color, occasionally moves rate expectations.",

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
    "Housing Starts": "New-construction pace; rate-sensitive housing cycle read.",
    "Durable Goods Orders m/m": "Big-ticket capex; ex-transport is the cleaner signal.",
    "Core Durable Goods Orders m/m": "Capex demand ex volatile aircraft — business investment pulse.",
    "Chicago PMI": "Regional mfg survey day before ISM; often front-runs the national print.",
    "Empire State Manufacturing Index": "First regional Fed survey each month; sets tone before ISM.",
    "Philly Fed Manufacturing Index": "Second regional Fed survey; more weight than Empire.",
    "Richmond Manufacturing Index": "Third regional survey; confirms/rejects the earlier two.",
    "S&P/Case-Shiller HPI y/y": "20-city home price index — housing wealth + rent CPI input, 2-month lag.",
    "Industrial Production m/m": "Fed's output gauge — utility + mining + mfg mix; recession signal when persistently negative.",
    "Personal Income m/m": "Household income growth; feeds savings + consumption forecasts.",
    "Personal Spending m/m": "Consumer outlays; released with PCE inflation same morning.",
    "Trade Balance": "US goods + services trade deficit; USD-sensitive on wide moves.",
    "Factory Orders m/m": "Order book for durable + non-durable; overlaps Durable Goods.",
    "Wholesale Inventories m/m": "Inventory stocking pace; late-cycle demand signal.",
    "Chicago Fed National Activity Index": "Composite of 85 indicators; growth pulse vs trend.",
    "Conference Board Leading Index m/m": "10-indicator leading index; negative streaks flag recession odds.",

    # ---- US Treasury / funding ----
    "10-y Bond Auction": "Treasury 10-year auction — bid-to-cover + tail size moves duration.",
    "30-y Bond Auction": "Treasury 30-year auction — long-end demand read; foreign participation matters.",
    "3-y Note Auction": "Treasury 3-year auction — short-end demand; cleanest of the trio for rate expectations.",
    "TIC Long-Term Purchases": "Foreign net Treasury flows 2 months lagged; USD structural demand signal.",
    "Fed Balance Sheet": "H.4.1 Wednesday release; QT pace + reserves; regime read for liquidity-sensitive assets.",

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
    "Jackson Hole Symposium": "Late-Aug Fed conference; Powell keynote often re-anchors policy narrative into fall.",
    "OPEC Meetings": "Production-quota decision; sets crude supply floor for the next quarter.",
    "OPEC-JMMC Meetings": "Joint OPEC monitoring; interim signal between full meetings.",
}


# ---------------------------------------------------------------------------
# "What the release IS" — plain-English definition. Primary focus: US events
# where a Wall Street FA needs to sound informed to clients. Longer keys first
# so specific variants beat generic ones.
# ---------------------------------------------------------------------------
EVENT_DEFINITIONS: dict[str, str] = {
    # ---- US inflation ----
    "Core CPI m/m": "US consumer inflation excluding food and energy, monthly change — the sticky-price trend the Fed weights most.",
    "Core CPI y/y": "Same core CPI measure but yearly — the annual trend a client hears about on TV.",
    "CPI m/m": "US consumer prices tracked by BLS across housing, food, energy, medical, transport — released 8:30 ET mid-month.",
    "CPI y/y": "Same headline CPI but yearly — the 'inflation rate' the news uses; policy-relevant when trending vs Fed's 2% goal.",
    "Trimmed Mean CPI m/m": "Cleveland Fed's inflation cut that trims the biggest movers each month — smoother than core CPI.",
    "Core PPI m/m": "Producer input prices excluding food and energy, monthly — leads CPI by 1-2 months in pass-through.",
    "PPI m/m": "US wholesale prices producers receive — supply-side inflation read, released day before or after CPI.",
    "Core PCE Price Index m/m": "The Fed's actual 2% inflation target measure (personal consumption expenditures ex food/energy), released last week of month.",
    "PCE Price Index m/m": "Broader PCE inflation including food and energy — Fed's target metric, released with personal income/spending.",

    # ---- US labor ----
    "Non-Farm Employment Change": "Number of new jobs added by US employers (excluding farm workers) last month — the headline jobs report on the first Friday.",
    "Unemployment Rate": "Share of the US labor force actively looking for work — headline recession gauge.",
    "Average Hourly Earnings m/m": "How fast US wages grew last month — the wage-inflation feed into Fed policy.",
    "ADP Non-Farm Employment Change": "Private payroll firm ADP's estimate of US private-sector jobs — released 2 days before NFP as a rough preview.",
    "JOLTS Job Openings": "Number of unfilled US job openings on the last business day of the prior month — Fed's labor-tightness gauge.",
    "Unemployment Claims": "New Americans filing for jobless benefits last week — real-time labor pulse released each Thursday.",
    "Challenger Job Cuts": "Total layoffs announced by US employers last month, tracked by Challenger Gray & Christmas.",

    # ---- US Fed ----
    "Federal Funds Rate": "The Fed's target interest rate decision — sets the floor for all US borrowing costs, decided 8 times a year.",
    "FOMC Statement": "Written Fed policy statement released with each rate decision — the specific wording moves markets when it changes.",
    "FOMC Press Conference": "Fed Chair's live Q&A 30 minutes after the rate decision — Powell's tone often overrides the statement.",
    "FOMC Meeting Minutes": "Detailed minutes of a Fed meeting, released 3 weeks after — reveals internal debate and hawk/dove balance.",
    "FOMC Economic Projections": "Fed officials' quarterly forecasts including the famous 'dot plot' showing each member's expected policy rate path.",
    "Fed Chair Powell Speaks": "Any scheduled speech by Fed Chair Jerome Powell — every word parsed for policy hints.",
    "Fed Chair Powell Testifies": "Powell's semiannual testimony to Congress (Humphrey-Hawkins) — Q&A can produce more news than prepared remarks.",
    "Chair Powell Speaks": "Scheduled Powell remarks (event calendar sometimes labels this variant).",
    "Beige Book": "Anecdotal economic conditions across the 12 Fed districts, released 2 weeks before each FOMC meeting.",

    # ---- US activity ----
    "Core Retail Sales m/m": "US retail sales excluding auto dealers — cleaner read on discretionary consumer spending.",
    "Retail Sales m/m": "How much Americans spent at retailers last month — the primary consumer-spending read, released mid-month.",
    "Advance GDP q/q": "First estimate of last quarter's US economic growth, released ~a month after quarter-end — most market-moving of the three GDP releases.",
    "Prelim GDP q/q": "Second estimate of last quarter's US GDP — revises the advance number with more complete data.",
    "GDP q/q": "US Gross Domestic Product growth for the quarter, annualized — the broadest measure of economic activity.",
    "ISM Manufacturing PMI": "Survey of US factory purchasing managers — above 50 = expansion, below = contraction. First business day each month.",
    "ISM Services PMI": "Same survey applied to the US services sector (much larger than manufacturing) — released third business day of month.",
    "S&P Global US Manufacturing PMI": "Private-sector US manufacturing survey by S&P Global — earlier release than ISM, methodologically similar.",
    "S&P Global US Services PMI": "Private-sector US services survey — companion to the manufacturing print.",
    "CB Consumer Confidence": "Conference Board's survey of ~5,000 US households about current + expected economic conditions.",
    "Consumer Confidence": "Same Conference Board consumer confidence survey (short label variant).",
    "Prelim UoM Consumer Sentiment": "University of Michigan mid-month preview of consumer sentiment plus 1-year and 5-10 year inflation expectations.",
    "Revised UoM Consumer Sentiment": "End-of-month final University of Michigan sentiment number — smaller revisions vs prelim.",
    "Existing Home Sales": "Annualized pace of existing-home sales closings in the US — released by NAR mid-month.",
    "New Home Sales": "Annualized pace of new single-family home sales — thinner data than existing sales but more forward-looking.",
    "Building Permits": "New housing units authorized by permit — leads housing starts by 1-2 months.",
    "Housing Starts": "New privately-owned housing units where construction began last month.",
    "Durable Goods Orders m/m": "New US orders for goods designed to last 3+ years (planes, cars, machinery) — capex demand read.",
    "Core Durable Goods Orders m/m": "Durable orders excluding transportation (which is dominated by lumpy aircraft orders) — cleaner capex signal.",
    "Chicago PMI": "MNI Chicago Business Barometer — regional purchasing managers survey, released last business day of month, just before ISM.",
    "Empire State Manufacturing Index": "NY Fed's monthly manufacturing survey — first regional Fed survey each month, sets early tone.",
    "Philly Fed Manufacturing Index": "Philadelphia Fed's monthly manufacturing survey — second-tier signal after Empire but before ISM.",
    "Richmond Manufacturing Index": "Richmond Fed's monthly manufacturing survey — completes the three regional-Fed set.",
    "S&P/Case-Shiller HPI y/y": "S&P CoreLogic Case-Shiller 20-city home price index — released with a 2-month lag.",
    "Industrial Production m/m": "Fed's index of US manufacturing, mining, and utility output — persistent negative prints often flag recession.",
    "Personal Income m/m": "How much Americans earned (wages + benefits + investment income) last month.",
    "Personal Spending m/m": "How much Americans spent last month — released alongside PCE inflation same morning.",
    "Trade Balance": "US exports minus imports for goods and services — a growing deficit typically weighs on USD marginally.",
    "Factory Orders m/m": "New orders received by US manufacturers (durable + non-durable goods).",
    "Wholesale Inventories m/m": "How much inventory US wholesalers hold — rising inventories vs sales flags demand weakness.",
    "Chicago Fed National Activity Index": "Composite of 85 indicators normalized to zero (trend growth) — negative = below-trend growth.",
    "Conference Board Leading Index m/m": "Composite of 10 forward-looking US indicators — extended negative streaks historically precede recessions.",

    # ---- US Treasury / funding ----
    "10-y Bond Auction": "US Treasury's regular auction of 10-year notes — bid-to-cover and yield 'tail' size gauge demand.",
    "30-y Bond Auction": "US Treasury's auction of 30-year bonds — long-end demand read, foreign participation especially watched.",
    "3-y Note Auction": "US Treasury's auction of 3-year notes — short-end demand tracks rate-cut expectations most directly.",
    "TIC Long-Term Purchases": "Treasury International Capital data — foreign net purchases of long-term US securities, 2-month lag.",
    "Fed Balance Sheet": "Weekly H.4.1 report of Fed asset holdings — QT pace + bank reserves determine system liquidity.",

    # ---- Non-US central banks (kept brief; not the FA's core focus) ----
    "Main Refinancing Rate": "European Central Bank's main policy rate decision.",
    "Official Bank Rate": "Bank of England's policy rate decision.",
    "BOJ Policy Rate": "Bank of Japan's policy rate decision.",
    "Overnight Rate": "Bank of Canada's policy rate decision.",
    "SNB Policy Rate": "Swiss National Bank's policy rate decision.",
    "Cash Rate": "Reserve Bank of Australia's policy rate decision.",
    "RBA Cash Rate": "Reserve Bank of Australia's policy rate decision.",
    "Official Cash Rate": "Reserve Bank of New Zealand's policy rate decision.",

    # ---- Special events ----
    "Jackson Hole Symposium": "Late-August Fed conference in Wyoming — Powell's keynote traditionally previews policy pivots (2010 QE2, 2022 hawkish reset).",
    "OPEC Meetings": "OPEC production quota decision — sets crude oil supply for the next quarter.",
    "Bank Holiday": "Major exchange or bank closure — reduced liquidity in the affected region's assets.",
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
    "TIC": "Treasury International Capital",
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

_ORDERED_DEFS: list[tuple[str, str, str]] = sorted(
    ((k, _norm(k), v) for k, v in EVENT_DEFINITIONS.items()),
    key=lambda x: -len(x[1]),
)


def _best_match(n: str, ordered: list[tuple[str, str, str]]) -> str | None:
    """Directional matcher: prefer key-appears-in-input (longest key wins),
    fall back to input-appears-in-key only if no direct match. This prevents
    "CPI m/m" from binding to the longer "Trimmed Mean CPI m/m" record just
    because the sorted-by-length iteration hit it first."""
    # Pass 1: key IN input (longest key wins — iteration is length-sorted)
    for _original_key, normed_key, value in ordered:
        if normed_key in n:
            return value
    # Pass 2: input IN key (fall back — helps when the input is a short label
    # that matches a longer canonical key)
    for _original_key, normed_key, value in ordered:
        if n in normed_key:
            return value
    return None


def explain(event_name: str) -> str | None:
    """Return the best 1-line MARKET-EFFECT explanation, or None. Case-insensitive."""
    if not event_name:
        return None
    return _best_match(_norm(event_name), _ORDERED)


def what_is(event_name: str) -> str | None:
    """Return the best 1-line DEFINITION ('what the release is'), or None.
    Same matching rules as explain(). Coverage is US-focused per §D.1.a.

    Callers render this as the 'What it is' line above the market-effect line
    for US 3-star events. Missing definition = fall back to explain() only."""
    if not event_name:
        return None
    return _best_match(_norm(event_name), _ORDERED_DEFS)


def explain_full(event_name: str) -> dict[str, str | None]:
    """Return {'what_it_is': ..., 'market_effect': ...} — both may be None.
    Convenience for report renderers that want the full two-line card."""
    return {
        "what_it_is": what_is(event_name),
        "market_effect": explain(event_name),
    }


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


# ---------------------------------------------------------------------------
# Country-to-macro-playbook mapping (Phase 2 wire-in).
# Maps event-name substrings to knowledge/macro/*.md filenames. When today's
# calendar contains a US 3-star event, knowledge.load_for_report() opts to load
# the matching playbook into the LLM context. Keys are lowercase substrings
# matched against event_name; first match wins.
# ---------------------------------------------------------------------------
EVENT_TO_PLAYBOOK: dict[str, str] = {
    "core cpi": "cpi_playbook.md",
    "cpi": "cpi_playbook.md",
    "core pce": "pce_playbook.md",
    "pce price": "pce_playbook.md",
    "core ppi": "ppi_playbook.md",
    "ppi": "ppi_playbook.md",
    "non-farm employment": "nfp_playbook.md",
    "unemployment rate": "nfp_playbook.md",
    "average hourly earnings": "nfp_playbook.md",
    "adp non-farm": "nfp_playbook.md",
    "jolts": "jolts_playbook.md",
    "federal funds rate": "fomc_playbook.md",
    "fomc statement": "fomc_playbook.md",
    "fomc press conference": "fomc_playbook.md",
    "fomc meeting minutes": "fomc_playbook.md",
    "fomc economic projections": "dot_plot_playbook.md",
    "chair powell": "powell_speeches.md",
    "fed chair powell": "powell_speeches.md",
    "beige book": "fomc_playbook.md",
    "retail sales": "retail_sales_playbook.md",
    "ism manufacturing": "ism_playbook.md",
    "ism services": "ism_playbook.md",
    "10-y bond auction": "treasury_auctions.md",
    "30-y bond auction": "treasury_auctions.md",
    "3-y note auction": "treasury_auctions.md",
    "jackson hole": "jackson_hole.md",
}


def matching_playbook(event_name: str) -> str | None:
    """Return the knowledge/macro/*.md filename that explains this event, or None.
    Used by knowledge loader to pull the right US-macro playbook into the LLM
    context on days when a corresponding 3-star event is scheduled."""
    if not event_name:
        return None
    n = _norm(event_name)
    # Longer keys first so 'core cpi' beats 'cpi'
    for key in sorted(EVENT_TO_PLAYBOOK, key=len, reverse=True):
        if key in n:
            return EVENT_TO_PLAYBOOK[key]
    return None
