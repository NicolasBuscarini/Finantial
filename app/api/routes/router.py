from fastapi import APIRouter
from app.api.routes import investment_detail, stock_transaction, utils, credit_card

# `api_router = APIRouter()` é criando uma instância do `APIRouter` do FastAPI
api_router = APIRouter()


@api_router.get(
    "/",
    status_code=201,
)
async def isAlive():
    """
    The function isAlive returns a dictionary with a message key "isAlive".
    :return: The function `isAlive()` is returning a dictionary with a key "message" and value
    "isAlive".
    """
    return {"message": "FINANCE API is alive!", "status_code": 201, "isAlive": True},

api_router.include_router(utils.router,
                          prefix="/utils", tags=["utils"])
api_router.include_router(credit_card.router,
                          prefix="/credit-card", tags=["credit-card"])
api_router.include_router(stock_transaction.router,
                          prefix="/stock-transaction", tags=["stock-transaction"])
api_router.include_router(investment_detail.router,
                          prefix="/investment-detail", tags=["investment-detail"])
