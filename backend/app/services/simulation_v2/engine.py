import asyncio
import json
import random
from datetime import datetime
from dataclasses import dataclass, field

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

from app.core.config import settings


@dataclass
class AgentProfile:
    name: str
    age: int
    gender: str
    occupation: str
    interests: list[str]
    personality: str
    social_media_usage: str  # heavy, moderate, light
    is_llm: bool = True  # True = full LLM agent, False = rule-based


@dataclass
class Action:
    round_num: int
    agent_name: str
    agent_profile: dict
    action_type: str  # post, reply, share, like, dislike, ignore
    content: str = ""
    target_agent: str = ""
    target_content: str = ""
    sentiment: str = "neutral"
    sentiment_score: float = 0.0


# In-memory simulation state
simulation_states: dict[str, dict] = {}


def _create_model():
    """Create a camel-ai model instance for Ollama."""
    return ModelFactory.create(
        model_platform=ModelPlatformType.OLLAMA,
        model_type=settings.llm_model,
        url=settings.llm_base_url,
    )


def _create_agent(profile: AgentProfile, content_context: str, graph_context: str) -> ChatAgent:
    """Create a camel-ai ChatAgent with persona."""
    system_msg = f"""You are simulating a real person on social media.

YOUR IDENTITY:
Name: {profile.name}
Age: {profile.age}, Gender: {profile.gender}
Occupation: {profile.occupation}
Interests: {', '.join(profile.interests)}
Personality: {profile.personality}
Social Media Usage: {profile.social_media_usage}

WORLD CONTEXT:
{graph_context}

You are reacting to and discussing this content on a social media platform:
{content_context}

Stay in character. React authentically based on your personality, age, and interests.
When replying to others, reference their actual words. Be natural, not robotic.
Always respond with a JSON object:
{{"action": "post|reply|share|like|dislike|ignore", "content": "your message", "sentiment": "positive|negative|neutral|mixed", "sentiment_score": <-1.0 to 1.0>}}"""

    model = _create_model()
    return ChatAgent(system_message=system_msg, model=model)


async def _llm_agent_act(
    agent: ChatAgent,
    profile: AgentProfile,
    round_num: int,
    feed: list[Action],
) -> Action:
    """Have a full LLM agent take an action."""
    # Build the feed context
    if feed:
        recent = feed[-10:]  # Last 10 actions
        feed_text = "Recent social media feed:\n"
        for a in recent:
            if a.action_type == "post":
                feed_text += f"@{a.agent_name}: {a.content}\n"
            elif a.action_type == "reply":
                feed_text += f"@{a.agent_name} replied to @{a.target_agent}: {a.content}\n"
            elif a.action_type == "share":
                feed_text += f"@{a.agent_name} shared @{a.target_agent}'s post: {a.target_content[:50]}\n"
        prompt = f"{feed_text}\nWhat do you do? React to what you see."
    else:
        prompt = "You just saw this content for the first time. What's your reaction?"

    try:
        response = agent.step(prompt)
        text = response.msgs[0].content

        # Parse JSON response
        from app.services.json_utils import extract_json
        data = extract_json(text)

        action_type = data.get("action", "post")
        if action_type not in ("post", "reply", "share", "like", "dislike", "ignore"):
            action_type = "post"

        # If replying/sharing, pick a target from feed
        target_agent = ""
        target_content = ""
        if action_type in ("reply", "share") and feed:
            target = random.choice(feed[-5:])
            target_agent = target.agent_name
            target_content = target.content

        return Action(
            round_num=round_num,
            agent_name=profile.name,
            agent_profile={
                "name": profile.name, "age": profile.age,
                "gender": profile.gender, "occupation": profile.occupation,
            },
            action_type=action_type,
            content=str(data.get("content", ""))[:500],
            target_agent=target_agent,
            target_content=target_content[:200],
            sentiment=data.get("sentiment", "neutral"),
            sentiment_score=float(data.get("sentiment_score", 0)),
        )
    except Exception as e:
        return Action(
            round_num=round_num,
            agent_name=profile.name,
            agent_profile={"name": profile.name},
            action_type="post",
            content=f"(agent error: {str(e)[:100]})",
            sentiment="neutral",
            sentiment_score=0,
        )


def _rule_agent_act(
    profile: AgentProfile,
    round_num: int,
    feed: list[Action],
) -> Action:
    """Have a rule-based agent take an action (no LLM call)."""
    # Probability-based behavior
    usage_weights = {"heavy": 0.8, "moderate": 0.5, "light": 0.2}
    engage_prob = usage_weights.get(profile.social_media_usage, 0.5)

    if random.random() > engage_prob:
        return Action(
            round_num=round_num,
            agent_name=profile.name,
            agent_profile={"name": profile.name, "age": profile.age},
            action_type="ignore",
            sentiment="neutral",
            sentiment_score=0,
        )

    # Pick action type based on personality
    actions = ["like", "like", "share", "reply", "dislike"]
    if "enthusiastic" in profile.personality.lower() or "fan" in profile.personality.lower():
        actions = ["like", "like", "share", "share", "reply"]
    elif "critical" in profile.personality.lower() or "skeptic" in profile.personality.lower():
        actions = ["dislike", "like", "ignore", "reply", "reply"]

    action_type = random.choice(actions)
    target_agent = ""
    target_content = ""

    if feed and action_type in ("reply", "share"):
        target = random.choice(feed[-5:]) if feed else None
        if target:
            target_agent = target.agent_name
            target_content = target.content[:200]

    # Generate sentiment based on personality
    if "fan" in profile.personality.lower() or "positive" in profile.personality.lower():
        sentiment_score = random.uniform(0.3, 0.9)
        sentiment = "positive"
    elif "critical" in profile.personality.lower():
        sentiment_score = random.uniform(-0.7, 0.2)
        sentiment = "negative" if sentiment_score < 0 else "neutral"
    else:
        sentiment_score = random.uniform(-0.3, 0.7)
        sentiment = "positive" if sentiment_score > 0.3 else "neutral" if sentiment_score > -0.3 else "negative"

    return Action(
        round_num=round_num,
        agent_name=profile.name,
        agent_profile={"name": profile.name, "age": profile.age},
        action_type=action_type,
        content="",  # Rule-based agents don't generate text
        target_agent=target_agent,
        target_content=target_content,
        sentiment=sentiment,
        sentiment_score=round(sentiment_score, 2),
    )


async def run_simulation(
    campaign_id: str,
    content: str,
    graph_context: str,
    llm_profiles: list[AgentProfile],
    rule_profiles: list[AgentProfile],
    num_rounds: int = 10,
) -> list[Action]:
    """Run multi-agent simulation with LLM + rule-based agents."""

    simulation_states[campaign_id] = {
        "status": "running",
        "total_rounds": num_rounds,
        "current_round": 0,
        "total_agents": len(llm_profiles) + len(rule_profiles),
        "actions_count": 0,
    }

    # Create LLM agents
    agents = {}
    for profile in llm_profiles:
        agents[profile.name] = _create_agent(profile, content, graph_context)

    all_actions: list[Action] = []

    try:
        for round_num in range(1, num_rounds + 1):
            simulation_states[campaign_id]["current_round"] = round_num
            round_actions: list[Action] = []

            # LLM agents act (sequentially to avoid overwhelming Ollama)
            for profile in llm_profiles:
                agent = agents[profile.name]
                action = await asyncio.to_thread(
                    lambda p=profile, a=agent: asyncio.run(
                        _llm_agent_act(a, p, round_num, all_actions)
                    )
                )
                round_actions.append(action)
                simulation_states[campaign_id]["actions_count"] += 1

            # Rule-based agents act (instant, no LLM)
            for profile in rule_profiles:
                action = _rule_agent_act(profile, round_num, all_actions)
                if action.action_type != "ignore":
                    round_actions.append(action)
                    simulation_states[campaign_id]["actions_count"] += 1

            all_actions.extend(round_actions)

        simulation_states[campaign_id]["status"] = "completed"
    except Exception as e:
        simulation_states[campaign_id]["status"] = "failed"
        simulation_states[campaign_id]["error"] = str(e)
    finally:
        # Clean up agents
        agents.clear()

    return all_actions


def get_simulation_state(campaign_id: str) -> dict:
    return simulation_states.get(campaign_id, {"status": "unknown"})
