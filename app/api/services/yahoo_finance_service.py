from decimal import Decimal
import yfinance as yf

class YahooFinanceService:
    def get_ticker_info(self, ticker_symbol: str):
        return yf.Ticker(ticker_symbol)

    def get_currency_code(self, ticker) -> str :
        return str(ticker.basic_info.get('currency'))

    def get_history(self, ticker, start_date):
        return ticker.history(start=start_date)

    def get_current_price(self, ticker) -> Decimal:
        return Decimal(str(ticker.basic_info.get('last_price')))

    def calculate_dividends_paid(self, quantity: int, history):
        dividends_paid = (history['Dividends'] * quantity).sum()
        return Decimal(str(dividends_paid))

    def calculate_highest_price(self, history):
        highest_price = history['High'].max()
        return Decimal(str(highest_price))

    def calculate_lowest_price(self, history):
        lowest_price = history['Low'].min()
        return Decimal(str(lowest_price))

    def calculate_average_price(self, history):
        average_price = history['Close'].mean()
        return Decimal(str(average_price))
