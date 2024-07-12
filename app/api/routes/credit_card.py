from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infra.db.mysql_conector import get_db
from app.api.services.credit_card_service import CreditCardService
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


@router.post("/")
def create_credit_card(credit_card_data: dict, db: Session = Depends(get_db)):
    service = CreditCardService(db)
    try:
        return service.create_credit_card(credit_card_data)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Internal Server Error") from e


@router.get("/{credit_card_id}")
def read_credit_card(credit_card_id: int, db: Session = Depends(get_db)):
    service = CreditCardService(db)
    try:
        return service.read_credit_card(credit_card_id)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Internal Server Error") from e


@router.put("/{credit_card_id}")
def update_credit_card(credit_card_id: int, credit_card_data: dict, db: Session = Depends(get_db)):
    service = CreditCardService(db)
    try:
        return service.update_credit_card(credit_card_id, credit_card_data)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Internal Server Error") from e


@router.delete("/{credit_card_id}")
def delete_credit_card(credit_card_id: int, db: Session = Depends(get_db)):
    service = CreditCardService(db)
    try:
        return service.delete_credit_card(credit_card_id)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Internal Server Error") from e
