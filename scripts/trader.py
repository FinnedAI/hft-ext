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
from scripts.cli import CliHandler
from scripts.strategy import Strategy, NeuralNetworkModel
from threading import Thread
import time
import sqlite3
from utils.utils import Utils

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

    def get(self, ticker):
        return self.portfolio[ticker]["price"], self.portfolio[ticker]["qty"]

    def cached(self):
        return self.portfolio

    def exists(self, ticker):
        return ticker in self.all().keys()

    def add(self, ticker, qty, price):
        order_data = self._create_market_order(ticker, qty, OrderSide.BUY)
        self._submit_order(order_data)
        self.portfolio[ticker] = {"qty": qty, "price": price}

    def remove(self, ticker):
        qty = self.portfolio[ticker]["qty"]
        order_data = self._create_market_order(ticker, qty, OrderSide.SELL)
        self._submit_order(order_data)
        del self.portfolio[ticker]

    def _create_market_order(self, ticker, qty, side):
        return MarketOrderRequest(
            symbol=ticker,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
        )

    def _submit_order(self, order_data):
        api.submit_order(order_data=order_data)
        time.sleep(CONFIG.ALPACA_TIMEOUT)


portfolio = Portfolio()


class Storage:
    def __init__(self):
        self.conn = sqlite3.connect("data/ticker_data.db")
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
storage.create_table()


class StockTrader:
    def __init__(self):
        self.account = api.get_account()
        self.market_is_open = lambda: api.get_clock().is_open
        self.back_open = False

    def _get_realtime_prices(self, tickers):
        tickers = utils.batch(CONFIG.TRADE_TICKERS, 1900)
        prices = strategy.get_live_prices(tickers)
        for ticker, price in prices.items():
            storage.save_data(ticker, price)
        return prices

    def _buy_manager(self, ticker, price):
        # don't buy if we can't afford it or we already own it
        # we don't want to buy if we already own it because we
        # don't want to concentrate our money in one stock
        if float(self.account.buying_power) < price or portfolio.exists(ticker):
            return

        pricelist = storage.retrieve_data(ticker)
        # 450 is the number of minutes in a trading day
        day_pricelist = pricelist[-450:] if len(pricelist) >= 450 else pricelist
        should_buy = strategy.should_buy(ticker, day_pricelist)
        if not should_buy:
            return

        max_shares = int(float(self.account.buying_power) / price)
        preferred_shares = CONFIG.CHOOSE_AMOUNT(price)
        qty = min(max_shares, preferred_shares)
        if qty == 0:
            return

        try:
            portfolio.add(ticker, qty, price)
            cli.buy_msg(ticker, price, qty)
            storage.save_data(ticker, price)
        except:
            cli.custom_msg("red", f" -> Error buying {ticker}")
            pass

    def _sell_manager(self, ticker, price):
        if not portfolio.exists(ticker):
            return

        buy_amt, qty = portfolio.get(ticker)
        pricelist = storage.retrieve_data(ticker)
        # 450 is the number of minutes in a trading day
        day_pricelist = pricelist[-450:] if len(pricelist) >= 450 else pricelist
        should_sell = strategy.should_sell(ticker, buy_amt, price, day_pricelist)
        if should_sell:
            portfolio.remove(ticker)
            cli.sell_msg(ticker)

    def start_buys(self):
        try:
            while True:
                if not self.market_is_open():
                    if self.back_open:
                        cli.custom_msg("yellow", " -> Stopping trades, market closed.")
                        # train NeuralNetwork model on latest data
                        for ticker in CONFIG.TRADE_TICKERS:
                            pricelist = storage.retrieve_data(ticker)
                            day_pricelist = (
                                pricelist[-450:] if len(pricelist) >= 450 else pricelist
                            )
                            nn = NeuralNetworkModel(450, 2)
                            X_train, y_train = nn._preprocess_data(day_pricelist)
                            nn.fit(X_train, y_train, 64, 10)
                            nn.save(ticker)

                    self.back_open = False
                    time.sleep(60)
                    continue

                self.back_open = True
                batches = utils.batch(CONFIG.TRADE_TICKERS, 1900)
                for batch in batches:
                    prices = self._get_realtime_prices(batch)
                    for ticker, price in prices.items():
                        self._buy_manager(ticker, price)
                time.sleep(30)
        except KeyboardInterrupt:
            os._exit(0)

    def start_sells(self):
        try:
            while True:
                if not self.market_is_open():
                    time.sleep(60)
                    continue

                batches = utils.batch(CONFIG.TRADE_TICKERS, 1900)
                for batch in batches:
                    prices = self._get_realtime_prices(batch)
                    for ticker, price in prices.items():
                        self._sell_manager(ticker, price)
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
