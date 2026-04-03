import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db, async_session
from app.models.campaign import Campaign, CampaignEntity, SimAction
from app.services.knowledge.graph_builder import GraphBuilder
from app.services.simulation_v2.profile_generator import generate_profiles
from app.services.simulation_v2.engine import (
    run_simulation, get_simulation_state, Action,
)
from app.services.report.report_agent import generate_report, interview_agent

router = APIRouter(prefix="/v2/campaigns", tags=["campaigns-v2"])


# --- Schemas ---

class CampaignCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    content_type: str = "social_post"
    context_text: str | None = None
    audience_config: dict | None = None
    language: str = "en"
    llm_agents: int = Field(default=10, ge=3, le=30)
    rule_agents: int = Field(default=50, ge=0, le=500)
    sim_rounds: int = Field(default=5, ge=1, le=20)


class CampaignOut(BaseModel):
    id: str
    title: str
    content: str
    content_type: str
    status: str
    language: str
    llm_agents: int
    rule_agents: int
    sim_rounds: int
    viral_score: float | None
    summary: str | None
    report: dict | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class GraphOut(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    stats: dict


class SimStatusOut(BaseModel):
    campaign_id: str
    status: str
    current_round: int
    total_rounds: int
    actions_count: int


class InterviewRequest(BaseModel):
    agent_name: str
    question: str


# --- Background tasks ---

async def _run_campaign_pipeline(campaign_id: str):
    """Full pipeline: build graph → generate profiles → simulate → report."""
    async with async_session() as db:
        campaign = await db.get(Campaign, campaign_id)
        if not campaign:
            return

        try:
            # Step 1: Build knowledge graph
            campaign.status = "graph_building"
            await db.commit()

            builder = GraphBuilder(campaign_id)
            await builder.initialize()
            graph_data = await builder.build_graph(campaign.content, campaign.context_text)

            # Save entities to DB
            for node in graph_data["nodes"]:
                entity = CampaignEntity(
                    campaign_id=campaign_id,
                    name=node["id"],
                    entity_type=node.get("type"),
                    description=node.get("description"),
                )
                db.add(entity)
            await db.commit()

            campaign.status = "graph_ready"
            campaign.graph_dir = builder.working_dir
            await db.commit()

            # Get graph context for agents
            graph_context = await builder.query(
                f"Summarize all key entities and relationships about: {campaign.content[:200]}",
                mode="hybrid",
            )
            if not graph_context:
                graph_context = "No additional context available."

            # Step 2: Generate profiles
            campaign.status = "generating_profiles"
            await db.commit()

            llm_profiles, rule_profiles = await generate_profiles(
                content=campaign.content,
                graph_context=graph_context,
                llm_count=campaign.llm_agents,
                rule_count=campaign.rule_agents,
                audience_config=campaign.audience_config,
                language=campaign.language,
            )

            # Step 3: Run simulation
            campaign.status = "simulating"
            await db.commit()

            actions = await run_simulation(
                campaign_id=campaign_id,
                content=campaign.content,
                graph_context=graph_context,
                llm_profiles=llm_profiles,
                rule_profiles=rule_profiles,
                num_rounds=campaign.sim_rounds,
            )

            # Save actions to DB
            for action in actions:
                sa = SimAction(
                    campaign_id=campaign_id,
                    round_num=action.round_num,
                    agent_name=action.agent_name,
                    agent_profile=action.agent_profile,
                    action_type=action.action_type,
                    content=(action.content or "").encode("utf-8", errors="replace").decode("utf-8"),
                    target_agent=action.target_agent,
                    target_content=(action.target_content or "").encode("utf-8", errors="replace").decode("utf-8"),
                    sentiment=action.sentiment,
                    sentiment_score=action.sentiment_score,
                )
                db.add(sa)
            await db.commit()

            # Step 4: Generate report
            campaign.status = "reporting"
            await db.commit()

            report = await generate_report(
                content=campaign.content,
                actions=actions,
                graph_context=graph_context,
            )

            campaign.viral_score = report.get("viral_score")
            campaign.summary = report.get("summary")
            campaign.report = report
            campaign.status = "completed"
            campaign.completed_at = datetime.utcnow()
            await db.commit()

        except Exception as e:
            try:
                await db.rollback()
            except Exception:
                pass
            campaign.status = "failed"
            campaign.summary = str(e)[:500]
            await db.commit()


# --- Routes ---

@router.post("/", response_model=CampaignOut)
async def create_campaign(req: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = Campaign(
        title=req.title,
        content=req.content,
        content_type=req.content_type,
        context_text=req.context_text,
        audience_config=req.audience_config,
        language=req.language,
        llm_agents=req.llm_agents,
        rule_agents=req.rule_agents,
        sim_rounds=req.sim_rounds,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    # Start pipeline in background
    asyncio.create_task(_run_campaign_pipeline(campaign.id))

    return campaign


@router.get("/", response_model=list[CampaignOut])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    return result.scalars().all()


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/{campaign_id}/graph", response_model=GraphOut)
async def get_graph(campaign_id: str, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not campaign.graph_dir:
        raise HTTPException(status_code=400, detail="Graph not built yet")

    builder = GraphBuilder(campaign_id)
    return builder.get_graph_data()


@router.get("/{campaign_id}/simulation/status", response_model=SimStatusOut)
async def get_sim_status(campaign_id: str):
    state = get_simulation_state(campaign_id)
    return SimStatusOut(
        campaign_id=campaign_id,
        status=state.get("status", "unknown"),
        current_round=state.get("current_round", 0),
        total_rounds=state.get("total_rounds", 0),
        actions_count=state.get("actions_count", 0),
    )


@router.get("/{campaign_id}/actions")
async def get_actions(
    campaign_id: str,
    round_num: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(SimAction).where(SimAction.campaign_id == campaign_id)
    if round_num:
        query = query.where(SimAction.round_num == round_num)
    query = query.order_by(SimAction.round_num, SimAction.created_at)
    result = await db.execute(query)
    actions = result.scalars().all()
    return [
        {
            "round": a.round_num,
            "agent": a.agent_name,
            "profile": a.agent_profile,
            "action": a.action_type,
            "content": a.content,
            "target": a.target_agent,
            "sentiment": a.sentiment,
            "score": a.sentiment_score,
        }
        for a in actions
    ]


@router.get("/{campaign_id}/report")
async def get_report(campaign_id: str, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not campaign.report:
        raise HTTPException(status_code=400, detail="Report not generated yet")
    return campaign.report


@router.post("/{campaign_id}/interview")
async def do_interview(
    campaign_id: str,
    req: InterviewRequest,
    db: AsyncSession = Depends(get_db),
):
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get actions for this campaign
    result = await db.execute(
        select(SimAction).where(SimAction.campaign_id == campaign_id)
    )
    db_actions = result.scalars().all()
    actions = [
        Action(
            round_num=a.round_num,
            agent_name=a.agent_name,
            agent_profile=a.agent_profile or {},
            action_type=a.action_type,
            content=a.content or "",
            sentiment=a.sentiment or "neutral",
            sentiment_score=a.sentiment_score or 0,
        )
        for a in db_actions
    ]

    response = await interview_agent(
        agent_name=req.agent_name,
        question=req.question,
        actions=actions,
        content=campaign.content,
    )
    return {"agent": req.agent_name, "response": response}
