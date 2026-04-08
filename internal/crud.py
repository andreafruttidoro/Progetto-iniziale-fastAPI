from sqlalchemy.orm import Session
from . import models, schemas
import joblib

# Caricamento modello (spostato qui perché serve al CRUD per calcolare il rischio)
try:
    rf_model = joblib.load("modello_rf.joblib")
except:
    rf_model = None


def create_customer(db: Session, customer: schemas.CustomerCreate):
    new_customer = models.Customer(
        full_name=customer.full_name, email=customer.email)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    # 1. Verifica cliente
    customer = db.query(models.Customer).filter(
        models.Customer.id == feedback.customer_id).first()
    if not customer:
        return None

    # 2. Prepara Feedback
    new_feedback = models.NPSFeedback(**feedback.model_dump())
    db.add(new_feedback)

    # 3. AI Prediction & Customer Update
    if rf_model:
        voto = feedback.score
        lunghezza = len(feedback.comment) if feedback.comment else 0
        prob = rf_model.predict_proba([[voto, lunghezza]])[0][1]

        customer.risk_score = int(prob * 100)
        customer.model_version = "rf_nps_production_v1"

        if customer.risk_score > 80:
            customer.status = "CRITICAL"
        elif customer.risk_score > 50:
            customer.status = "WARNING"
        else:
            customer.status = "STABLE"

    db.commit()
    db.refresh(new_feedback)
    return new_feedback


def get_feedbacks(db: Session):
    return db.query(models.NPSFeedback).all()


def delete_feedback(db: Session, feedback_id: int):
    feedback = db.query(models.NPSFeedback).filter(
        models.NPSFeedback.id == feedback_id).first()
    if feedback:
        db.delete(feedback)
        db.commit()
        return True
    return False
