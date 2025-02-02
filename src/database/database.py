from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    reports = relationship("ScamReport", back_populates="reporter")

class ScamReport(Base):
    __tablename__ = "scam_reports"
    
    id = Column(Integer, primary_key=True)
    scammer_phone = Column(String, nullable=False)
    scam_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String, nullable=False)
    
    reporter = relationship("User", back_populates="reports")

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True)
    model_version = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow) 