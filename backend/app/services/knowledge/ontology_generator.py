"""Auto-generate ontology (entity types + relationship types) from content before graph building."""

from openai import AsyncOpenAI
from app.core.config import settings
from app.services.json_utils import extract_json

ONTOLOGY_PROMPT = """Analyze this text and design a knowledge graph ontology for it.

TEXT:
{text}

SIMULATION PURPOSE:
{purpose}

Generate an ontology with:
1. Entity types (8-12 types): Each with name (PascalCase), description, and 2-3 key attributes
2. Relationship types (6-10 types): Each with name (UPPER_SNAKE_CASE), description, and valid source->target pairs

Rules:
- Always include these base types: Person, Organization, Event
- Entity types should cover all major concepts in the text
- Relationship types should capture the key dynamics between entities
- Think about what relationships matter for social media audience simulation

Return ONLY valid JSON:
{{
  "entity_types": [
    {{"name": "Person", "description": "An individual human", "attributes": ["role", "age_group", "influence_level"]}},
    {{"name": "Organization", "description": "A company or group", "attributes": ["industry", "size"]}}
  ],
  "relationship_types": [
    {{"name": "MEMBER_OF", "description": "Person belongs to organization", "source": "Person", "target": "Organization"}},
    {{"name": "COMPETES_WITH", "description": "Organizations competing", "source": "Organization", "target": "Organization"}}
  ],
  "analysis": "Brief 1-2 sentence analysis of the key entities and dynamics in this content"
}}"""


async def generate_ontology(content: str, context: str = "", purpose: str = "marketing audience simulation") -> dict:
    """Generate an ontology schema from content text."""
    text = content[:2000]
    if context:
        text += "\n\nADDITIONAL CONTEXT:\n" + context[:1000]

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = await client.chat.completions.create(
        model=settings.llm_analysis_model,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": ONTOLOGY_PROMPT.format(text=text, purpose=purpose),
        }],
    )

    text_response = response.choices[0].message.content
    ontology = extract_json(text_response)

    # Ensure base types exist
    entity_names = {e.get("name") for e in ontology.get("entity_types", [])}
    for base in ["Person", "Organization", "Event"]:
        if base not in entity_names:
            ontology.setdefault("entity_types", []).append({
                "name": base,
                "description": f"A {base.lower()} entity",
                "attributes": [],
            })

    return ontology
