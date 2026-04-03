from pydantic import BaseModel, Field
from datetime import datetime


class SimulationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_type: str = Field(default="text")
    audience_size: int = Field(default=50, ge=10, le=500)
    audience_config: dict | None = Field(default=None)
    language: str = Field(default="en")


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
    language: str = "en"
    status: str
    viral_score: float | None
    summary: str | None
    suggestions: list[str] | None
    created_at: datetime
    completed_at: datetime | None
    ab_test_id: str | None = None
    ab_variant: str | None = None
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


# A/B Test schemas
class ABTestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content_a: str = Field(..., min_length=1)
    content_b: str = Field(..., min_length=1)
    content_type: str = Field(default="text")
    audience_size: int = Field(default=50, ge=10, le=500)
    audience_config: dict | None = Field(default=None)
    language: str = Field(default="en")


class ABTestComparison(BaseModel):
    metric: str
    variant_a: float
    variant_b: float
    winner: str


class ABTestOut(BaseModel):
    id: str
    title: str
    status: str
    winner: str | None
    comparison: list[ABTestComparison] | None
    created_at: datetime
    completed_at: datetime | None
    simulation_a: SimulationOut | None = None
    simulation_b: SimulationOut | None = None

    model_config = {"from_attributes": True}


class ABTestSummary(BaseModel):
    id: str
    title: str
    status: str
    winner: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# Export schema
class ExportRequest(BaseModel):
    format: str = Field(default="csv", pattern="^(csv|json)$")
