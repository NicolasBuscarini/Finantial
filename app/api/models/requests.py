from pydantic import BaseModel


# This class represents a stock transaction request.
class StockTransactionRequest(BaseModel):
    ticker_symbol: str
    transaction_type: str
    ticker_suffix: str
    quantity: int
    price_per_unit: float
    transaction_date: str
