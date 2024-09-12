from django.core.management.base import BaseCommand
from authuser.models import Stock
import yfinance as yf
from datetime import date

class Command(BaseCommand):
    help = 'Updates stock data for all stocks in the database'

    def handle(self, *args, **options):
        today = date.today()
        stocks = Stock.objects.all()

        for stock in stocks:
            try:
                # Fetch the latest data
                yf_stock = yf.Ticker(stock.ticker)
                latest_data = yf_stock.history(period="1d").iloc[0]

                # Update the stock
                stock.date = today
                stock.open = latest_data['Open']
                stock.high = latest_data['High']
                stock.low = latest_data['Low']
                stock.close = latest_data['Close']
                stock.volume = latest_data['Volume']
                stock.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully updated {stock.ticker}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to update {stock.ticker}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Stock update completed'))
