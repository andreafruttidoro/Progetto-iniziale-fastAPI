import joblib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from internal import models
from internal import schemas
from internal import database

app = FastAPI(title="NPS Integration & AI Risk System")

# 1. SETUP DATABASE
# Crea le tabelle all'avvio (In produzione useresti Alembic)
models.Base.metadata.create_all(bind=database.engine)

# 2. CARICAMENTO MODELLO ML
# Caricato una volta sola all'avvio per massima efficienza
try:
    rf_model = joblib.load("modello_rf.joblib")
except:
    rf_model = None
    print("⚠️ ATTENZIONE: File 'modello_rf.joblib' non trovato. Il sistema funzionerà senza predizione AI.")

# --- PRIMO ENDPOINT CREATE CUSTOMER --- #


@app.post("/customers/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(database.get_db)):
    # Crea l'oggetto cliente per il database
    new_customer = models.Customer(
        full_name=customer.full_name, email=customer.email)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# --- ENDPOINT: CREATE (Con integrazione AI) ---


@app.post("/feedbacks/", response_model=schemas.FeedbackResponse)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(database.get_db)):
    # 1. Verifica cliente
    customer = db.query(models.Customer).filter(
        models.Customer.id == feedback.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    # 2. Salva Feedback
    new_feedback = models.NPSFeedback(**feedback.model_dump())
    db.add(new_feedback)

    # 3. AI Prediction & Customer Update
    if rf_model:
        # Prepariamo i dati (es. voto e lunghezza commento)
        voto = feedback.score
        lunghezza = len(feedback.comment) if feedback.comment else 0

        # Predizione
        prob = rf_model.predict_proba([[voto, lunghezza]])[0][1]

        # Aggiornamento attributi Customer
        customer.risk_score = int(prob * 100)
        customer.model_version = "rf_nps_production_v1"

        if customer.risk_score > 80:
            customer.status = "CRITICAL"
        elif customer.risk_score > 50:
            customer.status = "WARNING"
        else:
            customer.status = "STABLE"

    # 4. Commit Unico
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

# --- ENDPOINT: READ ---


@app.get("/feedbacks/", response_model=List[schemas.FeedbackResponse])
def get_all_feedbacks(db: Session = Depends(database.get_db)):
    return db.query(models.NPSFeedback).all()

# --- ENDPOINT: ANALYTICS (NPS Classico) ---


@app.get("/analytics/nps")
def calculate_nps(db: Session = Depends(database.get_db)):
    feedbacks = db.query(models.NPSFeedback).all()
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
        "passives": total - len(promoters) - len(detractors),
        "total_responses": total
    }

# --- ENDPOINT: DELETE ---


@app.delete("/feedbacks/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(database.get_db)):
    feedback = db.query(models.NPSFeedback).filter(
        models.NPSFeedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback non trovato")
    db.delete(feedback)
    db.commit()
    return {"message": "Cancellato con successo"}
