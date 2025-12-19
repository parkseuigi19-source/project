from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)

@router.post("/", response_model=schemas.Log)
def create_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    db_log = models.Log(
        content=log.content,
        log_type=log.log_type,
        user_id=log.user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/", response_model=List[schemas.Log])
def read_logs(user_id: str, db: Session = Depends(get_db)):
    return db.query(models.Log).filter(models.Log.user_id == user_id).all()
