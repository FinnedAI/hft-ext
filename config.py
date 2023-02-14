# These are our API keys and other configuration settings
# for the Alpaca API and the trading algorithm.
# ALPACA_PUBLIC_KEY is the API key ID for your account.
# ALPACA_SECRET_KEY is the "passphrase" for your API key.
# PAPER is a boolean value that determines whether we are
# using the paper trading API or the live trading API.
# You can configure these values by running the helpers/auth.py script.
ALPACA_PUBLIC_KEY = "<my api id key>"
ALPACA_SECRET_KEY = "<my api secret key>"
PAPER = True

# ALPACA_TIMEOUT is the number of seconds we will wait for
# to avoid rate limiting. This same value is used for both
# Yahoo Finance and Alpaca. It defaults to 3 seconds.
ALPACA_TIMEOUT = 3.0

# SHARES_BY_PRICE is a dictionary that maps the price of a
# share to the number of shares we want to buy at that price.
# For example, we want to buy 200 shares at $1, 100 shares
# at $2, 40 shares at $5, 20 shares at $10, 10 shares at $20, ...
# You can configure this dictionary by running the helpers/amount.py script.
SHARES_BY_PRICE = {1: 200, 2: 100, 5: 40, 10: 20, 50: 4, 100: 2}

# TRADE_TICKERS is a list of the tickers we want to trade.
# We will use the first 100 tickers in the S&P 500 by default.
# You can change this list to any other tickers you want.
# You can configure this list by running the helpers/tickers.py script.
TRADE_TICKERS = [ "AAPL", "MSFT", "AMZN", "GOOG", "FB", "JPM", "JNJ", "V", "PG", "UNH", "MA", "HD", "VZ", "DIS", "BAC", "INTC", "T", "PFE", "CMCSA", "WFC", "KO", "PEP", "NFLX", "NVDA", "ADBE", "CRM", "TMO", "CSCO", "ABT", "NKE", "MRK", "MDT", "ACN", "COST", "AVGO", "TXN", "QCOM", "UNP", "NEE", "PYPL", "LIN", "PM", "CVX", "MCD", "ORCL", "UPS", "IBM", "LOW", "MMM", "AMGN", "GS", "BA", "CAT", "XOM", "WMT", "DHR", "AMT", "AXP", "HON", "CVS", "BKNG", "CHTR", "SBUX", "GILD", "MDLZ", "BLK", "INTU", "TGT", "ZTS", "WBA", "MU", "GE", "MCK", "GPN", "FIS", "USB", "DUK", "DOW", "PLD", "RTX", "ANTM", "DE", "ISRG", "SYK", "LMT", "CI", "MS", "TJX", "BK", "C", "PNC", "SPGI", "ADP", "CL", "SO", "CME", "COP", "MDXG", "CNC", "CARR", "CRL", "CPB", "COF", "CAH", "KMX", "KHC", "K", "KEY", "KMB", "KIM", "KMI", "KLAC", "KSS", "KDP", "KR", "LB", "LHX", "LH", "LRCX", "LW", "LVS", "LEG", "LDOS", "LEN", "LLY", "LNC", "LIN", "LYB", "LKQ", "LMT", "L", "LOW", "LUMN", "LYV", "MTB", "MRO", "MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MKC", "MXIM", "MCD", "MCK", "MDT", "MRK", "MET", "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MHK", "TAP", "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "MYL", "NDAQ", "NOV", "NTAP", "NFLX", "NWL", "NEM", "NWSA", "NWS", "NEE", "NLSN", "NKE", "NI", "NSC", "NTRS", "NOC", "NLOK", "NCLH", "NRG", "NUE", "NVDA", "NVR", "ORLY", "OXY", "ODFL", "OMC", "OKE", "ORCL", "PCAR", "PKG", "PH", "PAYX", "PAYC", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO", "PFE", "PM", "PSX", "PNW", "PXD", "PNC", "POOL", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PTC", "PEG", "PSA", "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SEE", "SRE", "NOW", "SHW", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV", "SWK", "SBUX", "STT", "STE", "SYK", "SIVB", "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", "TPR", "TGT", "TEL", "TDY", "TFX", "TER", "TSLA", "TXN", "TXT", "TMO", "TJX", "TSCO", "TT", "TDG", "TRV", "TRMB", "TFC", "TWTR", "TYL", "TSN", "UDR", "ULTA", "USB", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", "URI", "UHS", "UNM", "VLO", "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VFC", "VIAC", "VTRS", "V", "VNO", "VMC", "WRB", "WAB", "WMT", "WBA", "DIS", "WM", "WAT", "WEC", "WFC", "WELL", "WST", "WDC", "WU", "WRK", "WY", "WHR", "WMB", "WLTW", "WYNN", "XEL", "XRX", "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS"]

# CHOOSE_AMOUNT is a function that takes a price and returns
# the number of shares we want to buy at that price. It is not
# configurable, but you can change it if you want.
def CHOOSE_AMOUNT(value):
    for key in SHARES_BY_PRICE:
        if value <= key:
            return SHARES_BY_PRICE[key]
    return 1
