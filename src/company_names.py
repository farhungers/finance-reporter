"""Ticker → human-readable company name (§C3 blue-chip universe).

Used to render 'Apple (AAPL)' instead of just 'AAPL' in pitch headers.
Kept as a code-level dict for O(1) lookup + zero LLM cost.
"""
from __future__ import annotations

COMPANY_NAMES: dict[str, str] = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia",
    "GOOGL": "Alphabet", "GOOG": "Alphabet", "AMZN": "Amazon",
    "META": "Meta", "TSLA": "Tesla", "BRK-B": "Berkshire Hathaway",
    "AVGO": "Broadcom", "LLY": "Eli Lilly", "JPM": "JPMorgan Chase",
    "V": "Visa", "WMT": "Walmart", "XOM": "Exxon Mobil",
    "UNH": "UnitedHealth", "MA": "Mastercard", "PG": "Procter & Gamble",
    "COST": "Costco", "JNJ": "Johnson & Johnson", "HD": "Home Depot",
    "ORCL": "Oracle", "BAC": "Bank of America", "ABBV": "AbbVie",
    "NFLX": "Netflix", "CVX": "Chevron", "KO": "Coca-Cola",
    "MRK": "Merck", "AMD": "AMD", "CRM": "Salesforce",
    "PEP": "PepsiCo", "TMO": "Thermo Fisher", "ADBE": "Adobe",
    "LIN": "Linde", "ACN": "Accenture", "MCD": "McDonald's",
    "CSCO": "Cisco", "ABT": "Abbott", "PM": "Philip Morris",
    "TXN": "Texas Instruments", "IBM": "IBM", "GE": "GE Aerospace",
    "WFC": "Wells Fargo", "DIS": "Disney", "DHR": "Danaher",
    "VZ": "Verizon", "INTC": "Intel", "CAT": "Caterpillar",
    "PFE": "Pfizer", "AMGN": "Amgen", "GS": "Goldman Sachs",
    "NOW": "ServiceNow", "QCOM": "Qualcomm", "AMAT": "Applied Materials",
    "T": "AT&T", "UBER": "Uber", "AXP": "American Express",
    "SPGI": "S&P Global", "MS": "Morgan Stanley", "BLK": "BlackRock",
    "RTX": "RTX", "NEE": "NextEra Energy", "BKNG": "Booking Holdings",
    "PGR": "Progressive", "HON": "Honeywell", "SYK": "Stryker",
    "TJX": "TJX Companies", "C": "Citigroup", "SCHW": "Charles Schwab",
    "LOW": "Lowe's", "COP": "ConocoPhillips", "BSX": "Boston Scientific",
    "PLD": "Prologis", "ADP": "ADP", "REGN": "Regeneron",
    "VRTX": "Vertex Pharmaceuticals", "ETN": "Eaton",
    "MMC": "Marsh McLennan", "GILD": "Gilead", "MDLZ": "Mondelez",
    "ANET": "Arista Networks", "DE": "Deere", "SBUX": "Starbucks",
    "CVS": "CVS Health", "MU": "Micron", "PANW": "Palo Alto Networks",
    "LMT": "Lockheed Martin", "FI": "Fiserv", "ADI": "Analog Devices",
    "BX": "Blackstone", "KLAC": "KLA", "SO": "Southern Company",
    "CB": "Chubb", "CI": "Cigna", "ICE": "Intercontinental Exchange",
    "USB": "US Bancorp", "AON": "Aon", "MO": "Altria",
}


def name(ticker: str) -> str:
    """Return the human-readable company name, or the ticker itself if unknown."""
    return COMPANY_NAMES.get(ticker.upper(), ticker.upper())
