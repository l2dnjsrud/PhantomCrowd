import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db, async_session
from app.models.simulation import ABTest, Simulation
from app.schemas.simulation import ABTestCreate, ABTestOut, ABTestSummary
from app.services.simulation_engine import run_simulation

router = APIRouter(prefix="/ab-tests", tags=["ab-tests"])


async def _run_ab_test_background(ab_test_id: str, sim_a_id: str, sim_b_id: str):
    async with async_session() as db:
        await run_simulation(sim_a_id, db)
    async with async_session() as db:
        await run_simulation(sim_b_id, db)
    async with async_session() as db:
        await _compute_winner(ab_test_id, db)


async def _compute_winner(ab_test_id: str, db: AsyncSession):
    ab = await db.get(ABTest, ab_test_id)
    if not ab:
        return

    result = await db.execute(
        select(Simulation)
        .options(selectinload(Simulation.reactions))
        .where(Simulation.ab_test_id == ab_test_id)
    )
    sims = {s.ab_variant: s for s in result.scalars().all()}

    sim_a = sims.get("A")
    sim_b = sims.get("B")

    if not sim_a or not sim_b:
        ab.status = "failed"
        await db.commit()
        return

    if sim_a.status == "failed" or sim_b.status == "failed":
        ab.status = "failed"
        await db.commit()
        return

    def avg_score(sim):
        if not sim.reactions:
            return 0
        return sum(r.sentiment_score for r in sim.reactions) / len(sim.reactions)

    def engagement_rate(sim):
        if not sim.reactions:
            return 0
        engaged = sum(1 for r in sim.reactions if r.engagement != "ignore")
        return round(engaged / len(sim.reactions) * 100, 1)

    def share_rate(sim):
        if not sim.reactions:
            return 0
        shares = sum(1 for r in sim.reactions if r.engagement == "share")
        return round(shares / len(sim.reactions) * 100, 1)

    score_a, score_b = sim_a.viral_score or 0, sim_b.viral_score or 0
    sent_a, sent_b = avg_score(sim_a), avg_score(sim_b)
    eng_a, eng_b = engagement_rate(sim_a), engagement_rate(sim_b)
    share_a, share_b = share_rate(sim_a), share_rate(sim_b)

    comparison = [
        {"metric": "Viral Score", "variant_a": score_a, "variant_b": score_b,
         "winner": "A" if score_a > score_b else "B" if score_b > score_a else "tie"},
        {"metric": "Avg Sentiment", "variant_a": round(sent_a, 3), "variant_b": round(sent_b, 3),
         "winner": "A" if sent_a > sent_b else "B" if sent_b > sent_a else "tie"},
        {"metric": "Engagement Rate %", "variant_a": eng_a, "variant_b": eng_b,
         "winner": "A" if eng_a > eng_b else "B" if eng_b > eng_a else "tie"},
        {"metric": "Share Rate %", "variant_a": share_a, "variant_b": share_b,
         "winner": "A" if share_a > share_b else "B" if share_b > share_a else "tie"},
    ]

    a_wins = sum(1 for c in comparison if c["winner"] == "A")
    b_wins = sum(1 for c in comparison if c["winner"] == "B")
    winner = "A" if a_wins > b_wins else "B" if b_wins > a_wins else "tie"

    ab.comparison = comparison
    ab.winner = winner
    ab.status = "completed"
    ab.completed_at = datetime.utcnow()
    await db.commit()


@router.post("/", response_model=ABTestOut)
async def create_ab_test(req: ABTestCreate, db: AsyncSession = Depends(get_db)):
    ab = ABTest(title=req.title)
    db.add(ab)
    await db.flush()

    sim_a = Simulation(
        title=f"{req.title} — Variant A",
        content=req.content_a,
        content_type=req.content_type,
        audience_size=req.audience_size,
        audience_config=req.audience_config,
        language=req.language,
        ab_test_id=ab.id,
        ab_variant="A",
    )
    sim_b = Simulation(
        title=f"{req.title} — Variant B",
        content=req.content_b,
        content_type=req.content_type,
        audience_size=req.audience_size,
        audience_config=req.audience_config,
        language=req.language,
        ab_test_id=ab.id,
        ab_variant="B",
    )
    db.add_all([sim_a, sim_b])
    await db.commit()

    asyncio.create_task(_run_ab_test_background(ab.id, sim_a.id, sim_b.id))

    return await _get_ab_test(ab.id, db)


@router.get("/", response_model=list[ABTestSummary])
async def list_ab_tests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ABTest).order_by(ABTest.created_at.desc()))
    return result.scalars().all()


async def _get_ab_test(ab_id: str, db: AsyncSession) -> dict:
    result = await db.execute(
        select(ABTest).where(ABTest.id == ab_id)
    )
    ab = result.scalar_one_or_none()
    if not ab:
        raise HTTPException(status_code=404, detail="A/B test not found")

    sim_result = await db.execute(
        select(Simulation)
        .options(selectinload(Simulation.reactions))
        .where(Simulation.ab_test_id == ab_id)
    )
    sims = {s.ab_variant: s for s in sim_result.scalars().all()}

    return {
        "id": ab.id,
        "title": ab.title,
        "status": ab.status,
        "winner": ab.winner,
        "comparison": ab.comparison,
        "created_at": ab.created_at,
        "completed_at": ab.completed_at,
        "simulation_a": sims.get("A"),
        "simulation_b": sims.get("B"),
    }


@router.get("/{ab_test_id}", response_model=ABTestOut)
async def get_ab_test(ab_test_id: str, db: AsyncSession = Depends(get_db)):
    return await _get_ab_test(ab_test_id, db)
