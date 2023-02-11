from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import numpy as np


class Strategy:
    def __init__(self):
        self.prob_increase = None
        self.prob_decrease = None

    def cleaner(self, x):
        return pd.DataFrame({"price": x})

    def predict_prob_change(self, data):
        model = ARIMA(data, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast()[0][0]
        self.prob_increase = np.where(forecast > data[-1], 1, 0)
        self.prob_decrease = np.where(forecast < data[-1], 1, 0)

    def should_buy(self, pricelist):
        df = self.cleaner(pricelist)
        self.predict_prob_change(df["price"])
        return self.prob_increase > 0.5

    def should_sell(self, buy_amt, pricelist):
        current_amt = pricelist[-1]
        df = self.cleaner(pricelist)
        self.predict_prob_change(df["price"])
        if current_amt <= buy_amt and self.prob_decrease > 0.5:
            return True
        if current_amt >= buy_amt and self.prob_increase > 0.5:
            return False
        if current_amt > buy_amt and self.prob_decrease >= 0.5:
            return True
