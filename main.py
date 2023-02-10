from trader import StockTraderRunner
import asyncio

if __name__ == "__main__":
    runner = StockTraderRunner()
    asyncio.run(runner.run())
