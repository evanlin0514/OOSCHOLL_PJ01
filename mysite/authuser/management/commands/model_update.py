import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from authuser.models import Stock
from django.core.management.base import BaseCommand
from decimal import Decimal
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import pickle
import os



class Command(BaseCommand):
    help = 'Updates the model for new data.'

    def handle(self, *args, **kwargs):
        data_dir = 'C:/Users/Evan/Desktop/code/final_project/mysite/data'
        stocks = Stock.objects.values_list('ticker', flat=True)
        scaler = MinMaxScaler()
        for stock in stocks:
            if not os.path.exists(os.path.join(data_dir, f'{stock}_prepared.pkl')):
                data = yf.Ticker(stock).history(start=dt.datetime.now() - dt.timedelta(days=15), end=dt.datetime.now())
                x_origin = data.loc[:,['Open']]
                y_origin = data.loc[:,['Close']]
                
                self.store_data(x_origin, y_origin, stock, data_dir)
                x_origin, y_origin = self.load_data(stock, data_dir)

                scaler.fit(x_origin)
                X = scaler.fit_transform(x_origin)
                scaler.fit(y_origin)
                y = scaler.fit_transform(y_origin)
                model = self.make_model(X) 
                model.fit(X, y, epochs=100,shuffle=False)
                self.save_model(model, stock, data_dir)
            else:
                model = self.load_model(stock, data_dir)   
                five_d = self.predict_nd(stock, model, 5)
                ten_d = self.predict_nd(stock, model, 10)
                fivteen_d = self.predict_nd(stock, model, 15)
                Stock.objects.filter(ticker=stock).update(d5=five_d, d10=ten_d, d15=fivteen_d)



    def store_data(self, X, y, stock, data_dir):
        prepared_file = os.path.join(data_dir, f'{stock}_prepared.pkl')
        pickle.dump((X, y), open(prepared_file, 'wb'))
        self.stdout.write(self.style.SUCCESS(f'Successfully stored {stock} data'))

    def load_data(self, stock, data_dir):
        prepared_file = os.path.join(data_dir, f'{stock}_prepared.pkl')
        return pickle.load(open(prepared_file, 'rb'))

    def make_model(self, X):
        model = Sequential()
        model.add(LSTM(256,input_shape=(X.shape[1],1), return_sequences=False))
        model.add(Dense(1))
        model.compile(optimizer='adam',loss='mse')
        return model
    
    def save_model(self, model, stock, data_dir):
        model_file = os.path.join(data_dir, f'{stock}_model.h5')
        pickle.dump(model, open(model_file, 'wb'))
        self.stdout.write(self.style.SUCCESS(f'Successfully stored {stock} model'))

    def load_model(self, stock, data_dir):
        model_file = os.path.join(data_dir, f'{stock}_model.h5')
        return pickle.load(open(model_file, 'rb'))

    def predict_nd(self, stock, model, n):
        scaler = MinMaxScaler()
        data = []
        a = yf.Ticker(stock).history(period='1d').loc[:, ['Close']]
        scaler.fit(a)
        data.append(scaler.transform(a))
        for i in range(n-1):
            pred = model.predict(data[i])
            data.append(pred)
        result = scaler.inverse_transform(data[-1])
        rounded_result = np.round(result, decimals=2)
        return Decimal(str(rounded_result[0][0]))




