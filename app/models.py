from sqlalchemy import Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CreditCard(Base):
    __tablename__ = 'credit_cards'

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(16), unique=True, index=True, nullable=False)
    card_holder_name = Column(String(100), nullable=False)
    expiration_date = Column(String(5), nullable=False)
    cvv = Column(String(3), nullable=False)
    bill = Column(Numeric(10, 2), nullable=False, default=0)
    limit = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)
