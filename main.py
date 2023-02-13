from scripts.trader import StockTraderRunner
from threading import Thread
from scripts.gui import start_gui

if __name__ == "__main__":
    runner = StockTraderRunner()
    Thread(target=runner.run).start()
    start_gui()
