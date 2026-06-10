from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter()
logger = logging.getLogger("ai_assistant")

@router.get("/users", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.get("/users/{user_id}/messages", response_model=List[schemas.MessageOut])
def get_user_messages(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        logger.warning(f"Attempted to fetch messages for non-existent user_id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.Message).filter(models.Message.user_id == user_id).all()