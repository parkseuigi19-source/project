from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        # For MVP, just return existing user if typed same name
        if db_user.user_type != user.user_type:
             # Update type if changed (simple logic)
             db_user.user_type = user.user_type
             db.commit()
             db.refresh(db_user)
        return db_user
    
    new_user = models.User(
        id=str(uuid.uuid4()),
        username=user.username,
        user_type=user.user_type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
