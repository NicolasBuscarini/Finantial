from decimal import Decimal
from pydantic import BaseModel, Field


# This class represents a response object for stock transactions.
class StockTransactionResponse(BaseModel):
    id: int
    ticker_symbol: str
    transaction_type: str
    quantity: int
    price_per_unit: Decimal
    transaction_date: str


def format_transaction_response(transaction):
    """
    Formats a SQLAlchemy transaction into the desired response.
    Converts transaction_date to a formatted string.
    """
    return StockTransactionResponse(
        id=transaction.id,
        ticker_symbol=transaction.ticker_symbol,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        price_per_unit=transaction.price_per_unit,
        transaction_date=transaction.transaction_date.strftime("%Y-%m-%d")
    )


class InvestmentDetailResponse(BaseModel):
    # In the provided code snippet, the line `ticker_symbol: str = Field(..., description="Ticker
    # symbol of the stock")` is defining a field `ticker_symbol` in the `StockDetailResponse` class
    # using Pydantic library.
    ticker_symbol: str = Field(
        ..., description="Ticker symbol of the stock")
    dividends_paid: Decimal = Field(
        ..., description="Total dividends paid")
    profitability_total: Decimal = Field(
        ..., description="Profitability total, including dividends and price variation")
    profitability_stock: Decimal = Field(
        ..., description="Profitability of the stock")
    price_variation: Decimal = Field(
        ..., description="Price variation of the stock")
    current_price: Decimal = Field(
        ..., description="Current price of the stock")
    best_price_to_sold_since_buy: Decimal = Field(
        ..., description="Best price to sell the stock since the first buy")
    best_price_to_buy_since_buy: Decimal = Field(
        ..., description="Best price to buy the stock since the first buy")
    average_price_since_buy: Decimal = Field(
        ..., description="Average price of the stock since the first buy")
    avarage_price_bought: Decimal = Field(
        ..., description="Average price of the stock bought")
    currency: str = Field(
        ..., description="Currency of the stock")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker_symbol": "IVVB11.SA",
                "dividends_paid": 0.0,
                "profitability_total": 0.0,
                "profitability_stock": 0.0,
                "price_variation": 0.0,
                "current_price": 0.0,
                "best_price_to_sold_since_buy": 0.0,
                "best_price_to_buy_since_buy": 0.0,
                "average_price_since_buy": 0.0,
                "avarage_price_bought": 0.0,
                "currency": "USD"
            }
        }
