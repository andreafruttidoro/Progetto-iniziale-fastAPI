from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from internal import schemas, crud, database, models

router = APIRouter()


@router.post("/customers/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(database.get_db)):
    return crud.create_customer(db, customer)


@router.post("/feedbacks/", response_model=schemas.FeedbackResponse)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(database.get_db)):
    db_feedback = crud.create_feedback(db, feedback)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    return db_feedback


@router.get("/feedbacks/", response_model=List[schemas.FeedbackResponse])
def read_feedbacks(db: Session = Depends(database.get_db)):
    return crud.get_feedbacks(db)


@router.get("/analytics/nps")
def get_nps_stats(db: Session = Depends(database.get_db)):
    feedbacks = crud.get_feedbacks(db)
    if not feedbacks:
        return {"nps_score": 0, "total_responses": 0}

    promoters = [f for f in feedbacks if f.score >= 9]
    detractors = [f for f in feedbacks if f.score <= 6]
    total = len(feedbacks)
    nps_score = ((len(promoters) - len(detractors)) / total) * 100

    return {
        "nps_score": round(nps_score, 2),
        "promoters": len(promoters),
        "detractors": len(detractors),
        "total_responses": total
    }


@router.delete("/feedbacks/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_feedback(db, feedback_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback non trovato")
    return {"message": "Cancellato con successo"}
