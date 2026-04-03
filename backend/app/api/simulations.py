import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db, async_session
from app.models.simulation import Simulation
from app.schemas.simulation import (
    SimulationCreate,
    SimulationOut,
    SimulationSummary,
    SimulationProgress,
)
from app.services.simulation_engine import run_simulation, simulation_progress

router = APIRouter(prefix="/simulations", tags=["simulations"])


async def _run_simulation_background(simulation_id: str):
    async with async_session() as db:
        await run_simulation(simulation_id, db)


@router.post("/", response_model=SimulationOut)
async def create_simulation(req: SimulationCreate, db: AsyncSession = Depends(get_db)):
    sim = Simulation(
        title=req.title,
        content=req.content,
        content_type=req.content_type,
        audience_size=req.audience_size,
    )
    db.add(sim)
    await db.commit()
    await db.refresh(sim)

    asyncio.create_task(_run_simulation_background(sim.id))

    return sim


@router.get("/", response_model=list[SimulationSummary])
async def list_simulations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Simulation).order_by(Simulation.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{simulation_id}", response_model=SimulationOut)
async def get_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Simulation)
        .options(selectinload(Simulation.reactions))
        .where(Simulation.id == simulation_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


@router.get("/{simulation_id}/progress", response_model=SimulationProgress)
async def get_progress(simulation_id: str, db: AsyncSession = Depends(get_db)):
    sim = await db.get(Simulation, simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    progress_data = simulation_progress.get(simulation_id, {})
    total = progress_data.get("total", sim.audience_size)
    completed = progress_data.get("completed", 0)

    if sim.status == "completed":
        completed = total

    return SimulationProgress(
        simulation_id=simulation_id,
        status=sim.status,
        total=total,
        completed=completed,
        progress=completed / total * 100 if total > 0 else 0,
    )


@router.delete("/{simulation_id}")
async def delete_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    sim = await db.get(Simulation, simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    await db.delete(sim)
    await db.commit()
    return {"detail": "Simulation deleted"}
