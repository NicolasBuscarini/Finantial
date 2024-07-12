from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.api.models.requests import StockTransactionRequest
from app.api.models.responses import StockTransactionResponse, format_transaction_response
from app.api.models.entities import StockTransaction


class StockTransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_stock_transaction(self, stock_transaction_data: StockTransactionRequest) -> StockTransactionResponse:
        ticker_symbol_with_suffix = stock_transaction_data.ticker_symbol.upper() + \
            stock_transaction_data.ticker_suffix.upper()

        stock_transaction_dict = stock_transaction_data.dict()
        stock_transaction_dict['ticker_symbol'] = ticker_symbol_with_suffix
        del stock_transaction_dict['ticker_suffix']

        stock_transaction = StockTransaction(**stock_transaction_dict)
        self.db.add(stock_transaction)
        self.db.commit()
        self.db.refresh(stock_transaction)
        return format_transaction_response(stock_transaction)

    def create_stock_transactions(self, stock_transactions_data: List[StockTransactionRequest]) -> List[StockTransactionResponse]:
        transactions = []
        for transaction_data in stock_transactions_data:
            transaction = self.create_stock_transaction(transaction_data)
            transactions.append(transaction)
        return transactions

    def read_stock_transaction(self, stock_transaction_id: int) -> StockTransactionResponse:
        stock_transaction = self.db.query(StockTransaction).filter(
            StockTransaction.id == stock_transaction_id).first()
        if stock_transaction is None:
            raise HTTPException(
                status_code=404, detail="Stock transaction not found")
        return format_transaction_response(stock_transaction)

    def read_stock_transactions_by_symbol(self, ticker_symbol: str) -> List[StockTransaction]:
        """
        Reads all stock transactions for a given ticker symbol.

        :param ticker_symbol: The ticker symbol of the stock transactions to retrieve.
        :return: A list of StockTransaction objects.
        """
        stock_transactions = self.db.query(StockTransaction).filter(
            StockTransaction.ticker_symbol == ticker_symbol).all()
        if not stock_transactions:
            raise HTTPException(
                status_code=404, detail=f"No stock transactions found for symbol {ticker_symbol}")
        return stock_transactions

    def list_stock_transactions(self, page: int, per_page: int, sort_by: str, order: str) -> List[StockTransactionResponse]:
        # Determine sort order
        if order == "asc":
            sort_order = StockTransaction.__dict__[sort_by].asc()
        else:
            sort_order = StockTransaction.__dict__[sort_by].desc()

        # Query for stock transactions with pagination and sorting
        stock_transactions = (
            self.db.query(StockTransaction)
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

    def update_stock_transaction(self, stock_transaction_id: int, stock_transaction_data: Dict) -> StockTransactionResponse:
        stock_transaction = self.db.query(StockTransaction).filter(
            StockTransaction.id == stock_transaction_id).first()
        if stock_transaction is None:
            raise HTTPException(
                status_code=404, detail="Stock transaction not found")
        for key, value in stock_transaction_data.items():
            setattr(stock_transaction, key, value)
        self.db.commit()
        self.db.refresh(stock_transaction)
        return format_transaction_response(stock_transaction)

    def delete_stock_transaction(self, stock_transaction_id: int) -> Dict:
        stock_transaction = self.db.query(StockTransaction).filter(
            StockTransaction.id == stock_transaction_id).first()
        if stock_transaction is None:
            raise HTTPException(
                status_code=404, detail="Stock transaction not found")
        self.db.delete(stock_transaction)
        self.db.commit()
        return {"message": "Stock transaction deleted successfully"}
