from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import urllib3
import json
import warnings

http = urllib3.PoolManager()
STRATEGY_REGISTRY = {}

class Strategy:
    def __init__(self, strategy):
        if not isinstance(strategy, Strategy):
            raise ValueError("Invalid strategy")
        self.model = strategy

    def get_live_prices(self, batches):
        formatted = []
        for batch in batches:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={'%2c'.join(batch)}&corsDomain=finance.yahoo.com"
            response = http.request("GET", url)
            data = json.loads(response.data)
            for ticker in data["quoteResponse"]["result"]:
                try:
                    ticker, price = (
                        ticker["symbol"],
                        ticker["regularMarketPrice"]["raw"],
                    )
                    formatted.append((ticker, price))
                except:
                    return None
        return formatted

    def cleaner(self, x):
        return pd.DataFrame({"price": x})

    def should_buy(self, ticker, pricelist):
        cleaned = self.cleaner(pricelist)
        return self.model._should_buy(cleaned)

    def should_sell(self, ticker, buy_amt, current_amt, pricelist):
        cleaned = self.cleaner(pricelist)
        return self.model._should_sell(buy_amt, current_amt, cleaned)


def register_strategy(name):
    def decorator(cls):
        STRATEGY_REGISTRY[name] = cls
        return cls

    return decorator

"""
Simplest model possible, just predicts the percent chance
that the price will increase or decrease in the next period.
"""
class ArimaModel(Strategy):
    def __init__(self):
        self.prob_increase = None
        self.prob_decrease = None

    def predict_prob_change(self, data):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ARIMA(data, order=(1, 1, 1))
            model_fit = model.fit()
            prediction = model_fit.get_forecast(steps=1)
            conf_int = prediction.conf_int()
            conf_int = conf_int.values.tolist()[0]

        data = data.values.tolist()
        if conf_int[0] > data[-1]:
            self.prob_increase = (conf_int[1] - data[-1]) / (conf_int[1] - conf_int[0])
            self.prob_decrease = 1 - self.prob_increase
        else:
            self.prob_decrease = (data[-1] - conf_int[0]) / (conf_int[1] - conf_int[0])
            self.prob_increase = 1 - self.prob_decrease

    def _should_buy(self, pricelist):
        self.predict_prob_change(pricelist["price"])
        return self.prob_increase > 0.5

    def _should_sell(self, buy_amt, current_amt, pricelist):
        self.predict_prob_change(pricelist["price"])
        if current_amt <= buy_amt and self.prob_decrease > 0.5:
            return True
        if current_amt >= buy_amt and self.prob_increase > 0.5:
            return False
        if current_amt > buy_amt and self.prob_decrease >= 0.5:
            return True


strategy = Strategy(ArimaModel())