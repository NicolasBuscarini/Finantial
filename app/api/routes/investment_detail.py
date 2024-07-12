from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends, Query
from pandas import DataFrame
from sqlalchemy.orm import Session
from app.api.models.responses import InvestmentDetailResponse
from app.config.logging_config import setup_logging
from app.api.models.entities import StockTransaction
from app.infra.db import create_session
import yfinance as yf
from babel.numbers import format_currency

logger = setup_logging()

router = APIRouter()


def get_db():
    """
    The function `get_db` creates a database session and yields it, ensuring the session is closed after
    its use.
    """
    db = create_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/by_transaction_id", response_model=InvestmentDetailResponse)
def get_dividends_paid_by_transaction_id(stock_transaction_id: int = Query(..., description="Stock transaction ID"), db: Session = Depends(get_db)):
    """
    Endpoint to fetch historical stock data and calculate dividends paid by transaction ID.

    Returns historical stock data with a field 'dividends_paid' formatted in the currency specified by ticker.basic_info.currency.
    """

    # Retrieve stock transaction by ID
    stock_transaction = db.query(StockTransaction).filter(
        StockTransaction.id == stock_transaction_id).first()

    if stock_transaction is None:
        raise HTTPException(
            status_code=404, detail="Stock transaction not found")

    ticker = yf.Ticker(stock_transaction.ticker_symbol)
    currency_code = ticker.basic_info.get('currency')

    # Format transaction date to YYYY-MM-DD
    transaction_date_str = stock_transaction.transaction_date.strftime(
        "%Y-%m-%d")

    # Fetch historical data from Yahoo Finance
    history = ticker.history(start=transaction_date_str)

    response = InvestmentDetailResponse(
        ticker_symbol=stock_transaction.ticker_symbol.__str__(),
        current_price=Decimal(ticker.basic_info.last_price),
        dividends_paid=calculate_dividends_paid(stock_transaction, history),
        best_price_to_sold_since_buy=Decimal(str(calculate_highest_price(history))),
        best_price_to_buy_since_buy=Decimal(str(calculate_lowest_price(history))),
        average_price_since_buy=Decimal(str(calculate_average_price(history))),
        avarage_price_bought= Decimal(stock_transaction.price_per_unit.__str__()),
        price_variation=Decimal(ticker.basic_info.last_price) - Decimal(stock_transaction.price_per_unit.__str__()),
        profitability_total=Decimal(str(calculate_dividends_paid(stock_transaction, history) + ((Decimal(ticker.basic_info.last_price) - stock_transaction.price_per_unit) * stock_transaction.quantity))),
        profitability_stock=Decimal(str(((Decimal(ticker.basic_info.last_price) - stock_transaction.price_per_unit) * stock_transaction.quantity))),
        currency=currency_code
    )

    return response

@router.get("/by_symbol", response_model=InvestmentDetailResponse)
def get_dividends_paid_by_symbol(stock_transaction_symbol: str = Query(..., description="Stock transaction symbol"), db: Session = Depends(get_db)):
    """
    Endpoint to fetch historical stock data and calculate dividends paid by ticker symbol.

    Returns historical stock data with a field 'dividends_paid' formatted in the currency specified by ticker.basic_info.currency.
    """

    # Retrieve all stock transactions by ticker symbol
    stock_transactions = db.query(StockTransaction).filter(
        StockTransaction.ticker_symbol == stock_transaction_symbol).all()

    if not stock_transactions:
        raise HTTPException(
            status_code=404, detail=f"No stock transactions found for symbol {stock_transaction_symbol}")

    total_dividends_paid = Decimal(0)
    total_quantity = Decimal(0)
    total_cost = Decimal(0)

    # Get currency code from the first transaction's ticker
    first_transaction = stock_transactions[0]
    ticker = yf.Ticker(first_transaction.ticker_symbol)
    currency_code = ticker.basic_info.get('currency')

    # Calculate dividends paid for each transaction
    for stock_transaction in stock_transactions:
        dividends_paid = calculate_dividends_paid(stock_transaction, ticker.history(start=stock_transaction.transaction_date.strftime("%Y-%m-%d")))
        total_dividends_paid += dividends_paid
        total_quantity += stock_transaction.quantity
        total_cost += stock_transaction.quantity * stock_transaction.price_per_unit
        
    average_price_bought = total_cost / total_quantity

    response = InvestmentDetailResponse(
        ticker_symbol=stock_transaction_symbol,
        current_price=Decimal(ticker.basic_info.last_price),
        dividends_paid=Decimal(str(total_dividends_paid)),
        best_price_to_sold_since_buy=Decimal(str(calculate_highest_price(ticker.history()))),
        best_price_to_buy_since_buy=Decimal(str(calculate_lowest_price(ticker.history()))),
        average_price_since_buy=Decimal(str(calculate_average_price(ticker.history()))),
        avarage_price_bought= Decimal(str(average_price_bought)),
        price_variation=Decimal(ticker.basic_info.last_price) - Decimal(str(average_price_bought)),
        profitability_total=Decimal(str(total_dividends_paid + ((Decimal(ticker.basic_info.last_price) - average_price_bought) * total_quantity))),
        profitability_stock=Decimal(str(((Decimal(ticker.basic_info.last_price) - average_price_bought) * total_quantity))),
        currency=currency_code
    )

    return response

def calculate_dividends_paid(stock_transaction: StockTransaction, history):
    """
    This function calculates the total dividends paid for a given stock transaction based on historical
    dividend data.
    
    :param stock_transaction: StockTransaction object containing information about a stock transaction,
    such as the stock symbol, quantity, and price
    :type stock_transaction: StockTransaction
    :param history: The `history` parameter likely refers to a DataFrame or a similar data structure
    containing historical financial data for a stock. It seems to have a column named 'Dividends' that
    represents the dividends paid for each period
    :return: the total dividends paid for a specific stock transaction based on the quantity of stocks
    and historical dividend data. The result is converted to a Decimal type before being returned.
    """
    dividends_paid = (history['Dividends'] * stock_transaction.quantity).sum()
    return Decimal(str(dividends_paid))

def calculate_highest_price(history):
    """
    The function calculates the highest price from a given historical data.
    
    :param history: It looks like the `calculate_highest_price` function is designed to calculate the
    highest price from a given historical data set. The function takes a parameter `history`, which
    seems to be a DataFrame or a similar data structure containing a column named 'High' that represents
    the high prices
    :return: The function `calculate_highest_price` returns the highest price from the 'High' column in
    the provided history data as a Decimal value.
    """
    highest_price = history['High'].max()
    return Decimal(str(highest_price))

def calculate_lowest_price(history):
    """
    This Python function calculates the lowest price from a given historical data.
    
    :param history: It looks like the function `calculate_lowest_price` takes a parameter `history`,
    which is likely a DataFrame containing historical stock price data. The function calculates the
    lowest price from the 'Low' column in the DataFrame and returns it as a Decimal value
    :return: The function `calculate_lowest_price` returns the lowest price from the 'Low' column in the
    provided history data as a Decimal object.
    """
    lowest_price = history['Low'].min()
    return Decimal(str(lowest_price))

def calculate_average_price(history):
    """
    The function `calculate_average_price` calculates the average closing price from a given historical
    data.
    
    :param history: The `history` parameter is likely a DataFrame containing historical stock price
    data, with a column named 'Close' representing the closing prices of the stock on different dates.
    The function `calculate_average_price` calculates the average closing price from the 'Close' column
    and returns it as a Decimal value
    :return: The function `calculate_average_price` returns the average price calculated from the
    'Close' column of the input history data as a Decimal object.
    """
    average_price = history['Close'].mean()
    return Decimal(str(average_price))
