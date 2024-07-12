from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.api.models.entities import CreditCard


class CreditCardService:
    """
    Service class for managing credit card operations.

    Args:
        db (Session): The database session.

    Methods:
        create_credit_card: Creates a new credit card.
        read_credit_card: Retrieves a credit card by ID.
        update_credit_card: Updates a credit card by ID.
        delete_credit_card: Deletes a credit card by ID.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_credit_card(self, credit_card_data: dict) -> CreditCard:
        """
        Creates a new credit card.

        Args:
            credit_card_data (dict): The data for the new credit card.

        Returns:
            CreditCard: The created credit card.
        """
        credit_card = CreditCard(**credit_card_data)
        self.db.add(credit_card)
        self.db.commit()
        self.db.refresh(credit_card)
        return credit_card

    def read_credit_card(self, credit_card_id: int) -> CreditCard:
        """
        Retrieves a credit card by ID.

        Args:
            credit_card_id (int): The ID of the credit card to retrieve.

        Returns:
            CreditCard: The retrieved credit card.

        Raises:
            HTTPException: If the credit card is not found.
        """
        credit_card = self.db.query(CreditCard).filter(
            CreditCard.id == credit_card_id).first()
        if credit_card is None:
            raise HTTPException(
                status_code=404, detail="Credit card not found")
        return credit_card

    def update_credit_card(self, credit_card_id: int, credit_card_data: dict) -> CreditCard:
        """
        Updates a credit card by ID.

        Args:
            credit_card_id (int): The ID of the credit card to update.
            credit_card_data (dict): The updated data for the credit card.

        Returns:
            CreditCard: The updated credit card.

        Raises:
            HTTPException: If the credit card is not found.
        """
        credit_card = self.db.query(CreditCard).filter(
            CreditCard.id == credit_card_id).first()
        if credit_card is None:
            raise HTTPException(
                status_code=404, detail="Credit card not found")
        for key, value in credit_card_data.items():
            setattr(credit_card, key, value)
        self.db.commit()
        self.db.refresh(credit_card)
        return credit_card

    def delete_credit_card(self, credit_card_id: int) -> dict:
        """
        Deletes a credit card by ID.

        Args:
            credit_card_id (int): The ID of the credit card to delete.

        Returns:
            dict: A dictionary with a message indicating the success of the deletion.

        Raises:
            HTTPException: If the credit card is not found.
        """
        credit_card = self.db.query(CreditCard).filter(
            CreditCard.id == credit_card_id).first()
        if credit_card is None:
            raise HTTPException(
                status_code=404, detail="Credit card not found")
        self.db.delete(credit_card)
        self.db.commit()
        return {"message": "Credit card deleted successfully"}
