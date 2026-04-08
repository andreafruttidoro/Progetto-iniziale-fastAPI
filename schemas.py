from pydantic import BaseModel
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# Schema per il Feedback (rimane quasi uguale aggiungendo l'AI)

# Cosa ci aspettiamo dal Frontend quando un utente vota
class FeedbackCreate(BaseModel):
    score: int
    score: int = Field(..., ge=0, le=10, description="Il voto deve essere tra 0 e 10")
    comment: Optional[str] = None
    customer_id: int

# Come restituiamo i dati (include l'ID generato dal DB)


class FeedbackResponse(FeedbackCreate):
    id: int

    class Config:
        from_attributes = True


# Schema per il Cliente (Aggiornato con i campi AI)

class CustomerCreate(BaseModel):
    full_name: str
    email: str
    email: EmailStr


class CustomerResponse(BaseModel):
    id: int
    full_name: str
    email: str
    risk_score: int
    status: str
    risk_updated_at: Optional[datetime]
    model_version: Optional[str]

    class Config:
        from_attributes = True
