from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import yfinance as yf
from app.config.logging_config import setup_logging
from app.infra.db.mysql_conector import create_session
from app.infra.entities import StockTransaction
from sqlalchemy.orm import Session

logger = setup_logging()

router = APIRouter()

# Dependency to get the database session


def get_db():
    db = create_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/stock_info")
async def get_stock_info(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

    except KeyError:
        raise HTTPException(
            status_code=404, detail="Ticker information not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    return info


@router.get("hystory/{stock_transaction_id}", )
def get_rend(stock_transaction_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to read a single stock transaction by its ID.

    Returns a StockTransactionResponse object.
    """

    stock_transaction = db.query(StockTransaction).filter(
        StockTransaction.id == stock_transaction_id).first()

    if stock_transaction is None:
        raise HTTPException(
            status_code=404, detail="Stock transaction not found")
    else:
        transaction_date_str = stock_transaction.transaction_date.strftime(
            "%Y-%m-%d")
        transaction_symbol_str = stock_transaction.ticker_symbol.__str__()

    history = yf.Ticker(transaction_symbol_str).history(start=transaction_date_str)
    return history.to_dict()


@router.get("/ticker_symbols", response_model=List[str])
def get_unique_ticker_symbols(db: Session = Depends(get_db)):
    """
    Endpoint to fetch a list of unique ticker symbols registered in the database.

    Returns a list of unique ticker symbols.
    """
    try:
        ticker_symbols = db.query(StockTransaction.ticker_symbol).distinct().all()
        unique_ticker_symbols = [symbol[0] for symbol in ticker_symbols]
        return unique_ticker_symbols
    except Exception as e:
        logger.error(f"Failed to fetch unique ticker symbols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch unique ticker symbols"
        )
