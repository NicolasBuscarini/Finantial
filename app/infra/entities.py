from sqlalchemy import Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Represents a credit card entity.


class CreditCard(Base):
    """
    Represents a credit card entity.

    Attributes:
        id (int): The unique identifier for the credit card.
        card_number (str): The 16-digit number of the credit card.
        card_holder_name (str): The name of the card holder.
        expiration_date (str): The expiration date of the credit card in the format 'MM/YY'.
        cvv (str): The 3-digit CVV code of the credit card.
        bill (decimal.Decimal): The current bill amount on the credit card.
        limit (decimal.Decimal): The credit limit of the card.
        due_date (datetime.date): The due date for the credit card payment.
    """

    __tablename__ = 'credit_cards'

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(16), unique=True, index=True, nullable=False)
    card_holder_name = Column(String(100), nullable=False)
    expiration_date = Column(String(5), nullable=False)
    cvv = Column(String(3), nullable=False)
    bill = Column(Numeric(10, 2), nullable=False, default=0)
    limit = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)


# Represents a stock transaction.
class StockTransaction(Base):
    """
    Represents a stock transaction.

    Attributes:
        id (int): The unique identifier of the transaction.
        ticker_symbol (str): The symbol of the stock being transacted.
        transaction_type (str): The type of transaction, either "BUY" or "SELL".
        quantity (int): The number of shares transacted.
        price_per_unit (decimal.Decimal): The price per share.
        transaction_date (datetime.datetime): The date and time of the transaction.
    """
    __tablename__ = 'stock_transactions'

    id = Column(Integer, primary_key=True, index=True)
    ticker_symbol = Column(String(10), nullable=False)
    transaction_type = Column(String(4), nullable=False)  # "BUY" or "SELL"
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
