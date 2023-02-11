from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import numpy as np
import urllib3
import json
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense
import sqlite3

http = urllib3.PoolManager()


class Strategy:
    def __init__(self, modelname):
        if modelname == "arima":
            self.model = ArimaModel()
        elif modelname == "nn":
            self.model = NeuralNetworkModel()

    def get_live_prices(self, ticker):
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&symbols={'%2c'.join(tickers)}&corsDomain=finance.yahoo.com"
        response = http.request("GET", url)
        data = json.loads(response.data)
        formatted = []
        for ticker in data["quoteResponse"]["result"]:
            try:
                ticker, price = ticker["symbol"], ticker["regularMarketPrice"]["raw"]
                formatted.append((ticker, price))
            except:
                return None
        return formatted

    def cleaner(self, x):
        return pd.DataFrame({"price": x})

    def should_buy(self, ticker, pricelist):
        cleaned = self.cleaner(pricelist)
        # if model is nn, then we need to load the model weights
        if self.modelname == "nn":
            self.model.load_weights(f"data/weights/{ticker}.h5")")
        return self.model._should_buy(cleaned)

    def should_sell(self, ticker, buy_amt, current_amt, pricelist):
        cleaned = self.cleaner(pricelist)
        # if model is nn, then we need to load the model weights
        if self.modelname == "nn":
            self.model.load_weights(f"data/weights/{ticker}.h5")")
        return self.model._should_sell(buy_amt, current_amt, cleaned)


"""
Simplest model possible, just predicts the percent chance
that the price will increase or decrease in the next period.
"""


class ArimaModel:
    def __init__(self):
        self.prob_increase = None
        self.prob_decrease = None

    def predict_prob_change(self, data):
        model = ARIMA(data, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast()[0][0]
        self.prob_increase = np.where(forecast > data[-1], 1, 0)
        self.prob_decrease = np.where(forecast < data[-1], 1, 0)

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


class NeuralNetworkModel:
    def __init__(self, input_shape, num_classes):
        self.model = Sequential()
        self.model.add(Dense(64, activation="relu", input_shape=(input_shape,)))
        self.model.add(Dense(64, activation="relu"))
        self.model.add(Dense(num_classes, activation="softmax"))
        self.model.compile(
            loss=keras.losses.categorical_crossentropy,
            optimizer=keras.optimizers.Adam(),
            metrics=["accuracy"],
        )

    def _preprocess_data(self, pricelist):
        # Transform the pricelist into a suitable format for the model
        X = []
        y = []
        for i in range(len(pricelist) - 1):
            X.append(pricelist[i])
            if pricelist[i + 1] > pricelist[i]:
                y.append([1, 0])
            else:
                y.append([0, 1])
        X = np.array(X)
        y = np.array(y)

        # Normalize the data
        X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        return X_train, y_train

    def fit(self, X_train, y_train, batch_size, epochs, validation_data=None):
        self.model.fit(
            X_train,
            y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=validation_data,
        )

    def predict(self, X_test):
        return self.model.predict(X_test)

    def save_weights(self, file_path):
        self.model.save_weights(file_path)

    def load_weights(self, file_path):
        self.model.load_weights(file_path)

    def _should_buy(self, pricelist):
        X_test = np.array(pricelist)
        predictions = self.predict(X_test)
        self.prob_increase = predictions[0][0]
        self.prob_decrease = predictions[0][1]
        if self.prob_increase > self.prob_decrease:
            return True
        return False

    def _should_sell(self, buy_amt, current_amt, pricelist):
        X_test = np.array(pricelist)
        predictions = self.predict(X_test)
        self.prob_increase = predictions[0][0]
        self.prob_decrease = predictions[0][1]
        if current_amt <= buy_amt and self.prob_decrease > self.prob_increase:
            return True
        if current_amt >= buy_amt and self.prob_increase > self.prob_decrease:
            return False
        if current_amt > buy_amt and self.prob_decrease >= self.prob_increase:
            return True
