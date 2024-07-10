from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import CreditCard
from app.core.bd import create_session

router = APIRouter()


# Dependency to get the database session
def get_db():
    db = create_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/credit-card/")
def create_credit_card(credit_card_data: dict, db: Session = Depends(get_db)):
    credit_card = CreditCard(**credit_card_data)
    db.add(credit_card)
    db.commit()
    db.refresh(credit_card)
    return credit_card

@router.get("/credit-card/{credit_card_id}")
def read_credit_card(credit_card_id: int, db: Session = Depends(get_db)):
    credit_card = db.query(CreditCard).filter(CreditCard.id == credit_card_id).first()
    if credit_card is None:
        raise HTTPException(status_code=404, detail="Credit card not found")
    return credit_card

@router.put("/credit-card/{credit_card_id}")
def update_credit_card(credit_card_id: int, credit_card_data: dict, db: Session = Depends(get_db)):
    credit_card = db.query(CreditCard).filter(CreditCard.id == credit_card_id).first()
    if credit_card is None:
        raise HTTPException(status_code=404, detail="Credit card not found")
    for key, value in credit_card_data.items():
        setattr(credit_card, key, value)
    db.commit()
    db.refresh(credit_card)
    return credit_card

@router.delete("/credit-card/{credit_card_id}")
def delete_credit_card(credit_card_id: int, db: Session = Depends(get_db)):
    credit_card = db.query(CreditCard).filter(CreditCard.id == credit_card_id).first()
    if credit_card is None:
        raise HTTPException(status_code=404, detail="Credit card not found")
    db.delete(credit_card)
    db.commit()
    return {"message": "Credit card deleted successfully"}

