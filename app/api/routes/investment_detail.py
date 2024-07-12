from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.api.models.responses import InvestmentDetailResponse
from app.config.logging_config import setup_logging
from app.infra.db.mysql_conector import get_db
from app.api.services.stock_transaction_service import StockTransactionService
from app.api.services.yahoo_finance_service import YahooFinanceService

logger = setup_logging()
router = APIRouter()


def get_investment_details(stock_transaction, yahoo_finance_service):
    ticker = yahoo_finance_service.get_ticker_info(
        stock_transaction.ticker_symbol)
    currency_code = yahoo_finance_service.get_currency_code(ticker)
    history = yahoo_finance_service.get_history(
        ticker, start_date=stock_transaction.transaction_date)

    dividends_paid = yahoo_finance_service.calculate_dividends_paid(
        stock_transaction.quantity, history)
    current_price = yahoo_finance_service.get_current_price(ticker)
    best_price_to_sold_since_buy = yahoo_finance_service.calculate_highest_price(
        history)
    best_price_to_buy_since_buy = yahoo_finance_service.calculate_lowest_price(
        history)
    average_price_since_buy = yahoo_finance_service.calculate_average_price(
        history)
    average_price_bought = stock_transaction.price_per_unit
    price_variation = current_price - average_price_bought
    profitability_total = dividends_paid + \
        (price_variation * stock_transaction.quantity)
    profitability_stock = price_variation * stock_transaction.quantity

    return InvestmentDetailResponse(
        ticker_symbol=stock_transaction.ticker_symbol,
        current_price=current_price,
        dividends_paid=dividends_paid,
        best_price_to_sold_since_buy=best_price_to_sold_since_buy,
        best_price_to_buy_since_buy=best_price_to_buy_since_buy,
        average_price_since_buy=average_price_since_buy,
        avarage_price_bought=average_price_bought,
        price_variation=price_variation,
        profitability_total=profitability_total,
        profitability_stock=profitability_stock,
        currency=currency_code
    )


@router.get("/by_transaction_id", response_model=InvestmentDetailResponse)
def get_dividends_paid_by_transaction_id(
        stock_transaction_id: int = Query(..., description="Stock transaction ID"), db: Session = Depends(get_db)):
    stock_transaction_service = StockTransactionService(db)
    yahoo_finance_service = YahooFinanceService()

    try:
        stock_transaction = stock_transaction_service.read_stock_transaction(
            stock_transaction_id)
        response = get_investment_details(
            stock_transaction, yahoo_finance_service)
        return response

    except Exception as e:
        logger.error(f"Failed to get dividends paid by transaction ID: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process request")


@router.get("/by_symbol", response_model=InvestmentDetailResponse)
def get_dividends_paid_by_symbol(stock_transaction_symbol: str = Query(...,
                                 description="Stock transaction symbol"), db: Session = Depends(get_db)):
    stock_transaction_service = StockTransactionService(db)
    yahoo_finance_service = YahooFinanceService()

    try:
        stock_transactions = stock_transaction_service.read_stock_transactions_by_symbol(
            stock_transaction_symbol)

        if not stock_transactions:
            raise HTTPException(
                status_code=404, detail=f"No stock transactions found for symbol {stock_transaction_symbol}")

        total_dividends_paid = Decimal(0)
        total_quantity: int = 0
        total_cost = Decimal(0)

        for stock_transaction in stock_transactions:
            history = yahoo_finance_service.get_history(yahoo_finance_service.get_ticker_info(
                stock_transaction_symbol), start_date=stock_transaction.transaction_date.__str__())
            quantity = int(str(stock_transaction.quantity))
            price_per_unit = stock_transaction.price_per_unit.real
            dividends_paid = yahoo_finance_service.calculate_dividends_paid(
                quantity, history)
            total_dividends_paid += dividends_paid
            total_quantity += quantity
            total_cost += quantity * price_per_unit

        average_price_bought = Decimal(total_cost / total_quantity)
        current_price = yahoo_finance_service.get_current_price(
            yahoo_finance_service.get_ticker_info(stock_transaction_symbol))
        price_variation = current_price - average_price_bought.real
        profitability_total = total_dividends_paid + \
            (price_variation * total_quantity)
        profitability_stock = price_variation * total_quantity

        response = InvestmentDetailResponse(
            ticker_symbol=stock_transaction_symbol,
            current_price=current_price,
            dividends_paid=total_dividends_paid,
            best_price_to_sold_since_buy=yahoo_finance_service.calculate_highest_price(
                history),
            best_price_to_buy_since_buy=yahoo_finance_service.calculate_lowest_price(
                history),
            average_price_since_buy=yahoo_finance_service.calculate_average_price(
                history),
            avarage_price_bought=average_price_bought,
            price_variation=price_variation,
            profitability_total=profitability_total,
            profitability_stock=profitability_stock,
            currency=yahoo_finance_service.get_currency_code(
                yahoo_finance_service.get_ticker_info(stock_transaction_symbol))
        )

        return response

    except Exception as e:
        logger.error(f"Failed to get dividends paid by symbol: {e.__str__()}")
        raise HTTPException(
            status_code=500, detail="Failed to process request")
