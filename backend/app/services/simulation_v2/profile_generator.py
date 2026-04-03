import json
import random

from openai import AsyncOpenAI
from app.core.config import settings
from app.services.json_utils import extract_json
from app.services.simulation_v2.engine import AgentProfile

PROFILE_PROMPT = """Generate {count} diverse, realistic social media user personas for a simulation about this content:

Content: {content}

World knowledge from graph:
{graph_context}

{audience_config}

Each persona must be a JSON object with:
- "name": realistic name matching the target culture
- "age": integer 13-65
- "gender": "male", "female", or "non-binary"
- "occupation": their job
- "interests": list of 3-5 interests
- "personality": one sentence description including their stance on the content topic
- "social_media_usage": "heavy", "moderate", or "light"

Make them diverse: mix of fans, casual observers, critics, industry people, and general public.
Ensure variety in age, gender, occupation, and attitude toward the content.

Return ONLY a JSON array."""


async def generate_profiles(
    content: str,
    graph_context: str,
    llm_count: int = 20,
    rule_count: int = 100,
    audience_config: dict | None = None,
    language: str = "en",
) -> tuple[list[AgentProfile], list[AgentProfile]]:
    """Generate LLM agent profiles (via API) and rule-based profiles (quick generation)."""

    config_text = ""
    if audience_config:
        config_text = f"Target audience: {json.dumps(audience_config)}"
    if language != "en":
        config_text += f"\nGenerate names appropriate for {language} culture."

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)

    # Generate LLM profiles via API
    response = await client.chat.completions.create(
        model=settings.llm_analysis_model,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": PROFILE_PROMPT.format(
                count=llm_count,
                content=content[:500],
                graph_context=graph_context[:1000],
                audience_config=config_text,
            ),
        }],
    )

    text = response.choices[0].message.content
    raw_profiles = extract_json(text)
    if isinstance(raw_profiles, dict):
        raw_profiles = [raw_profiles]

    llm_profiles = []
    for p in raw_profiles[:llm_count]:
        if not isinstance(p, dict):
            continue
        interests = p.get("interests", ["general"])
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(",")]
        llm_profiles.append(AgentProfile(
            name=p.get("name", f"Agent-{len(llm_profiles)+1}"),
            age=int(p.get("age", 25)),
            gender=p.get("gender", "non-binary"),
            occupation=p.get("occupation", "Unknown"),
            interests=interests,
            personality=p.get("personality", "Average social media user"),
            social_media_usage=p.get("social_media_usage", "moderate"),
            is_llm=True,
        ))

    # Generate rule-based profiles (no LLM call, fast)
    rule_profiles = _generate_rule_profiles(rule_count, audience_config, language)

    return llm_profiles, rule_profiles


def _generate_rule_profiles(
    count: int,
    audience_config: dict | None = None,
    language: str = "en",
) -> list[AgentProfile]:
    """Fast generation of rule-based agent profiles."""

    # Name pools by language
    name_pools = {
        "ko": {
            "first_m": ["민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호", "지훈", "준서"],
            "first_f": ["서연", "서윤", "지우", "하은", "하린", "수아", "지아", "다은", "예은", "채원"],
            "last": ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"],
        },
        "en": {
            "first_m": ["James", "Michael", "David", "Alex", "Ryan", "Tyler", "Jake", "Chris", "Sam", "Ben"],
            "first_f": ["Emma", "Sarah", "Jessica", "Olivia", "Mia", "Sophia", "Lily", "Chloe", "Zoe", "Ava"],
            "last": ["Smith", "Johnson", "Kim", "Lee", "Park", "Chen", "Garcia", "Miller", "Davis", "Wilson"],
        },
    }
    names = name_pools.get(language, name_pools["en"])

    occupations = ["Student", "Office Worker", "Developer", "Designer", "Teacher", "Freelancer",
                    "Marketing Manager", "Nurse", "Artist", "Entrepreneur"]
    interests_pool = ["music", "fashion", "gaming", "travel", "food", "sports", "tech", "art", "movies", "fitness"]
    personalities = [
        "Enthusiastic fan who loves discovering new content",
        "Casual observer who scrolls through feeds occasionally",
        "Critical thinker who questions everything",
        "Trendsetter who shares everything interesting",
        "Skeptical user who rarely engages",
        "Supportive community member who likes everything",
        "Professional who evaluates content objectively",
        "Young and impulsive, reacts emotionally",
    ]

    profiles = []
    for i in range(count):
        gender = random.choice(["male", "female", "non-binary"])
        if gender == "male":
            first = random.choice(names["first_m"])
        else:
            first = random.choice(names["first_f"])
        last = random.choice(names["last"])

        if language == "ko":
            name = f"{last}{first}"
        else:
            name = f"{first} {last}"

        profiles.append(AgentProfile(
            name=f"{name}-{i+1}",
            age=random.randint(15, 55),
            gender=gender,
            occupation=random.choice(occupations),
            interests=random.sample(interests_pool, 3),
            personality=random.choice(personalities),
            social_media_usage=random.choice(["heavy", "moderate", "light"]),
            is_llm=False,
        ))

    return profiles
