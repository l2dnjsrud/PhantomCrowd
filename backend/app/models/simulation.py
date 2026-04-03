import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String, default="text")  # text, image_url, ad_copy
    audience_size = Column(Integer, default=50)
    status = Column(String, default="pending")  # pending, running, completed, failed
    viral_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    reactions = relationship("Reaction", back_populates="simulation", cascade="all, delete-orphan")


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String, ForeignKey("simulations.id"), nullable=False)
    persona_name = Column(String, nullable=False)
    persona_profile = Column(JSON, nullable=False)
    sentiment = Column(String, nullable=False)  # positive, negative, neutral, mixed
    sentiment_score = Column(Float, nullable=False)  # -1.0 to 1.0
    comment = Column(Text, nullable=False)
    engagement = Column(String, nullable=False)  # like, share, ignore, dislike
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship("Simulation", back_populates="reactions")
