"""Controversy Detector: pre-scan content for culturally sensitive issues.

Runs before simulation to flag potential controversies that small LLMs might miss.
Uses a larger model for nuanced cultural analysis, then injects warnings into
the simulation context so agents and the report agent can account for them.
"""

import logging
import httpx
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.json_utils import extract_json

logger = logging.getLogger(__name__)

CONTROVERSY_PROMPT = """You are a cultural sensitivity analyst specializing in marketing and advertising.
Analyze the following content for potential controversies, offensive elements, or culturally sensitive issues.

Content: {content}
Content Type: {content_type}
Target Language/Market: {language}
Additional Context: {context}

Check for ALL of the following:
1. Gender stereotyping or sexism
2. Racial/ethnic insensitivity
3. Age discrimination
4. Body shaming
5. Economic/class discrimination ("if you can't afford it, you don't deserve it")
6. Cultural appropriation
7. Religious insensitivity
8. Disability insensitivity
9. LGBTQ+ insensitivity
10. Tone-deaf messaging (making light of serious issues)
11. Exclusionary language ("only for X", "real men/women")
12. Toxic positivity / shaming ("stop being lazy", "no excuses")

For each issue found, explain:
- What the issue is
- Why it's problematic in the target market/culture
- How severe it is (low/medium/high/critical)
- Historical examples of similar controversies if applicable

Return a JSON object:
{{
  "has_controversy": true/false,
  "overall_risk": "none" | "low" | "medium" | "high" | "critical",
  "issues": [
    {{
      "category": "category name",
      "description": "what the issue is",
      "severity": "low" | "medium" | "high" | "critical",
      "cultural_context": "why this matters in the target market",
      "score_penalty": <0-40 points to subtract from viral score>
    }}
  ],
  "safe_aspects": ["list of things the content does well"],
  "recommendation": "overall recommendation for the marketer"
}}

Be thorough. Marketing teams need to know about potential backlash BEFORE it happens.
Do NOT give a pass to content that uses stereotypes or exclusionary language, even if
it might appeal to a specific demographic segment."""

LANGUAGE_MAP = {
    "ko": "Korean (South Korea)",
    "ja": "Japanese",
    "zh": "Chinese",
    "en": "English (Global)",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
}


async def detect_controversy(
    content: str,
    content_type: str = "text",
    language: str = "en",
    context: str = "",
) -> dict:
    """Scan content for potential controversies before simulation.

    Returns a dict with has_controversy, overall_risk, issues[], and score_penalty.
    """
    lang_name = LANGUAGE_MAP.get(language, language)

    prompt = CONTROVERSY_PROMPT.format(
        content=content,
        content_type=content_type,
        language=lang_name,
        context=context[:500] if context else "No additional context provided.",
    )

    try:
        # Use dedicated controversy model via Ollama native API if configured
        # (qwen3.5 doesn't work well with OpenAI-compatible /v1 endpoint)
        controversy_model = settings.controversy_model
        if controversy_model:
            ollama_base = settings.llm_base_url.replace("/v1", "")
            async with httpx.AsyncClient(timeout=300.0) as http:
                resp = await http.post(
                    f"{ollama_base}/api/chat",
                    json={
                        "model": controversy_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                text = resp.json().get("message", {}).get("content", "")
        else:
            client = AsyncOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )
            response = await client.chat.completions.create(
                model=settings.llm_analysis_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content

        result = extract_json(text)

        # Calculate total score penalty
        total_penalty = 0
        if result.get("issues"):
            for issue in result["issues"]:
                total_penalty += issue.get("score_penalty", 0)

        result["total_score_penalty"] = min(total_penalty, 80)  # Cap at 80
        return result

    except Exception as e:
        logger.error("Controversy detection failed: %s", e, exc_info=True)
        return {
            "has_controversy": False,
            "overall_risk": "unknown",
            "issues": [],
            "safe_aspects": [],
            "recommendation": f"Controversy detection failed: {str(e)}",
            "total_score_penalty": 0,
        }


def build_controversy_context(controversy: dict) -> str:
    """Build a context string to inject into agent prompts."""
    if not controversy.get("has_controversy"):
        return ""

    lines = ["\nCONTROVERSY ALERT (detected by pre-scan):"]
    lines.append(f"Overall Risk: {controversy.get('overall_risk', 'unknown').upper()}")

    for issue in controversy.get("issues", []):
        lines.append(
            f"- [{issue.get('severity', '?').upper()}] {issue.get('category', '?')}: "
            f"{issue.get('description', '')}"
        )
        if issue.get("cultural_context"):
            lines.append(f"  Context: {issue['cultural_context']}")

    lines.append(
        "\nIMPORTANT: Consider these issues when reacting. "
        "Some personas should react negatively to these problems. "
        "Not everyone will be offended, but awareness varies by age, gender, and values."
    )

    return "\n".join(lines)
