"""Auto-generate simulation configuration based on content and graph analysis."""

from openai import AsyncOpenAI
from app.core.config import settings
from app.services.json_utils import extract_json

CONFIG_PROMPT = """Design simulation parameters for a social media audience simulation.

CONTENT: {content}
GRAPH ENTITIES: {entity_count} entities, {edge_count} relationships
KEY ENTITIES: {key_entities}
LANGUAGE: {language}

Generate realistic simulation parameters:

Return JSON:
{{
  "activity_pattern": {{
    "peak_hours": [list of hours 0-23 when activity is highest],
    "activity_multiplier": {{
      "peak": 2.0,
      "normal": 1.0,
      "low": 0.3
    }}
  }},
  "agent_behavior": {{
    "supporter_share_rate": 0.4,
    "supporter_reply_rate": 0.5,
    "critic_share_rate": 0.1,
    "critic_reply_rate": 0.6,
    "neutral_engage_rate": 0.2
  }},
  "viral_dynamics": {{
    "viral_threshold": 0.6,
    "echo_chamber_strength": 0.3,
    "controversy_boost": 1.5
  }},
  "content_sensitivity": {{
    "topic_heat": <0.0-1.0, how controversial/hot is this topic>,
    "expected_sentiment_bias": <-1.0 to 1.0, expected overall lean>,
    "polarization_risk": <0.0-1.0, how likely to create divided opinions>
  }}
}}"""


async def generate_sim_config(
    content: str,
    entity_count: int,
    edge_count: int,
    key_entities: list[str],
    language: str = "en",
) -> dict:
    """Auto-generate simulation configuration from content analysis."""

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = await client.chat.completions.create(
        model=settings.llm_analysis_model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": CONFIG_PROMPT.format(
                content=content[:500],
                entity_count=entity_count,
                edge_count=edge_count,
                key_entities=", ".join(key_entities[:10]),
                language=language,
            ),
        }],
    )

    text = response.choices[0].message.content
    try:
        config = extract_json(text)
    except Exception:
        config = _default_config()

    # Ensure all required fields
    config.setdefault("activity_pattern", {"peak_hours": [9, 12, 18, 21], "activity_multiplier": {"peak": 2.0, "normal": 1.0, "low": 0.3}})
    config.setdefault("agent_behavior", {"supporter_share_rate": 0.4, "supporter_reply_rate": 0.5, "critic_share_rate": 0.1, "critic_reply_rate": 0.6, "neutral_engage_rate": 0.2})
    config.setdefault("viral_dynamics", {"viral_threshold": 0.6, "echo_chamber_strength": 0.3, "controversy_boost": 1.5})
    config.setdefault("content_sensitivity", {"topic_heat": 0.5, "expected_sentiment_bias": 0.0, "polarization_risk": 0.3})

    return config


def _default_config() -> dict:
    return {
        "activity_pattern": {"peak_hours": [9, 12, 18, 21], "activity_multiplier": {"peak": 2.0, "normal": 1.0, "low": 0.3}},
        "agent_behavior": {"supporter_share_rate": 0.4, "supporter_reply_rate": 0.5, "critic_share_rate": 0.1, "critic_reply_rate": 0.6, "neutral_engage_rate": 0.2},
        "viral_dynamics": {"viral_threshold": 0.6, "echo_chamber_strength": 0.3, "controversy_boost": 1.5},
        "content_sensitivity": {"topic_heat": 0.5, "expected_sentiment_bias": 0.0, "polarization_risk": 0.3},
    }
