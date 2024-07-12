from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.models.requests import StockTransactionRequest
from app.api.models.responses import StockTransactionResponse, format_transaction_response
from app.config.logging_config import setup_logging
from app.api.models.entities import StockTransaction
from app.infra.db import create_session

logger = setup_logging()

router = APIRouter()


# Dependency to get the database session
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


def create_single_stock_transaction(db: Session, stock_transaction_data: StockTransactionRequest):
    """
    Processes stock transaction data, creates a new StockTransaction instance,
    adds it to the database, commits the transaction, refreshes the instance, and returns it.
    """
    ticker_symbol_with_suffix = stock_transaction_data.ticker_symbol.upper() + \
        stock_transaction_data.ticker_suffix.upper()

    stock_transaction_dict = stock_transaction_data.dict()
    stock_transaction_dict['ticker_symbol'] = ticker_symbol_with_suffix
    del stock_transaction_dict['ticker_suffix']

    stock_transaction = StockTransaction(**stock_transaction_dict)
    db.add(stock_transaction)
    db.commit()
    db.refresh(stock_transaction)
    return stock_transaction


@router.post("/", response_model=List[StockTransactionResponse])
def create_stock_transactions(stock_transactions_data: List[StockTransactionRequest], db: Session = Depends(get_db)):
    """
    Endpoint to create multiple stock transactions.

    Returns a list of StockTransactionResponse objects.
    """
    transactions = []
    try:
        for transaction_data in stock_transactions_data:
            transaction = create_single_stock_transaction(db, transaction_data)
            response_transaction = format_transaction_response(transaction)
            transactions.append(response_transaction)
    except Exception as e:
        logger.error(f"Failed to create stock transactions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to process stock transactions")

    return transactions


@router.get("/{stock_transaction_id}", response_model=StockTransactionResponse)
def read_stock_transaction(stock_transaction_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to read a single stock transaction by its ID.

    Returns a StockTransactionResponse object.
    """
    stock_transaction = db.query(StockTransaction).filter(
        StockTransaction.id == stock_transaction_id).first()
    if stock_transaction is None:
        raise HTTPException(
            status_code=404, detail="Stock transaction not found")
    return format_transaction_response(stock_transaction)


@router.get("/", response_model=List[StockTransactionResponse])
def list_stock_transactions(
    db: Session = Depends(get_db),
    page: int = Query(1, description="Page number", gt=0),
    per_page: int = Query(
        10, description="Transactions per page", gt=0, le=100),
    sort_by: str = Query("transaction_date", description="Field to sort by",
                         regex=r"^(id|ticker_symbol|transaction_type|quantity|price_per_unit|transaction_date)$"),
    order: str = Query("asc", description="Sort order", regex=r"^(asc|desc)$"),
):
    """
    Endpoint to list stock transactions with pagination and sorting.

    Returns a list of StockTransactionResponse objects.
    """
    try:
        # Determine sort order
        if order == "asc":
            sort_order = StockTransaction.__dict__[sort_by].asc()
        else:
            sort_order = StockTransaction.__dict__[sort_by].desc()

        # Query for stock transactions with pagination and sorting
        stock_transactions = (
            db.query(StockTransaction)
            .order_by(sort_order)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        # Format each transaction for the response
        transactions = [
            format_transaction_response(transaction)
            for transaction in stock_transactions
        ]

        return transactions

    except Exception as e:
        logger.error(f"Failed to list stock transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stock transactions"
        )


@router.put("/{stock_transaction_id}", response_model=StockTransactionResponse)
def update_stock_transaction(stock_transaction_id: int, stock_transaction_data: dict, db: Session = Depends(get_db)):
    """
    Endpoint to update a stock transaction by its ID.

    Returns the updated StockTransactionResponse object.
    """
    stock_transaction = db.query(StockTransaction).filter(
        StockTransaction.id == stock_transaction_id).first()
    if stock_transaction is None:
        raise HTTPException(
            status_code=404, detail="Stock transaction not found")
    for key, value in stock_transaction_data.items():
        setattr(stock_transaction, key, value)
    db.commit()
    db.refresh(stock_transaction)
    return format_transaction_response(stock_transaction)


@router.delete("/{stock_transaction_id}", response_model=dict)
def delete_stock_transaction(stock_transaction_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete a stock transaction by its ID.

    Returns a message confirming the deletion.
    """
    stock_transaction = db.query(StockTransaction).filter(
        StockTransaction.id == stock_transaction_id).first()
    if stock_transaction is None:
        raise HTTPException(
            status_code=404, detail="Stock transaction not found")
    db.delete(stock_transaction)
    db.commit()
    return {"message": "Stock transaction deleted successfully"}

