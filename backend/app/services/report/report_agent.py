import json
from collections import Counter

from openai import AsyncOpenAI
from app.core.config import settings
from app.services.json_utils import extract_json
from app.services.simulation_v2.engine import Action

REPORT_PROMPT = """You are a marketing analytics expert. Analyze these social media simulation results and produce a marketing report.

ORIGINAL CONTENT:
{content}

SIMULATION STATS:
- Total agents: {total_agents}
- Total rounds: {total_rounds}
- Total actions: {total_actions}

SENTIMENT DISTRIBUTION:
{sentiment_dist}

ENGAGEMENT DISTRIBUTION:
{engagement_dist}

AVERAGE SENTIMENT SCORE: {avg_score:.2f}

VIRAL INDICATORS:
- Share rate: {share_rate:.1f}%
- Reply rate: {reply_rate:.1f}%
- Like rate: {like_rate:.1f}%
- Dislike rate: {dislike_rate:.1f}%

SAMPLE LLM AGENT REACTIONS (most detailed):
{sample_reactions}

SPREAD DYNAMICS:
{spread_dynamics}

Return a JSON object with:
{{
  "viral_score": <0-100>,
  "summary": "<2-3 sentence executive summary>",
  "sections": [
    {{"title": "Audience Reception", "content": "<detailed analysis>"}},
    {{"title": "Viral Potential", "content": "<spread analysis with specific numbers>"}},
    {{"title": "Segment Analysis", "content": "<how different demographics reacted>"}},
    {{"title": "Key Insights", "content": "<surprising findings, patterns>"}},
    {{"title": "Recommendations", "content": "<3-5 actionable suggestions>"}}
  ],
  "recommendations": ["<suggestion1>", "<suggestion2>", "<suggestion3>"]
}}"""


async def generate_report(
    content: str,
    actions: list[Action],
    graph_context: str = "",
) -> dict:
    """Generate a marketing report from simulation results."""

    # Compute stats
    total_actions = len(actions)
    if total_actions == 0:
        return {"viral_score": 0, "summary": "No simulation data", "sections": [], "recommendations": []}

    rounds = set(a.round_num for a in actions)
    agents = set(a.agent_name for a in actions)

    # Sentiment
    sentiments = Counter(a.sentiment for a in actions if a.sentiment)
    sentiment_dist = json.dumps(dict(sentiments))

    # Engagement
    engagements = Counter(a.action_type for a in actions)
    engagement_dist = json.dumps(dict(engagements))

    # Scores
    scores = [a.sentiment_score for a in actions if a.sentiment_score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Rates
    share_rate = engagements.get("share", 0) / total_actions * 100
    reply_rate = engagements.get("reply", 0) / total_actions * 100
    like_rate = engagements.get("like", 0) / total_actions * 100
    dislike_rate = engagements.get("dislike", 0) / total_actions * 100

    # Sample LLM reactions (ones with actual content)
    llm_reactions = [a for a in actions if a.content and len(a.content) > 10 and not a.content.startswith("(agent")]
    sample_text = ""
    for a in llm_reactions[:15]:
        sample_text += f"[@{a.agent_name}, {a.agent_profile.get('age', '?')}y, {a.agent_profile.get('occupation', '?')}] "
        sample_text += f"({a.action_type}, {a.sentiment} {a.sentiment_score}): {a.content[:150]}\n"

    # Spread dynamics (how actions evolved over rounds)
    spread_text = ""
    for r in sorted(rounds):
        round_actions = [a for a in actions if a.round_num == r]
        round_sentiments = Counter(a.sentiment for a in round_actions if a.sentiment)
        round_types = Counter(a.action_type for a in round_actions)
        spread_text += f"Round {r}: {len(round_actions)} actions, sentiment={dict(round_sentiments)}, types={dict(round_types)}\n"

    # Generate report via LLM
    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = await client.chat.completions.create(
        model=settings.llm_analysis_model,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": REPORT_PROMPT.format(
                content=content[:500],
                total_agents=len(agents),
                total_rounds=len(rounds),
                total_actions=total_actions,
                sentiment_dist=sentiment_dist,
                engagement_dist=engagement_dist,
                avg_score=avg_score,
                share_rate=share_rate,
                reply_rate=reply_rate,
                like_rate=like_rate,
                dislike_rate=dislike_rate,
                sample_reactions=sample_text,
                spread_dynamics=spread_text,
            ),
        }],
    )

    text = response.choices[0].message.content
    report = extract_json(text)

    # Ensure required fields
    report.setdefault("viral_score", 50)
    report.setdefault("summary", "Report generation completed")
    report.setdefault("sections", [])
    report.setdefault("recommendations", [])

    return report


async def interview_agent(
    agent_name: str,
    question: str,
    actions: list[Action],
    content: str,
) -> str:
    """Interview a specific agent about their behavior in the simulation."""
    agent_actions = [a for a in actions if a.agent_name == agent_name]
    if not agent_actions:
        return f"Agent '{agent_name}' not found in simulation."

    profile = agent_actions[0].agent_profile
    action_summary = "\n".join(
        f"Round {a.round_num}: {a.action_type} - {a.content[:100]}" for a in agent_actions[:10]
    )

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = await client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": f"You are {agent_name}, {json.dumps(profile)}. "
                           f"You participated in a social media discussion about: {content[:200]}. "
                           f"Your actions during the simulation:\n{action_summary}\n"
                           f"Answer the question IN CHARACTER.",
            },
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content
