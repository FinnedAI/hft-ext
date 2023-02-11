import os
from alpaca.trading.client import TradingClient
import config as CONFIG

api = TradingClient(
    CONFIG.ALPACA_PUBLIC_KEY, CONFIG.ALPACA_SECRET_KEY, paper=CONFIG.PAPER
)


class CliHandler:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"

    def buy_msg(self, ticker, value, qty):
        print(f"{self.GREEN} -> BUY {ticker} ({value} x {qty}){self.END}")

    def sell_msg(self, ticker, value, qty, direction):
        print(f"{self.RED} -> SELL [{direction}] {ticker} ({value} x {qty}){self.END}")

    def custom_msg(self, color, message):
        color = getattr(self, color.upper(), self.END)
        print(f"{color}{message}{self.END}")

    def print_startup(self):
        account = api.get_account()

        self.custom_msg("blue", "Connected to Alpaca.")
        self.custom_msg("blue", f"Account ID: {account.id}")
        self.custom_msg("blue", f"Buying power: {account.buying_power}")
        self.custom_msg(
            "blue",
            f"Change since last run: {float(account.equity) - float(account.last_equity)}",
        )

        print("\n>> Enter 'exit' at any time to exit the program.\n")

        if account.trading_blocked:
            self.custom_msg("red", "Trading is blocked on this account.")
            os._exit(1)
