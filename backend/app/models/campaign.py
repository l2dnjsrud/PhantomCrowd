import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String, default="social_post")
    context_text = Column(Text, nullable=True)  # Additional context (fan posts, news, etc.)
    audience_config = Column(JSON, nullable=True)
    language = Column(String, default="en")
    audience_size = Column(Integer, default=20)

    # Pipeline state
    status = Column(String, default="created")  # created, graph_building, graph_ready, simulating, completed, failed
    graph_dir = Column(String, nullable=True)  # LightRAG working directory

    # Simulation config
    llm_agents = Column(Integer, default=20)  # Full LLM agents
    rule_agents = Column(Integer, default=100)  # Rule-based agents
    sim_rounds = Column(Integer, default=10)

    # Results
    viral_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    report = Column(JSON, nullable=True)  # Full report sections

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relations
    graph_entities = relationship("CampaignEntity", back_populates="campaign", cascade="all, delete-orphan")
    sim_actions = relationship("SimAction", back_populates="campaign", cascade="all, delete-orphan")


class CampaignEntity(Base):
    __tablename__ = "campaign_entities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    attributes = Column(JSON, nullable=True)

    campaign = relationship("Campaign", back_populates="graph_entities")


class SimAction(Base):
    __tablename__ = "sim_actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    round_num = Column(Integer, nullable=False)
    agent_name = Column(String, nullable=False)
    agent_profile = Column(JSON, nullable=True)
    action_type = Column(String, nullable=False)  # post, reply, share, like, dislike
    content = Column(Text, nullable=True)
    target_agent = Column(String, nullable=True)  # Who they're replying to
    target_content = Column(Text, nullable=True)  # What they're replying to
    sentiment = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="sim_actions")
