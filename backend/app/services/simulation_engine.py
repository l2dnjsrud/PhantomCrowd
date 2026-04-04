import json
import asyncio
from datetime import datetime

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.simulation import Simulation, Reaction
from app.services.persona_generator import generate_personas
from app.services.json_utils import extract_json

REACTION_PROMPT = """You are simulating a real person's reaction to content on social media.

YOUR PERSONA:
Name: {name}
Age: {age}
Gender: {gender}
Occupation: {occupation}
Interests: {interests}
Personality: {personality}
Social Media Usage: {social_media_usage}

CONTENT TO REACT TO:
Type: {content_type}
Content: {content}

React to this content AS THIS PERSONA. Be authentic to the persona's background, age, interests, and personality.
{language_instruction}
Return ONLY valid JSON with these exact keys:
- "sentiment": one of "positive", "negative", "neutral", "mixed"
- "sentiment_score": a number between -1.0 and 1.0
- "comment": a realistic comment this person would write
- "engagement": one of "like", "share", "ignore", "dislike"
- "reasoning": brief internal reasoning

Example format:
{{"sentiment": "positive", "sentiment_score": 0.7, "comment": "Great post!", "engagement": "like", "reasoning": "I found it interesting"}}"""

ANALYSIS_PROMPT = """Analyze the following audience simulation results and provide a summary.

Content: {content}

Total Reactions: {total}
Sentiment Distribution: {sentiment_dist}
Engagement Distribution: {engagement_dist}
Average Sentiment Score: {avg_score:.2f}

Sample Comments:
{sample_comments}

Provide:
1. A concise summary (2-3 sentences) of overall audience reception. Be honest about weaknesses.
2. A viral score from 0-100 using this STRICT calibration:
   - 0-15: Actively harmful, would cause brand damage or backlash
   - 16-30: Poor, mostly negative reactions, offensive or tone-deaf
   - 31-45: Below average, weak engagement, forgettable
   - 46-55: Average, some positive but nothing compelling to share
   - 56-70: Good, solid positive sentiment, moderate sharing potential
   - 71-85: Very good, strong engagement, clear viral potential
   - 86-95: Excellent, overwhelming positive, massive sharing
   - 96-100: Legendary, historic campaign level
   IMPORTANT: Most content scores 40-60. Above 75 requires strong evidence.
   If avg sentiment < 0.3, score should NOT exceed 60.
   If "ignore" or "dislike" exceeds 30%, subtract 15+ points.
3. 3-5 actionable suggestions to improve the content

Return ONLY a JSON object:
{{
  "summary": "<summary>",
  "viral_score": <0-100>,
  "suggestions": ["<suggestion1>", "<suggestion2>", ...]
}}"""

# In-memory progress tracking
simulation_progress: dict[str, dict] = {}


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )


LANGUAGE_MAP = {
    "en": "English", "ko": "Korean", "ja": "Japanese", "zh": "Chinese",
    "es": "Spanish", "fr": "French", "de": "German", "pt": "Portuguese",
    "ar": "Arabic", "hi": "Hindi", "vi": "Vietnamese", "th": "Thai",
}


async def _generate_single_reaction(
    client: AsyncOpenAI,
    persona: dict,
    content: str,
    content_type: str,
    language: str = "en",
) -> dict:
    lang_name = LANGUAGE_MAP.get(language, language)
    lang_instruction = ""
    if language != "en":
        lang_instruction = f"\nIMPORTANT: Write the comment in {lang_name}. The persona is a {lang_name} speaker."

    persona_copy = {**persona, "interests": ", ".join(persona["interests"])}
    prompt = REACTION_PROMPT.format(
        content_type=content_type,
        content=content,
        language_instruction=lang_instruction,
        **persona_copy,
    )

    response = await client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content
    return extract_json(text)


async def _generate_batch_reactions(
    client: AsyncOpenAI,
    personas: list[dict],
    content: str,
    content_type: str,
    simulation_id: str,
    language: str = "en",
) -> list[dict]:
    tasks = [
        _generate_single_reaction(client, p, content, content_type, language)
        for p in personas
    ]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        if simulation_id in simulation_progress:
            simulation_progress[simulation_id]["completed"] += 1
    return results


async def _analyze_results(
    client: AsyncOpenAI,
    content: str,
    reactions: list[dict],
) -> dict:
    sentiment_dist = {}
    engagement_dist = {}
    scores = []

    for r in reactions:
        sentiment_dist[r["sentiment"]] = sentiment_dist.get(r["sentiment"], 0) + 1
        engagement_dist[r["engagement"]] = engagement_dist.get(r["engagement"], 0) + 1
        scores.append(r["sentiment_score"])

    avg_score = sum(scores) / len(scores) if scores else 0
    sample_comments = "\n".join(
        f"- [{r['sentiment']}] {r['comment']}" for r in reactions[:10]
    )

    prompt = ANALYSIS_PROMPT.format(
        content=content[:500],
        total=len(reactions),
        sentiment_dist=json.dumps(sentiment_dist),
        engagement_dist=json.dumps(engagement_dist),
        avg_score=avg_score,
        sample_comments=sample_comments,
    )

    response = await client.chat.completions.create(
        model=settings.llm_analysis_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content
    return extract_json(text)


async def run_simulation(simulation_id: str, db: AsyncSession):
    sim = await db.get(Simulation, simulation_id)
    if not sim:
        return

    sim.status = "running"
    await db.commit()

    simulation_progress[simulation_id] = {
        "total": sim.audience_size,
        "completed": 0,
    }

    try:
        client = _get_client()

        # Step 1: Generate personas
        personas = await generate_personas(
            content=sim.content,
            content_type=sim.content_type,
            count=sim.audience_size,
            audience_config=sim.audience_config,
        )

        # Step 2: Generate reactions in batches
        all_reactions = []
        for i in range(0, len(personas), settings.batch_size):
            batch = personas[i : i + settings.batch_size]
            batch_results = await _generate_batch_reactions(
                client, batch, sim.content, sim.content_type, simulation_id,
                language=getattr(sim, "language", "en") or "en",
            )

            for persona, reaction in zip(batch, batch_results):
                # Clean surrogate characters that break SQLite/UTF-8
                comment = reaction.get("comment", "").encode("utf-8", errors="replace").decode("utf-8")
                reasoning = (reaction.get("reasoning") or "").encode("utf-8", errors="replace").decode("utf-8")
                reaction_obj = Reaction(
                    simulation_id=simulation_id,
                    persona_name=persona["name"],
                    persona_profile=persona,
                    sentiment=reaction["sentiment"],
                    sentiment_score=reaction["sentiment_score"],
                    comment=comment,
                    engagement=reaction["engagement"],
                    reasoning=reasoning,
                )
                db.add(reaction_obj)
                all_reactions.append(reaction)

            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise

        # Step 3: Analyze results
        analysis = await _analyze_results(client, sim.content, all_reactions)

        sim.viral_score = analysis["viral_score"]
        sim.summary = analysis["summary"]
        sim.suggestions = analysis["suggestions"]
        sim.status = "completed"
        sim.completed_at = datetime.utcnow()
        await db.commit()

    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass
        sim.status = "failed"
        sim.summary = str(e)[:500]
        await db.commit()
    finally:
        simulation_progress.pop(simulation_id, None)
