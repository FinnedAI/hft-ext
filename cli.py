import asyncio
from alpaca.trading.client import TradingClient
import config as CONFIG

api = TradingClient(CONFIG.ALPACA_PUBLIC_KEY, CONFIG.ALPACA_SECRET_KEY, paper=CONFIG.PAPER)

class colors:
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    blue = '\033[94m'
    end = '\033[0m'

class CliHandler:
    def buy_msg(self, ticker, value, qty):
        print(f"{colors.green} -> BUY {ticker} ({value} x {qty}){colors.end}")

    def sell_msg(self, ticker, value, qty):
        print(f"{colors.red} -> SELL {ticker} ({value} x {qty}){colors.end}")

    def custom_msg(self, color, msg):
        print(f"{colors.__dict__[color]}{msg}{colors.end}")

    def print_startup(self):
        account = api.get_account()
        print(f"{colors.blue}Connected to Alpaca.{colors.end}")
        print(f"{colors.blue}Account ID: {account.id}{colors.end}")
        print(f"{colors.blue}Buying power: {account.buying_power}{colors.end}")
        print(f"{colors.blue}Change since last run: {float(account.equity) - float(account.last_equity)}{colors.end}")

        print("\n>> Enter 'exit' at any time to exit the program.\n")

        if account.trading_blocked:
            print(f"{colors.red}Trading is blocked on this account.{colors.end}")
            os._exit(1)
        
