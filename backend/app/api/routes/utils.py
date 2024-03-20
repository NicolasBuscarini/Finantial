from fastapi import APIRouter

router = APIRouter()

@router.get(
    "/teste",
    status_code=201,
)
async def teste():
    return {"Hello": "World"}