from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from sqlalchemy.sql import func


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)

    # --- CAMPI PER L'INTEGRAZIONE AI ---
    risk_score = Column(Integer, default=0)         # Il numero (0-100)
    # L'etichetta (es. "Critical")
    status = Column(String, default="Active")
    risk_updated_at = Column(DateTime(timezone=True),
                             onupdate=func.now())  # Quando è cambiato
    model_version = Column(String, default="rf_v1")  # Quale cervello ha deciso

    # Relazione: un cliente può avere molti feedback (One-to-Many)
    feedbacks = relationship("NPSFeedback", back_populates="owner")


class NPSFeedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer)  # Il voto 0-10
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    owner = relationship("Customer", back_populates="feedbacks")
