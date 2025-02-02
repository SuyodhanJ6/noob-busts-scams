from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
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
    """Model for storing scam reports."""
    
    __tablename__ = "scam_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    scammer_phone = Column(String(20), index=True, nullable=False)
    description = Column(Text, nullable=False)
    reporter_phone = Column(String(20), nullable=True)
    reporter_email = Column(String(255), nullable=True)
    scam_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<ScamReport(id={self.id}, scammer_phone={self.scammer_phone})>"

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True)
    model_version = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow) 