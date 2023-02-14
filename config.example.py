ALPACA_PUBLIC_KEY = "<your public key>"
ALPACA_SECRET_KEY = "<your secret key>"
PAPER = True

# list of large cap stocks to trade
TRADE_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOG", "FB", "JPM", "JNJ", "V", "PG",
    "UNH", "MA", "HD", "VZ", "DIS", "BAC", "INTC", "T", "PFE", "CMCSA",
    "WFC", "KO", "PEP", "NFLX", "NVDA", "ADBE", "CRM", "TMO", "CSCO", "ABT",
    "NKE", "MRK", "MDT", "ACN", "COST", "AVGO", "TXN", "QCOM", "UNP", "NEE",
    "PYPL", "LIN", "PM", "CVX", "MCD", "ORCL", "UPS", "IBM", "LOW", "MMM",
    "AMGN", "GS", "BA", "CAT", "XOM", "WMT", "DHR", "AMT", "AXP", "HON",
    "CVS", "BKNG", "CHTR", "SBUX", "GILD", "MDLZ", "BLK", "INTU", "TGT",
    "ZTS", "WBA", "MU", "GE", "MCK", "GPN", "FIS", "USB", "DUK", "DOW",
    "PLD", "RTX", "ANTM", "DE", "ISRG", "SYK", "LMT", "CI", "MS", "TJX",
    "BK", "C", "PNC", "SPGI", "ADP", "CL", "SO", "CME", "COP", "MDXG",
    "CNC", "CARR", "CRL", "CPB", "COF", "CAH", "KMX", "KHC", "K", "KEY",
    "KMB", "KIM", "KMI", "KLAC", "KSS", "KDP", "KR", "LB", "LHX", "LH",
    "LRCX", "LW", "LVS", "LEG", "LDOS", "LEN", "LLY", "LNC", "LIN", "LYB",
    "LKQ", "LMT", "L", "LOW", "LUMN", "LYV", "MTB", "MRO", "MPC", "MKTX",
    "MAR", "MMC", "MLM", "MAS", "MA", "MKC", "MXIM", "MCD", "MCK", "MDT",
    "MRK", "MET", "MTD", "MGM", "MCHP", "MU", "MSFT", "MAA", "MHK", "TAP",
    "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "MYL", "NDAQ", "NOV",
    "NTAP", "NFLX", "NWL", "NEM", "NWSA", "NWS", "NEE", "NLSN", "NKE",
    "NI", "NSC", "NTRS", "NOC", "NLOK", "NCLH", "NRG", "NUE", "NVDA",
    "NVR", "ORLY", "OXY", "ODFL", "OMC", "OKE", "ORCL", "PCAR", "PKG",
    "PH", "PAYX", "PAYC", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO",
    "PFE", "PM", "PSX", "PNW", "PXD", "PNC", "POOL", "PPG", "PPL", "PFG",
    "PG", "PGR", "PLD", "PRU", "PTC", "PEG", "PSA", "PHM", "PVH", "QRVO",
    "PWR", "QCOM", "DGX", "RL", "RJF", "RTX", "O", "REG", "REGN", "RF",
    "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI",
    "CRM", "SBAC", "SLB", "STX", "SEE", "SRE", "NOW", "SHW", "SPG", "SWKS",
    "SLG", "SNA", "SO", "LUV", "SWK", "SBUX", "STT", "STE", "SYK", "SIVB",
    "SYF", "SNPS", "SYY", "TMUS", "TROW", "TTWO", "TPR", "TGT", "TEL",
    "TDY", "TFX", "TER", "TSLA", "TXN", "TXT", "TMO", "TJX", "TSCO",
    "TT", "TDG", "TRV", "TRMB", "TFC", "TWTR", "TYL", "TSN", "UDR", "ULTA",
    "USB", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", "URI", "UHS", "UNM",
    "VLO", "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VFC", "VIAC", "VTRS",
    "V", "VNO", "VMC", "WRB", "WAB", "WMT", "WBA", "DIS", "WM", "WAT",
    "WEC", "WFC", "WELL", "WST", "WDC", "WU", "WRK", "WY", "WHR", "WMB",
    "WLTW", "WYNN", "XEL", "XRX", "XYL", "YUM", "ZBRA", "ZBH",
    "ZION", "ZTS"
]

# API is limited to 200 requests per minute
ALPACA_TIMEOUT = 3.0


def CHOOSE_AMOUNT(value):
    value_buys = {1: 200, 5: 40, 10: 20, 20: 10, 50: 4, 100: 2}
    for key in value_buys:
        if value <= key:
            return value_buys[key]
    return 1
