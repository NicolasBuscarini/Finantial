from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.models.requests import StockTransactionRequest
from app.api.models.responses import StockTransactionResponse
from app.config.logging_config import setup_logging
from app.infra.db.mysql_conector import create_session
from app.api.services.stock_transaction_service import StockTransactionService

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


@router.post("/", response_model=List[StockTransactionResponse])
def create_stock_transactions(
        stock_transactions_data: List[StockTransactionRequest], db: Session = Depends(get_db)):
    """
    Endpoint to create multiple stock transactions.

    Returns a list of StockTransactionResponse objects.
    """
    service = StockTransactionService(db)
    try:
        return service.create_stock_transactions(stock_transactions_data)
    except Exception as e:
        logger.error(f"Failed to create stock transactions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to process stock transactions")


@router.get("/{stock_transaction_id}", response_model=StockTransactionResponse)
def read_stock_transaction(stock_transaction_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to read a single stock transaction by its ID.

    Returns a StockTransactionResponse object.
    """
    service = StockTransactionService(db)
    try:
        return service.read_stock_transaction(stock_transaction_id)
    except Exception as e:
        logger.error(f"Failed to read stock transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stock transaction")


@router.get("/", response_model=List[StockTransactionResponse])
def list_stock_transactions(
    db: Session = Depends(get_db),
    page: int = Query(1, description="Page number", gt=0),
    per_page: int = Query(10, description="Transactions per page", gt=0, le=100),
    sort_by: str = Query(
        "transaction_date",
        description="Field to sort by",
        regex=r"^(id|ticker_symbol|transaction_type|quantity|price_per_unit|transaction_date)$"),
    order: str = Query("asc", description="Sort order", regex=r"^(asc|desc)$"),
):
    """
    Endpoint to list stock transactions with pagination and sorting.

    Returns a list of StockTransactionResponse objects.
    """
    service = StockTransactionService(db)
    try:
        return service.list_stock_transactions(page, per_page, sort_by, order)
    except Exception as e:
        logger.error(f"Failed to list stock transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stock transactions")


@router.put("/{stock_transaction_id}", response_model=StockTransactionResponse)
def update_stock_transaction(stock_transaction_id: int,
                             stock_transaction_data: dict, db: Session = Depends(get_db)):
    """
    Endpoint to update a stock transaction by its ID.

    Returns the updated StockTransactionResponse object.
    """
    service = StockTransactionService(db)
    try:
        return service.update_stock_transaction(stock_transaction_id, stock_transaction_data)
    except Exception as e:
        logger.error(f"Failed to update stock transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update stock transaction")


@router.delete("/{stock_transaction_id}", response_model=dict)
def delete_stock_transaction(stock_transaction_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete a stock transaction by its ID.

    Returns a message confirming the deletion.
    """
    service = StockTransactionService(db)
    try:
        return service.delete_stock_transaction(stock_transaction_id)
    except Exception as e:
        logger.error(f"Failed to delete stock transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete stock transaction")
