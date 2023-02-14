import config as CONFIG
import os
import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import urllib3
from scripts.strategy import strategy
from threading import Thread
import time
from utils.utils import Utils, Storage
from utils.notifier import Notifier

http = urllib3.PoolManager()
notify = Notifier()
utils = Utils()
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
        self.filled = False

    def all(self):
        positions = account.list_positions()
        for position in positions:
            self.portfolio[position.symbol] = {
                "qty": float(position.qty),
                "price": float(position.avg_entry_price),
            }

        notify.new_portfolio(self.portfolio)

    def get(self, ticker):
        if not self.filled:
            self.all()
            self.filled = True
        
        return self.portfolio[ticker]["price"], self.portfolio[ticker]["qty"]

    def cached(self):
        if not self.filled:
            self.all()
            self.filled = True
        
        return self.portfolio

    def exists(self, ticker):
        return ticker in self.cached().keys()

    def add(self, ticker, qty, price):
        order_data = self._create_market_order(ticker, qty, OrderSide.BUY)
        self._submit_order(order_data)
        self.portfolio[ticker] = {"qty": qty, "price": price}
        notify.new_portfolio(self.cached())

    def remove(self, ticker):
        qty = self.portfolio[ticker]["qty"]
        order_data = self._create_market_order(ticker, qty, OrderSide.SELL)
        self._submit_order(order_data)
        del self.portfolio[ticker]
        notify.new_portfolio(self.cached())

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


class StockTrader:
    def __init__(self):
        self.account = api.get_account()
        self.market_is_open = lambda: api.get_clock().is_open
        self.back_open = False

    def _get_realtime_prices(self, tickers, thread):
        tickers = utils.batch(CONFIG.TRADE_TICKERS, 1900)
        prices = strategy.get_live_prices(tickers)
        for ticker, price in prices:
            # sqlite can only handle one thread at a time
            if thread == "buy":
                self.buy_storage.save_data(ticker, price)
            elif thread == "sell":
                self.sell_storage.save_data(ticker, price)

        time.sleep(CONFIG.ALPACA_TIMEOUT)
        return prices

    def _buy_manager(self, ticker, price):
        # don't buy if we can't afford it or we already own it
        # we don't want to buy if we already own it because we
        # don't want to concentrate our money in one stock
        if float(self.account.buying_power) < price or portfolio.exists(ticker):
            return

        pricelist = self.buy_storage.retrieve_data(ticker)
        # 450 is the number of minutes in a trading day
        day_pricelist = pricelist[-450:] if len(pricelist) >= 450 else pricelist
        day_pricelist = [item[0] for item in day_pricelist]
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
            notify.new_action(f" -> Buy {ticker} ({price} x {qty})")
            self.buy_storage.save_data(ticker, price)
        except:
            notify.new_action(f" -> Error buying {ticker}")
            pass
        time.sleep(CONFIG.ALPACA_TIMEOUT)

    def _sell_manager(self, ticker, price):
        if not portfolio.exists(ticker):
            return

        try:
            buy_amt, qty = portfolio.get(ticker)
        except:
            notify.new_action(f" -> Error getting {ticker} from portfolio")
            return

        pricelist = self.sell_storage.retrieve_data(ticker)
        # 450 is the number of minutes in a trading day
        day_pricelist = pricelist[-450:] if len(pricelist) >= 450 else pricelist
        day_pricelist = [item[0] for item in day_pricelist]
        should_sell = strategy.should_sell(ticker, buy_amt, price, day_pricelist)
        if should_sell:
            portfolio.remove(ticker)
            notify.new_action(f" -> Sell {ticker} (BUY:{price} x {qty})")
        time.sleep(CONFIG.ALPACA_TIMEOUT)

    def start_buys(self):
        try:
            self.buy_storage = Storage()
            self.buy_storage.create_table()
            while True:
                if not self.market_is_open():
                    if self.back_open:
                        notify.new_action(" -> Error: Market is closed")

                    self.back_open = False
                    time.sleep(60)
                    continue

                self.back_open = True
                batches = utils.batch(CONFIG.TRADE_TICKERS, 1900)
                for batch in batches:
                    prices = self._get_realtime_prices(batch, "buy")
                    for ticker, price in prices:
                        self._buy_manager(ticker, price)
                time.sleep(30)
        except KeyboardInterrupt:
            os._exit(0)

    def start_sells(self):
        try:
            self.sell_storage = Storage()
            self.sell_storage.create_table()
            while True:
                if not self.market_is_open():
                    time.sleep(60)
                    continue

                batches = utils.batch(CONFIG.TRADE_TICKERS, 1900)
                for batch in batches:
                    prices = self._get_realtime_prices(batch, "sell")
                    for ticker, price in prices:
                        self._sell_manager(ticker, price)
                time.sleep(30)
        except KeyboardInterrupt:
            os._exit(0)


class StockTraderRunner:
    def __init__(self):
        self.trader = StockTrader()

    def run(self):
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
