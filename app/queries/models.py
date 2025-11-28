from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Query(Base):
    """
    Query model to store user questions.
    Each query represents a question asked by a user.
    """
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="queries")
    report = relationship("Report", back_populates="query", uselist=False, cascade="all, delete-orphan")
