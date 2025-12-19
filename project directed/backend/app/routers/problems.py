from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..utils import extract_text_by_ext, parse_problems_for_written

router = APIRouter(
    prefix="/problems",
    tags=["problems"],
)

@router.post("/bulk", response_model=dict)
def create_problems_bulk(problems: List[schemas.ProblemCreate], db: Session = Depends(get_db)):
    count = 0
    for p in problems:
        db_problem = models.Problem(
            text=p.text,
            options=p.options,
            answer=p.answer,
            explain=p.explain,
            source=p.source,
            tags=p.tags,
            important=p.important
        )
        db.add(db_problem)
        count += 1
    db.commit()
    return {"inserted": count}

@router.get("/", response_model=List[schemas.Problem])
def read_problems(important: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(models.Problem)
    if important is not None:
        query = query.filter(models.Problem.important == important)
    return query.order_by(models.Problem.created_at.desc()).all()

@router.get("/important", response_model=List[schemas.Problem])
def read_important_problems(db: Session = Depends(get_db)):
    return db.query(models.Problem).filter(models.Problem.important == True).all()

@router.post("/upload_file")
async def upload_problem_file(
    file: UploadFile = File(...),
    importantAll: bool = Form(False),
    tags: str = Form(""),
    source: str = Form(None),
    db: Session = Depends(get_db)
):
    name = file.filename or "upload"
    _, ext = name.rsplit('.', 1) if '.' in name else (name, "")
    ext = f".{ext}"
    
    try:
        data = await file.read()
        raw_text = extract_text_by_ext(ext, data)
        parsed = parse_problems_for_written(raw_text)
        
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        
        inserted = 0
        for obj in parsed:
            db_prob = models.Problem(
                text=obj["text"],
                options=obj.get("options", []),
                answer=obj.get("answer"),
                explain=obj.get("explain"),
                source=source or name,
                tags=tag_list,
                important=importantAll,
                created_at=datetime.utcnow()
            )
            db.add(db_prob)
            inserted += 1
        
        db.commit()
        
        return {
            "inserted": inserted,
            "ext": ext.lower(),
            "message": f"{inserted}개의 문제가 업로드되었습니다."
        }
    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=str(e))
