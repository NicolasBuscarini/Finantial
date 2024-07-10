from fastapi import APIRouter, HTTPException
import yfinance as yf

router = APIRouter()

@router.get(
    "/teste",
    status_code=201,
)
async def teste():
    return {"Hello": "World"}

@router.get("/stock_info")
async def get_stock_info(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

    except KeyError:
        raise HTTPException(status_code=404, detail="Ticker information not found")
    except Exception:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return info