from typing import Final

# ────────────────────────────────────────────────────────────────────────────
# US universes (default focus)
# ────────────────────────────────────────────────────────────────────────────

# Dow Jones Industrial Average — 30 large-cap US stocks
DOW_30: Final[list[str]] = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX",
    "DIS", "GS", "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM",
    "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ",
    "WMT",
]

# Magnificent 7 — the dominant US mega-caps
MAG_7: Final[list[str]] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
]

# Classic FAANG
FAANG: Final[list[str]] = ["META", "AAPL", "AMZN", "NFLX", "GOOGL"]

# A practical NASDAQ-100 subset (top ~50 by liquidity, useful for portfolio work)
NASDAQ_100_TOP: Final[list[str]] = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA",
    "AVGO", "COST", "NFLX", "ADBE", "PEP", "AMD", "INTC", "CSCO",
    "CMCSA", "TMUS", "QCOM", "INTU", "AMGN", "TXN", "ISRG", "BKNG",
    "HON", "AMAT", "VRTX", "PANW", "REGN", "MU", "ADP", "LRCX",
    "SBUX", "GILD", "MDLZ", "ADI", "KLAC", "PYPL", "CRWD", "SNPS",
    "CDNS", "MAR", "MNST", "ABNB", "ASML", "MELI", "FTNT", "ORLY",
    "CHTR", "CTAS",
]

# S&P 100 — broad large-cap US
SP_100: Final[list[str]] = [
    "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT",
    "AMZN", "AVGO", "AXP", "BA", "BAC", "BK", "BLK", "BMY", "BRK-B",
    "C", "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM",
    "CSCO", "CVS", "CVX", "DE", "DHR", "DIS", "DOW", "DUK", "EMR",
    "F", "FDX", "GD", "GE", "GILD", "GM", "GOOG", "GOOGL", "GS", "HD",
    "HON", "IBM", "INTC", "INTU", "JNJ", "JPM", "KHC", "KO", "LIN",
    "LLY", "LMT", "LOW", "MA", "MCD", "MDLZ", "MDT", "MET", "META",
    "MMM", "MO", "MRK", "MS", "MSFT", "NEE", "NFLX", "NKE", "NVDA",
    "ORCL", "PEP", "PFE", "PG", "PM", "PYPL", "QCOM", "RTX", "SBUX",
    "SCHW", "SO", "SPG", "T", "TGT", "TMO", "TMUS", "TSLA", "TXN",
    "UNH", "UNP", "UPS", "USB", "V", "VZ", "WBA", "WFC", "WMT", "XOM",
]

# A clean tech-mega-cap default — good first run
US_TECH_GIANTS: Final[list[str]] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
    "ORCL", "ADBE",
]

# Dividend Aristocrats (subset) — for income-focused investors
DIVIDEND_ARISTOCRATS: Final[list[str]] = [
    "KO", "PG", "JNJ", "MMM", "CL", "PEP", "MCD", "WMT", "T", "VZ",
    "CVX", "XOM", "ABBV", "EMR", "IBM", "MO", "ABT", "TGT", "ADP", "LOW",
]

# ────────────────────────────────────────────────────────────────────────────
# NIFTY universes (preserved — bundled offline data + DRL agents trained on this)
# ────────────────────────────────────────────────────────────────────────────

NIFTY_50: Final[list[str]] = [
    "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "ITC.NS", "IOC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS",
    "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS",
    "NESTLEIND.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS",
    "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS",
    "UPL.NS", "WIPRO.NS", "GAIL.NS", "TATACHEM.NS",
]

DRL_UNIVERSE: Final[list[str]] = [
    "ASIANPAINT.NS", "CIPLA.NS", "DRREDDY.NS", "GAIL.NS", "GRASIM.NS",
    "HDFCBANK.NS", "HEROMOTOCO.NS", "HINDUNILVR.NS", "INFY.NS", "ITC.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "POWERGRID.NS",
    "SUNPHARMA.NS", "TATACHEM.NS", "TCS.NS", "ULTRACEMCO.NS", "WIPRO.NS",
]

# ────────────────────────────────────────────────────────────────────────────
# Common US benchmark tickers (ETFs that track major indexes)
# ────────────────────────────────────────────────────────────────────────────

BENCHMARKS: Final[dict[str, str]] = {
    "SPY": "S&P 500 (SPDR)",
    "DIA": "Dow Jones Industrial Average (SPDR)",
    "QQQ": "NASDAQ-100 (Invesco)",
    "IWM": "Russell 2000 (iShares small-cap)",
    "VTI": "Total US Stock Market (Vanguard)",
    "VOO": "S&P 500 (Vanguard)",
}

# ────────────────────────────────────────────────────────────────────────────
# Registry (order matters: US first, NIFTY at the end as a research curio)
# ────────────────────────────────────────────────────────────────────────────

UNIVERSES: Final[dict[str, list[str]]] = {
    "DOW30": DOW_30,
    "MAG7": MAG_7,
    "FAANG": FAANG,
    "TECH_GIANTS": US_TECH_GIANTS,
    "NASDAQ100_TOP": NASDAQ_100_TOP,
    "SP100": SP_100,
    "DIVIDEND_KINGS": DIVIDEND_ARISTOCRATS,
    "NIFTY50": NIFTY_50,
    "DRL_NIFTY20": DRL_UNIVERSE,
}
