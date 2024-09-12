import os
import django
from authuser.models import User, List, Stock
import yfinance as yf

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

# Initialize Django
django.setup()

stocks = ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
key_list = ['open', 'high', 'low', 'close', 'volume']

def insert_data(stock_list, key_list, period='1y'):
    for stock in stock_list:
        hist = yf.Ticker(stock).history(period=period)
        for i in range(len(hist)):
            stock_data = {}
            for key in key_list:
                stock_data['date'] = hist.index[i]
                stock_data[key] = hist[key.capitalize()].iloc[i]
            Stock.objects._import_stock(
                stock,
                stock_data['date'],
                stock_data['open'],
                stock_data['high'],
                stock_data['low'],
                stock_data['volume'],
                0, 0, 0
            )

# Call the function to insert data
insert_data(stocks, key_list)

User.objects.create(
    email = '1234@django.com',
    password = 'rogen42069',
    name = 'Jacky',
)
