from pydantic import BaseModel, Field
from datetime import datetime


class SimulationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_type: str = Field(default="text")
    audience_size: int = Field(default=50, ge=10, le=500)
    audience_config: dict | None = Field(default=None)


class PersonaProfile(BaseModel):
    name: str
    age: int
    gender: str
    occupation: str
    interests: list[str]
    personality: str
    social_media_usage: str


class ReactionOut(BaseModel):
    id: str
    persona_name: str
    persona_profile: PersonaProfile
    sentiment: str
    sentiment_score: float
    comment: str
    engagement: str
    reasoning: str | None

    model_config = {"from_attributes": True}


class SimulationOut(BaseModel):
    id: str
    title: str
    content: str
    content_type: str
    audience_size: int
    status: str
    viral_score: float | None
    summary: str | None
    suggestions: list[str] | None
    created_at: datetime
    completed_at: datetime | None
    reactions: list[ReactionOut] = []

    model_config = {"from_attributes": True}


class SimulationSummary(BaseModel):
    id: str
    title: str
    status: str
    audience_size: int
    viral_score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SimulationProgress(BaseModel):
    simulation_id: str
    status: str
    total: int
    completed: int
    progress: float
