from scripts.trader import StockTraderRunner
from threading import Thread
from scripts.gui import start_gui
import os

if __name__ == "__main__":
    try:
        runner = StockTraderRunner()
        Thread(target=runner.run).start()
        start_gui()
    except KeyboardInterrupt:
        os._exit(1)
