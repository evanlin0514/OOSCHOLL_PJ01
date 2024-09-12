from django.core.management.base import BaseCommand
from authuser.models import Stock
import yfinance as yf
from datetime import date

class Command(BaseCommand):
    help = 'Populates the database with initial stock data'

    def handle(self, *args, **options):
        # List of stock tickers you want to add
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB']  # Add more as needed

        for ticker in tickers:
            try:
                # Fetch the latest data
                yf_stock = yf.Ticker(ticker)
                latest_data = yf_stock.history(period="1d").iloc[0]

                # Create the stock object
                stock, created = Stock.objects.update_or_create(
                    ticker=ticker,
                    defaults={
                        'date': date.today(),
                        'open': latest_data['Open'],
                        'high': latest_data['High'],
                        'low': latest_data['Low'],
                        'close': latest_data['Close'],
                        'volume': latest_data['Volume']
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully added {ticker}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated {ticker}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to add/update {ticker}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Stock population completed'))