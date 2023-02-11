from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import numpy as np


class Strategy:
    def cleaner(self, x):
        return pd.DataFrame({"price": x})

    def predict_prob_change(data):
        # determine and return the probability of
        # the price increasing or decreasing
        model = ARIMA(data, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast()[0][0]
        prob_increase = np.where(forecast > data[-1], 1, 0)
        prob_decrease = np.where(forecast < data[-1], 1, 0)
        return prob_increase, prob_decrease

    def should_buy(self, pricelist):
        df = self.cleaner(pricelist)
        prob_increase, prob_decrease = self.predict_prob_change(df["price"])
        return prob_increase > 0.5

    def should_sell(self, buy_amt, pricelist):
        current_amt = pricelist[-1]
        df = self.cleaner(pricelist)
        prob_increase, prob_decrease = self.predict_prob_change(df["price"])
        if current_amt <= buy_amt and prob_decrease > 0.5:
            return True
        if current_amt >= buy_amt and prob_increase > 0.5:
            return False  # hold until price increases
        if current_amt > buy_amt and prob_decrease >= 0.5:
            return True
