import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.simulation import Simulation

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/simulations/{simulation_id}/csv")
async def export_csv(simulation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Simulation)
        .options(selectinload(Simulation.reactions))
        .where(Simulation.id == simulation_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Persona", "Age", "Gender", "Occupation", "Interests",
        "Personality", "Social Media Usage", "Sentiment", "Sentiment Score",
        "Engagement", "Comment", "Reasoning",
    ])

    for r in sim.reactions:
        p = r.persona_profile
        writer.writerow([
            r.persona_name, p.get("age"), p.get("gender"), p.get("occupation"),
            ", ".join(p.get("interests", [])), p.get("personality"),
            p.get("social_media_usage"), r.sentiment, r.sentiment_score,
            r.engagement, r.comment, r.reasoning,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=phantomcrowd-{simulation_id[:8]}.csv"},
    )


@router.get("/simulations/{simulation_id}/json")
async def export_json(simulation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Simulation)
        .options(selectinload(Simulation.reactions))
        .where(Simulation.id == simulation_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    data = {
        "title": sim.title,
        "content": sim.content,
        "content_type": sim.content_type,
        "audience_size": sim.audience_size,
        "viral_score": sim.viral_score,
        "summary": sim.summary,
        "suggestions": sim.suggestions,
        "reactions": [
            {
                "persona": r.persona_profile,
                "sentiment": r.sentiment,
                "sentiment_score": r.sentiment_score,
                "engagement": r.engagement,
                "comment": r.comment,
                "reasoning": r.reasoning,
            }
            for r in sim.reactions
        ],
    }

    output = json.dumps(data, indent=2, ensure_ascii=False)
    return StreamingResponse(
        iter([output]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=phantomcrowd-{simulation_id[:8]}.json"},
    )
