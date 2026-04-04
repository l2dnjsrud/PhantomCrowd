"""ReportAgent with ReACT pattern: Plan → Search → Write → Reflect per section."""

import json
from collections import Counter

from openai import AsyncOpenAI
from app.core.config import settings
from app.services.json_utils import extract_json
from app.services.simulation_v2.engine import Action
from app.services.report.tools import (
    graph_search, action_search, sentiment_aggregate, identify_influencers,
    ToolResult,
)

# --- Phase 1: Plan ---

PLAN_PROMPT = """You are a marketing report planner. Based on the simulation data below, plan a report outline.

Content being analyzed: {content}
Total agents: {total_agents} | Total rounds: {total_rounds} | Total actions: {total_actions}
Sentiment: {sentiment_summary}
Engagement: {engagement_summary}
Avg Score: {avg_score:.2f}

Create 5-7 report sections that would be most valuable for a marketing team.
Each section should investigate a specific question about the audience reaction.

Return a JSON array of section objects:
[
  {{"title": "Section Title", "question": "What specific question should this section answer?", "tools": ["tool_name1", "tool_name2"]}}
]

Available tools: graph_search, action_search, sentiment_aggregate, identify_influencers

Return ONLY the JSON array."""

# --- Phase 2: Search + Write per section ---

SEARCH_PROMPT = """Based on the tool results below, what are the key findings for this section?

Section: {title}
Question: {question}

Tool Results:
{tool_results}

List the 3-5 most important findings. Be specific with numbers."""

WRITE_PROMPT = """Write a detailed marketing report section based on these findings.

Section Title: {title}
Question: {question}
Key Findings: {findings}

Additional context from knowledge graph:
{graph_context}

Sample agent reactions:
{sample_reactions}

Write 2-4 paragraphs. Be specific, use numbers, quote agent reactions when relevant.
Focus on actionable insights for a marketing team. No generic advice."""

# --- Phase 3: Reflect ---

REFLECT_PROMPT = """Review this report section for quality. Is it specific enough? Does it use real data?

Section: {title}
Content: {content}

Rate 1-10 and suggest one specific improvement. Return JSON:
{{"score": N, "improvement": "specific suggestion", "revised": "improved version if score < 7, else empty string"}}"""

# --- Phase 4: Final synthesis ---

SYNTHESIS_PROMPT = """You are a senior marketing analyst. Synthesize these report sections into a final verdict.

Content: {content}

Simulation Statistics:
- Average sentiment score: {avg_score:.2f} (range: -1.0 to 1.0)
- Positive ratio: {positive_ratio:.0%}
- Negative ratio: {negative_ratio:.0%}
- Engagement rate: {engagement_rate:.0%} (non-ignore actions / total)

Sections:
{sections_text}

Influencer Analysis:
{influencer_data}

Provide:
1. viral_score (0-100): Use this STRICT calibration scale:
   - 0-15: Actively harmful. Would cause brand damage, boycotts, PR crisis.
   - 16-30: Poor. Mostly negative reactions, offensive/tone-deaf content. Most people would ignore or criticize.
   - 31-45: Below average. Weak engagement, forgettable content. No sharing momentum.
   - 46-55: Average. Some positive reactions but nothing compelling enough to share widely.
   - 56-70: Good. Solid positive sentiment, moderate sharing. Decent campaign but not exceptional.
   - 71-85: Very good. Strong positive engagement, high share rate, clear viral potential.
   - 86-95: Excellent. Overwhelming positive response, massive sharing, cultural moment potential.
   - 96-100: Legendary. Historic campaign level (Think: Nike "Just Do It", Apple "Think Different").

   IMPORTANT: Most content should score 40-60. Scores above 75 require overwhelming evidence.
   A score above 85 should be RARE. Use the actual sentiment data to justify your score.
   If avg sentiment is below 0.3, the score should NOT be above 60.
   If negative ratio exceeds 20%, subtract at least 15 points from your initial estimate.
   Content that is offensive, exclusionary, or shaming should score below 30 regardless of engagement.

2. summary: 2-3 sentence executive summary. Be honest about weaknesses.
3. recommendations: 3-5 specific, actionable recommendations

Return JSON:
{{"viral_score": N, "summary": "...", "recommendations": ["...", "..."]}}"""


async def _llm_call(prompt: str, max_tokens: int = 2048) -> str:
    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = await client.chat.completions.create(
        model=settings.llm_analysis_model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def _compute_stats(actions: list[Action]) -> dict:
    sentiments = Counter(a.sentiment for a in actions if a.sentiment)
    engagements = Counter(a.action_type for a in actions)
    scores = [a.sentiment_score for a in actions if a.sentiment_score is not None]
    rounds = set(a.round_num for a in actions)
    agents = set(a.agent_name for a in actions)
    return {
        "total_agents": len(agents),
        "total_rounds": len(rounds),
        "total_actions": len(actions),
        "sentiments": dict(sentiments),
        "engagements": dict(engagements),
        "avg_score": sum(scores) / len(scores) if scores else 0,
    }


LANGUAGE_INSTRUCTION_MAP = {
    "ko": "\n\nIMPORTANT: Write ALL output in Korean (한국어). Section titles, analysis, recommendations, summary — everything must be in Korean.",
    "ja": "\n\nIMPORTANT: Write ALL output in Japanese (日本語).",
    "zh": "\n\nIMPORTANT: Write ALL output in Chinese (中文).",
    "es": "\n\nIMPORTANT: Write ALL output in Spanish (Español).",
    "fr": "\n\nIMPORTANT: Write ALL output in French (Français).",
    "de": "\n\nIMPORTANT: Write ALL output in German (Deutsch).",
}


async def generate_report(
    content: str,
    actions: list[Action],
    graph_context: str = "",
    language: str = "en",
) -> dict:
    """Generate a marketing report using ReACT pattern."""

    if not actions:
        return {"viral_score": 0, "summary": "No simulation data", "sections": [], "recommendations": []}

    lang_instruction = LANGUAGE_INSTRUCTION_MAP.get(language, "")

    stats = _compute_stats(actions)

    # === PHASE 1: Plan ===
    plan_prompt = PLAN_PROMPT.format(
        content=content[:500],
        total_agents=stats["total_agents"],
        total_rounds=stats["total_rounds"],
        total_actions=stats["total_actions"],
        sentiment_summary=json.dumps(stats["sentiments"]),
        engagement_summary=json.dumps(stats["engagements"]),
        avg_score=stats["avg_score"],
    )

    plan_text = await _llm_call(plan_prompt + lang_instruction, 1024)
    try:
        sections_plan = extract_json(plan_text)
        if isinstance(sections_plan, dict):
            sections_plan = [sections_plan]
    except Exception:
        sections_plan = [
            {"title": "Audience Reception", "question": "How did the audience react overall?", "tools": ["sentiment_aggregate"]},
            {"title": "Viral Potential", "question": "How likely is this content to spread?", "tools": ["action_search", "identify_influencers"]},
            {"title": "Segment Analysis", "question": "How did different demographics react?", "tools": ["sentiment_aggregate"]},
            {"title": "Key Insights", "question": "What unexpected patterns emerged?", "tools": ["action_search"]},
            {"title": "Recommendations", "question": "What should the marketing team do next?", "tools": ["graph_search"]},
        ]

    # === PHASE 2: Search → Write → Reflect per section ===
    completed_sections = []
    sample_reactions = "\n".join(
        f"@{a.agent_name}: {a.content[:120]}" for a in actions if a.content and len(a.content) > 10
    )[:1500]

    for sec in sections_plan[:7]:  # Cap at 7 sections
        title = sec.get("title", "Analysis")
        question = sec.get("question", "")
        tools = sec.get("tools", [])

        # --- Search phase: run tools ---
        tool_results: list[ToolResult] = []

        for tool_name in tools:
            if tool_name == "graph_search":
                result = graph_search(graph_context, question)
                tool_results.append(result)
            elif tool_name == "action_search":
                result = action_search(actions, {"has_content": True})
                tool_results.append(result)
            elif tool_name == "sentiment_aggregate":
                # Overall
                result = sentiment_aggregate(actions)
                tool_results.append(result)
                # Young segment
                result2 = sentiment_aggregate(actions, {"age_min": 15, "age_max": 25})
                tool_results.append(result2)
                # Older segment
                result3 = sentiment_aggregate(actions, {"age_min": 26, "age_max": 45})
                tool_results.append(result3)
            elif tool_name == "identify_influencers":
                result = identify_influencers(actions, top_n=5)
                tool_results.append(result)

        tool_text = "\n\n".join(f"[{tr.tool}] {tr.result}" for tr in tool_results)

        # --- Search synthesis ---
        search_result = await _llm_call(SEARCH_PROMPT.format(
            title=title, question=question, tool_results=tool_text,
        ) + lang_instruction, 512)

        # --- Write phase ---
        section_content = await _llm_call(WRITE_PROMPT.format(
            title=title, question=question, findings=search_result,
            graph_context=graph_context[:500], sample_reactions=sample_reactions[:500],
        ) + lang_instruction, 1024)

        # --- Reflect phase ---
        try:
            reflect_text = await _llm_call(REFLECT_PROMPT.format(
                title=title, content=section_content,
            ), 512)
            reflect_data = extract_json(reflect_text)
            score = reflect_data.get("score", 7)
            if score < 7 and reflect_data.get("revised"):
                section_content = reflect_data["revised"]
        except Exception:
            pass  # Reflection failed, keep original

        completed_sections.append({"title": title, "content": section_content})

    # === PHASE 3: Final synthesis ===
    influencer_result = identify_influencers(actions, top_n=5)
    sections_text = "\n\n".join(f"## {s['title']}\n{s['content'][:300]}" for s in completed_sections)

    # Compute calibration stats for scoring
    positive_count = stats["sentiments"].get("positive", 0)
    negative_count = stats["sentiments"].get("negative", 0)
    total_sentiment = sum(stats["sentiments"].values()) or 1
    ignore_count = stats["engagements"].get("ignore", 0)
    total_engage = sum(stats["engagements"].values()) or 1

    synthesis_text = await _llm_call(SYNTHESIS_PROMPT.format(
        content=content[:500],
        avg_score=stats["avg_score"],
        positive_ratio=positive_count / total_sentiment,
        negative_ratio=negative_count / total_sentiment,
        engagement_rate=(total_engage - ignore_count) / total_engage,
        sections_text=sections_text,
        influencer_data=influencer_result.result,
    ) + lang_instruction, 1024)

    try:
        synthesis = extract_json(synthesis_text)
    except Exception:
        synthesis = {"viral_score": 50, "summary": "Report completed", "recommendations": []}

    return {
        "viral_score": synthesis.get("viral_score", 50),
        "summary": synthesis.get("summary", ""),
        "sections": completed_sections,
        "recommendations": synthesis.get("recommendations", []),
    }


async def interview_agent(
    agent_name: str,
    question: str,
    actions: list[Action],
    content: str,
) -> str:
    """Interview a specific agent about their behavior, using their memory."""
    agent_actions = [a for a in actions if a.agent_name == agent_name]
    if not agent_actions:
        return f"Agent '{agent_name}' not found in simulation."

    profile = agent_actions[0].agent_profile

    # Build memory context from their actions
    memory_lines = []
    for a in agent_actions:
        if a.action_type == "post":
            memory_lines.append(f"Round {a.round_num}: I posted: \"{a.content[:100]}\"")
        elif a.action_type == "reply":
            memory_lines.append(f"Round {a.round_num}: I replied to @{a.target_agent}: \"{a.content[:100]}\"")
        elif a.action_type == "share":
            memory_lines.append(f"Round {a.round_num}: I shared @{a.target_agent}'s post")
        elif a.action_type in ("like", "dislike"):
            memory_lines.append(f"Round {a.round_num}: I {a.action_type}d @{a.target_agent}'s post")

    # Build relationship context
    interactions = {}
    for a in agent_actions:
        if a.target_agent:
            interactions[a.target_agent] = interactions.get(a.target_agent, 0) + 1
    relationship_text = ", ".join(f"@{k} ({v} interactions)" for k, v in sorted(interactions.items(), key=lambda x: -x[1])[:5])

    # Sentiment journey
    sentiment_journey = " → ".join(
        f"R{a.round_num}:{a.sentiment}({a.sentiment_score})" for a in agent_actions if a.sentiment
    )

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = await client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are {agent_name}. Your profile: {json.dumps(profile)}\n\n"
                    f"During a social media simulation about: {content[:200]}\n\n"
                    f"YOUR MEMORY (what you did):\n" + "\n".join(memory_lines) + "\n\n"
                    f"YOUR RELATIONSHIPS: {relationship_text}\n"
                    f"YOUR SENTIMENT JOURNEY: {sentiment_journey}\n\n"
                    f"Answer the question IN CHARACTER, referencing your actual actions and feelings."
                ),
            },
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content
