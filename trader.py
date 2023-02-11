import config as CONFIG
import os

# trade api is needed to retrieve positions
import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import urllib3
import json
import pandas as pd
from cli import CliHandler
from strategy import Strategy
from threading import Thread
import time
import sqlite3
from utils import Utils

http = urllib3.PoolManager()
cli = CliHandler()
utils = Utils()
strategy = Strategy()
api = TradingClient(
    CONFIG.ALPACA_PUBLIC_KEY, CONFIG.ALPACA_SECRET_KEY, paper=CONFIG.PAPER
)
account = tradeapi.REST(
    key_id=CONFIG.ALPACA_PUBLIC_KEY,
    secret_key=CONFIG.ALPACA_SECRET_KEY,
    base_url="https://paper-api.alpaca.markets",
    api_version="v2",
)


class Portfolio:
    def __init__(self):
        self.portfolio = {}

    def all(self):
        positions = account.list_positions()
        return {position.symbol: position.qty for position in positions}

    def cached(self):
        return self.portfolio

    def exists(self, ticker):
        return ticker in self.all().keys()

    def add(self, ticker, qty, price):
        market_order_data = MarketOrderRequest(
            symbol=ticker,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        api.submit_order(order_data=market_order_data)
        # wait for order to be processed
        time.sleep(CONFIG.ALPACA_TIMEOUT)
        # add to self.portfolio
        self.portfolio[ticker] = {qty: qty, price: price}

    def remove(self, ticker):
        qty = self.portfolio[ticker]["qty"]
        market_order_data = MarketOrderRequest(
            symbol=ticker,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        api.submit_order(order_data=market_order_data)
        # wait for order to be processed
        time.sleep(CONFIG.ALPACA_TIMEOUT)
        # remove from self.portfolio
        del self.portfolio[ticker]


portfolio = Portfolio()


class Storage:
    def __init__(self):
        self.conn = sqlite3.connect("ticker_data.db")
        self.create_table()

    def create_table(self):
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS ticker_data (
                        ticker text,
                        price real
                    )"""
        )
        self.conn.commit()

    def save_data(self, ticker, price):
        c = self.conn.cursor()
        c.execute(
            """INSERT INTO ticker_data (ticker, price)
                    VALUES (?,?)""",
            (ticker, price),
        )
        self.conn.commit()

    def retrieve_data(self, ticker):
        c = self.conn.cursor()
        c.execute(
            """SELECT price FROM ticker_data
                    WHERE ticker=?""",
            (ticker,),
        )
        return c.fetchall()


storage = Storage()


class StockTrader:
    def __init__(self):
        self.account = api.get_account()
        self.market_is_open = lambda: api.get_clock().is_open
        # keep track of buys and prices
        self.buys = {}

    def get_tickers_json(self):
        tickers = utils.batch(CONFIG.TRADE_TICKERS, 1900)
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={'%2c'.join(tickers)}&corsDomain=finance.yahoo.com"
        response = http.request("GET", url)
        data = json.loads(response.data)
        for ticker in data["quoteResponse"]["result"]:
            try:
                ticker, price = ticker["symbol"], ticker["regularMarketPrice"]["raw"]
                storage.save_data(ticker, price)
                self.make_decision(ticker, price)
            except:
                cli.custom_msg("red", f" -> Error with {ticker['symbol']}")
                pass

    def make_decision(self, ticker, price):
        if float(self.account.buying_power) < price:
            return

        should_buy = strategy.should_buy(ticker)
        if portfolio.exists(ticker) and should_buy:
            max_shares = int(float(self.account.buying_power) / price)
            preferred_shares = CONFIG.CHOOSE_AMOUNT(price)
            qty = min(max_shares, preferred_shares)
            if qty == 0:
                return

            try:
                portfolio.add(ticker, qty, price)
                cli.buy_msg(ticker, price, qty)
                self.buys[ticker] = (price, qty)
            except:
                cli.custom_msg("red", f" -> Error buying {ticker}")
                pass

    def start_buys(self):
        try:
            while True:
                if not self.market_is_open():
                    time.sleep(60)
                    continue

                self.get_tickers_json()
                time.sleep(30)
        except KeyboardInterrupt:
            os._exit(0)

    def start_sells(self):
        try:
            while True:
                if not self.market_is_open():
                    time.sleep(60)
                    continue

                positions = portfolio.all()
                for ticker in positions.keys():
                    if ticker not in portfolio.cached():
                        continue

                    try:
                        buy_amt, qty = self.buys[ticker]
                        pricelist = storage.retrieve_data(ticker)
                        should_sell = strategy.should_sell(buy_amt, pricelist)
                        if should_sell:
                            portfolio.remove(ticker)
                            cli.sell_msg(ticker)
                            del self.buys[ticker]
                    except:
                        cli.custom_msg("red", f" -> Error selling {ticker}")
                        pass
                time.sleep(5)
        except KeyboardInterrupt:
            os._exit(0)


class StockTraderRunner:
    def __init__(self):
        self.trader = StockTrader()

    def run(self):
        cli.print_startup()
        Thread(target=self.trader.start_buys).start()
        Thread(target=self.trader.start_sells).start()
        Thread(target=self.listen_for_exit).start()

    def exit_safely(self):
        os._exit(1)

    def listen_for_exit(self):
        try:
            while True:
                if input() == "exit":
                    self.exit_safely()
        except KeyboardInterrupt:
            self.exit_safely()
