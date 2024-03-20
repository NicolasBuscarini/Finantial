from fastapi import APIRouter

from app.api.routes import utils, credit_card

api_router = APIRouter()
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(credit_card.router, prefix="/credit-card", tags=["credit-card"])
