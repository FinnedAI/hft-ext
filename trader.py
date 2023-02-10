import config as CONFIG
import os
from alpaca.trading.client import TradingClient
import urllib3
import json
import pandas as pd
import asyncio
from cli import CliHandler

http = urllib3.PoolManager()
cli = CliHandler()
api = TradingClient(
    CONFIG.ALPACA_PUBLIC_KEY, CONFIG.ALPACA_SECRET_KEY, paper=CONFIG.PAPER
)


class Portfolio:
    def __init__(self):
        self.portfolio = json.load(open("portfolio.json"))

    def get(self, ticker):
        if ticker in self.portfolio:
            return self.portfolio[ticker]
        raise Exception("Ticker not in portfolio")

    def add(self, ticker, quantity):
        if ticker in self.portfolio:
            self.portfolio[ticker] += quantity
        else:
            self.portfolio[ticker] = quantity

    def remove(self, ticker, quantity):
        if ticker in self.portfolio:
            self.portfolio[ticker] -= quantity
        else:
            raise Exception("Ticker not in portfolio")

    exists = lambda self, ticker: ticker in self.portfolio

    all = lambda self: self.portfolio

    def save(self):
        with open("portfolio.json", "w") as f:
            json.dump(self.portfolio, f)


portfolio = Portfolio()


class StockTrader:
    def __init__(self):
        self.account = api.get_account()
        self.market_is_open = lambda: api.get_clock().is_open
        self.tickers = False
        self.market = {}
        self.changes = {}

    async def retrieve_tickers(self):
        if self.tickers:
            return self.tickers

        url = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqtraded.txt"
        df = pd.read_csv(url, sep="|")["Symbol"][:-1]
        blacklist = [".", "$"]
        self.tickers = [t for t in df if all(char not in t for char in blacklist)]
        return self.tickers

    async def get_tickers_json(self):
        tickers = await self.retrieve_tickers()
        ticker_batches = [tickers[i: i + 1900] for i in range(0, len(tickers), 1900)]
        for batch in ticker_batches:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={'%2c'.join(batch)}&corsDomain=finance.yahoo.com"
            response = http.request("GET", url)
            data = json.loads(response.data)
            for ticker in data["quoteResponse"]["result"]:
                await self.make_decision(
                    ticker["symbol"], ticker["regularMarketPrice"]["raw"]
                )

    async def make_decision(self, ticker, price):
        if ticker not in self.market:
            self.market[ticker] = price
            self.changes[ticker] = 0
            return

        change = (price - self.market[ticker]) / self.market[ticker] * 100
        self.market[ticker] = price
        self.changes[ticker] = change
        if change > CONFIG.BUY_THRESHOLD and self.account.buying_power > price:
            max_shares = int(self.account.buying_power / price)
            preferred_shares = CONFIG.CHOOSE_AMOUNT(price)
            qty = min(max_shares, preferred_shares)
            api.submit_order(
                symbol=ticker, qty=qty, side="buy", type="market", time_in_force="day"
            )
            portfolio.add(ticker, qty)
            cli.buy_msg(ticker, price, qty)

    async def start_buys(self):
        try:
            while True:
                if not self.market_is_open():
                    await asyncio.sleep(60)
                    continue

                await self.get_tickers_json()
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            portfolio.save()
            os._exit(0)

    async def start_sells(self):
        try:
            while True:
                if not self.market_is_open():
                    await asyncio.sleep(60)
                    continue

                for ticker in portfolio.all():
                    change = self.changes[ticker]
                    if change < CONFIG.SELL_THRESHOLD:
                        qty = portfolio.get(ticker)
                        api.submit_order(
                            symbol=ticker,
                            qty=qty,
                            side="sell",
                            type="market",
                            time_in_force="day",
                        )
                        portfolio.remove(ticker, ticker, qty)
                        cli.sell_msg(ticker, self.market[ticker], qty)
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            portfolio.save()
            os._exit(0)


class StockTraderRunner:
    def __init__(self):
        self.trader = StockTrader()

    async def run(self):
        cli.print_startup()
        loop = asyncio.get_event_loop()
        loop.create_task(self.trader.start_buys())
        loop.create_task(self.trader.start_sells())
        loop.create_task(self.listen_for_exit())
        loop.run_forever()

    def exit_safely(self):
        portfolio.save()
        os._exit(1)

    async def listen_for_exit(self):
        try:
            while True:
                if input() == "exit":
                    self.exit_safely()
        except KeyboardInterrupt:
            self.exit_safely()
